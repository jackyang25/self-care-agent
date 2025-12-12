"""whatsapp webhook integration."""

import os
import re
import hmac
import hashlib
import requests
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.responses import JSONResponse
from src.agent import create_agent
from src.channels.base import BaseChannelHandler
from src.config import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE
from src.utils.logger import get_logger
from src.utils.user_lookup import get_user_by_phone
from src.utils.context import current_user_id

logger = get_logger("whatsapp")

app = FastAPI(title="WhatsApp Webhook")

# module-level agent singleton (shared across all requests)
_agent_instance = None


def _get_agent():
    """get or create agent instance (singleton).

    returns:
        compiled agent workflow instance
    """
    global _agent_instance
    if _agent_instance is None:
        llm_model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
        temperature = float(os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)))
        _agent_instance = create_agent(llm_model=llm_model, temperature=temperature)
        logger.info(
            f"created agent singleton: model={llm_model}, temperature={temperature}"
        )
    return _agent_instance


class WhatsAppHandler(BaseChannelHandler):
    """whatsapp message handler."""

    def __init__(self, llm_model: str, temperature: float):
        """initialize handler with agent configuration."""
        super().__init__(llm_model, temperature)

    @property
    def agent(self):
        """get agent from module-level singleton."""
        return _get_agent()

    def get_conversation_history(
        self, user_id: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """get conversation history for user.

        note: would need to implement storage/retrieval from database
        """
        # todo: implement conversation history storage/retrieval
        return []

    def get_user_id(self) -> Optional[str]:
        """get current user id from context variable.

        note: user_id is set in webhook handler via context variable for thread-safe access
        """
        return current_user_id.get()


# module-level handler singleton (initialized on first use)
_handler = None


def _get_handler() -> WhatsAppHandler:
    """get or create whatsapp handler instance (singleton).

    returns:
        whatsapp handler instance
    """
    global _handler
    if _handler is None:
        llm_model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
        temperature = float(os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)))
        _handler = WhatsAppHandler(llm_model=llm_model, temperature=temperature)
        logger.info(
            f"created whatsapp handler singleton: model={llm_model}, temperature={temperature}"
        )
    return _handler


def verify_webhook_signature(
    payload: bytes, signature: Optional[str], secret: str
) -> bool:
    """verify webhook signature from whatsapp.

    args:
        payload: raw request body
        signature: x-hub-signature-256 header value
        secret: webhook verification token

    returns:
        true if signature is valid
    """
    if not signature:
        return False

    # whatsapp sends signature as "sha256=<hash>"
    if not signature.startswith("sha256="):
        return False

    expected_signature = signature[7:]  # remove "sha256=" prefix
    calculated = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected_signature, calculated)


@app.get("/webhook")
async def verify_webhook(request: Request):
    """verify webhook endpoint for whatsapp.

    whatsapp sends a get request with verification token.
    note: whatsapp uses hub.mode, hub.verify_token, hub.challenge (with dots)
    """
    # whatsapp sends query params with dots: hub.mode, hub.verify_token, hub.challenge
    query_params = request.query_params
    hub_mode = query_params.get("hub.mode")
    hub_verify_token = query_params.get("hub.verify_token")
    hub_challenge = query_params.get("hub.challenge")

    client_host = request.client.host if request.client else "unknown"
    logger.info(
        f"webhook verification request from {client_host} - mode: {hub_mode}, token provided: {bool(hub_verify_token)}"
    )

    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

    # debug logging
    if verify_token:
        logger.info(
            f"verify token from env: {verify_token[:10]}... (length: {len(verify_token)})"
        )
    else:
        logger.warning("WHATSAPP_VERIFY_TOKEN not found in environment")

    if hub_verify_token:
        logger.info(
            f"verify token from request: {hub_verify_token[:10]}... (length: {len(hub_verify_token)})"
        )

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("webhook verified successfully - challenge returned")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning(
        f"webhook verification failed - mode: {hub_mode}, token match: {hub_verify_token == verify_token}"
    )
    raise HTTPException(status_code=403, detail="verification failed")


