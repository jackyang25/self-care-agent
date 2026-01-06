"""whatsapp webhook integration."""

import hashlib
import hmac
import os
import re
from typing import Any, Dict, Optional

import requests
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from src.presentation.base import BaseChannelHandler
# context vars no longer needed - set in execution_node during agent execution
import logging

from src.infrastructure.postgres.repositories.users import get_user_by_phone

logger = logging.getLogger(__name__)

app = FastAPI(title="WhatsApp Webhook")


class WhatsAppHandler(BaseChannelHandler):
    """whatsapp message handler."""

    # conversation history managed automatically by redis
    # no need to override get_conversation_history()

    def get_user_id(self) -> Optional[str]:
        """get current user id.
        
        whatsapp handler always passes user_id explicitly to respond(),
        so this method is not used.
        """
        return None


# module-level handler singleton (initialized on first use)
_handler = None


def _get_handler() -> WhatsAppHandler:
    """get or create whatsapp handler instance (singleton).

    returns:
        whatsapp handler instance
    """
    global _handler
    if _handler is None:
        _handler = WhatsAppHandler()
        logger.info("whatsapp handler initialized")
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
    
    logger.info(f"webhook verification | client={client_host} | mode={hub_mode}")

    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("webhook verified")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning(f"verification failed: mode={hub_mode}, token_match={hub_verify_token == verify_token}")
    logger.info("webhook verification failed")
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
    
    logger.info(f"webhook message received | client={client_host}")

    # get raw body for signature verification
    body = await request.body()

    # verify signature if configured
    webhook_secret = os.getenv("WHATSAPP_WEBHOOK_SECRET")
    if webhook_secret:
        if not verify_webhook_signature(body, x_hub_signature_256, webhook_secret):
            logger.warning("invalid webhook signature")
            logger.error("webhook invalid signature")
            raise HTTPException(status_code=403, detail="invalid signature")

    # parse webhook payload
    try:
        data = await request.json()
        payload_preview = str(data)[:150] + "..." if len(str(data)) > 150 else str(data)
        logger.info(f"payload: {payload_preview}")
    except Exception as e:
        logger.error(f"parse error: {e}")
        logger.error("webhook parse error")
        raise HTTPException(status_code=400, detail="invalid payload")

    # whatsapp webhook structure
    # adjust based on your whatsapp provider (meta business api, twilio, etc.)
    entry = data.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])

    if not messages:
        # not a message event (could be status update, etc.)
        logger.info("webhook no messages")
        return JSONResponse(content={"status": "ok"})

    # process each message
    for message in messages:
        try:
            # extract message data
            from_number = message.get("from")
            message_type = message.get("type")

            if message_type != "text":
                logger.info(f"skipping non-text: {message_type}")
                continue

            text_body = message.get("text", {}).get("body", "")

            if not text_body:
                continue

            msg_preview = text_body[:80] + "..." if len(text_body) > 80 else text_body
            logger.info(f"from: {from_number} | message: {msg_preview}")

            # lookup user by phone number
            # whatsapp sends phone numbers in E.164 format (e.g., "1234567890" or "+1234567890")
            # normalize: ensure it starts with + if it doesn't
            normalized_phone = from_number
            if not normalized_phone.startswith("+"):
                # if it's just digits, assume it needs country code
                # for now, try as-is first, then with +
                normalized_phone = f"+{normalized_phone}"

            try:
                user = get_user_by_phone(normalized_phone)
                # if not found with +, try without +
                if not user and normalized_phone.startswith("+"):
                    user = get_user_by_phone(from_number)
            except Exception as e:
                logger.error(f"user lookup error: {e}")
                user = None

            user_id = str(user.get("user_id")) if user else None

            if not user_id:
                logger.warning(f"user not found: {from_number}")
                # send error message to user
                error_response = "sorry, your phone number is not registered. please contact support to register your account."
                try:
                    send_whatsapp_message(from_number, error_response)
                except Exception as e:
                    logger.error(f"send error: {e}")
                continue  # skip processing this message

            logger.info(f"user_id: {user_id[:8]}... | processing message")

            # get user demographics
            demographics = user.get("demographics", {}) if user else {}
            age = demographics.get("age")
            gender = demographics.get("gender")
            timezone = user.get("timezone", "UTC") if user else "UTC"

            # process message through handler (context vars set in execution_node)
            handler = _get_handler()
            response, sources = handler.respond(
                text_body,
                user_id=user_id,
                user_age=age,
                user_gender=gender,
                user_timezone=timezone,
            )

            # format sources as plain text for whatsapp (no markdown support)
            if sources:
                sources_text = "\n\nSources:\n"
                for i, source in enumerate(sources, 1):
                    similarity_pct = int(source.get("similarity", 0) * 100)
                    content_type = source.get("content_type", "")
                    content_type_label = f" ({content_type})" if content_type else ""
                    sources_text += f"{i}. {source.get('title', 'Unknown')}{content_type_label} - {similarity_pct}% match\n"
                response = response + sources_text

            resp_preview = response[:80] + "..." if len(response) > 80 else response
            logger.info(f"sending response: {resp_preview}")

            # send response via whatsapp api
            try:
                send_whatsapp_message(from_number, response)
                logger.info("message sent successfully")
            except Exception as e:
                logger.error(f"send error: {e}")

        except Exception as e:
            logger.error(f"processing error: {e}")
            continue

    logger.info("webhook processed successfully")
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
    text = re.sub(r"^\s*(\d+)\.\s+", r"\1. ", text, flags=re.MULTILINE)  # ordered lists
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
        logger.error("whatsapp credentials not configured")
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
            logger.error(f"whatsapp api error: {e} - {error_detail}")
        except Exception:
            logger.error(f"whatsapp api error: {e} - {response.text}")
        raise
    except Exception as e:
        logger.error(f"whatsapp api error: {e}")
        raise