@app.post("/webhook")
async def handle_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
):
    """handle incoming whatsapp messages.

    processes incoming messages and sends responses via agent.
    """
    # log incoming request
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"incoming webhook request from {client_host}")

    # get raw body for signature verification
    body = await request.body()

    # verify signature if configured
    webhook_secret = os.getenv("WHATSAPP_WEBHOOK_SECRET")
    if webhook_secret:
        if not verify_webhook_signature(body, x_hub_signature_256, webhook_secret):
            logger.warning("invalid webhook signature")
            raise HTTPException(status_code=403, detail="invalid signature")
        else:
            logger.info("webhook signature verified successfully")

    # parse webhook payload
    try:
        data = await request.json()
        logger.info(f"received webhook payload: {str(data)[:200]}...")
    except Exception as e:
        logger.error(f"failed to parse webhook payload: {e}")
        raise HTTPException(status_code=400, detail="invalid payload")

    # whatsapp webhook structure
    # adjust based on your whatsapp provider (meta business api, twilio, etc.)
    entry = data.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])

    if not messages:
        # not a message event (could be status update, etc.)
        return JSONResponse(content={"status": "ok"})

    # process each message
    for message in messages:
        try:
            # extract message data
            from_number = message.get("from")
            message_type = message.get("type")

            if message_type != "text":
                logger.info(f"ignoring non-text message type: {message_type}")
                continue

            text_body = message.get("text", {}).get("body", "")

            if not text_body:
                continue

            logger.info(f"received message from {from_number}: {text_body[:100]}")

            # lookup user by phone number
            # whatsapp sends phone numbers in E.164 format (e.g., "1234567890" or "+1234567890")
            # normalize: ensure it starts with + if it doesn't
            normalized_phone = from_number
            if not normalized_phone.startswith("+"):
                # if it's just digits, assume it needs country code
                # for now, try as-is first, then with +
                normalized_phone = f"+{normalized_phone}"

            user = get_user_by_phone(normalized_phone)
            # if not found with +, try without +
            if not user and normalized_phone.startswith("+"):
                user = get_user_by_phone(from_number)

            user_id = str(user.get("user_id")) if user else None

            if not user_id:
                logger.warning(
                    f"user not found for phone: {from_number} (tried: {normalized_phone})"
                )
                # send error message to user
                error_response = "sorry, your phone number is not registered. please contact support to register your account."
                try:
                    send_whatsapp_message(from_number, error_response)
                except Exception as e:
                    logger.error(f"failed to send error message: {e}")
                continue  # skip processing this message

            # set user_id in context variable for thread-safe access
            current_user_id.set(user_id)

            # process message through handler
            handler = _get_handler()
            # user_id is now available via get_user_id() or can be passed explicitly
            response, sources = handler.respond(text_body, user_id=user_id)

            # format sources as plain text for whatsapp (no markdown support)
            if sources:
                sources_text = "\n\nSources:\n"
                for i, source in enumerate(sources, 1):
                    similarity_pct = int(source.get("similarity", 0) * 100)
                    content_type = source.get("content_type", "")
                    content_type_label = f" ({content_type})" if content_type else ""
                    sources_text += f"{i}. {source.get('title', 'Unknown')}{content_type_label} - {similarity_pct}% match\n"
                response = response + sources_text

            logger.info(f"sending response to {from_number}: {response[:100]}")

            # send response via whatsapp api
            try:
                send_whatsapp_message(from_number, response)
            except Exception as e:
                logger.error(f"failed to send whatsapp message: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"error processing message: {e}", exc_info=True)
            continue

    return JSONResponse(content={"status": "ok"})


def format_whatsapp_text(message: str) -> str:
    """convert markdown-ish output to whatsapp-friendly text."""
    if not message:
        return ""

    text = message
    text = re.sub(
        r"```[\w-]*\n(.*?)\n```", r"```\1```", text, flags=re.DOTALL
    )  # code fences
    text = re.sub(r"`([^`]+)`", r"`\1`", text)  # inline code to monospace
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)  # bold
    text = re.sub(r"__(.+?)__", r"_\1_", text)  # italics
    text = re.sub(r"\[(.+?)\]\((https?[^)]+)\)", r"\1 - \2", text)  # links
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)  # headings to plain
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)  # strip blockquotes
    text = re.sub(r"^\s*[\*\-]\s+", "- ", text, flags=re.MULTILINE)  # bullets
    text = re.sub(
        r"^\s*\d+\.\s+", lambda m: m.group(0).strip(), text, flags=re.MULTILINE
    )  # ordered lists
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse blank lines
    return text.strip()


def send_whatsapp_message(phone_number: str, message: str) -> Dict[str, Any]:
    """send message via whatsapp api.

    args:
        phone_number: recipient phone number in E.164 format
        message: message text to send

    returns:
        api response dict

    note: requires WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID env vars
    """
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    if not access_token or not phone_number_id:
        logger.error("whatsapp access token or phone number id not configured")
        raise ValueError("whatsapp credentials not configured")

    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": format_whatsapp_text(message)},
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = response.json()
            logger.error(f"failed to send whatsapp message: {e} - {error_detail}")
        except Exception:
            logger.error(f"failed to send whatsapp message: {e} - {response.text}")
        raise
    except Exception as e:
        logger.error(f"failed to send whatsapp message: {e}")
        raise
