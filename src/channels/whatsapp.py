"""whatsapp webhook integration."""

import os
import hmac
import hashlib
import requests
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.responses import JSONResponse
from src.channels.base import BaseChannelHandler
from src.config import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE
from src.utils.logger import get_logger
from src.utils.user_lookup import get_user_by_phone

logger = get_logger("whatsapp")

app = FastAPI(title="WhatsApp Webhook")


class WhatsAppHandler(BaseChannelHandler):
    """whatsapp message handler."""

    def get_conversation_history(self, user_id: Optional[str] = None) -> List[Dict[str, str]]:
        """get conversation history for user.
        
        note: would need to implement storage/retrieval from database
        """
        # todo: implement conversation history storage/retrieval
        return []

    def get_user_id(self) -> Optional[str]:
        """get current user id.
        
        note: whatsapp handler receives user_id as parameter, not from state
        """
        # whatsapp handler gets user_id from webhook payload, not from state
        return None


# global handler instance (initialized on first use)
_handler = None


def _get_handler() -> WhatsAppHandler:
    """get or create whatsapp handler instance."""
    global _handler
    if _handler is None:
        llm_model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
        temperature = float(os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)))
        _handler = WhatsAppHandler(llm_model=llm_model, temperature=temperature)
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
            user = get_user_by_phone(from_number)
            user_id = user.get("user_id") if user else None

            if not user_id:
                logger.warning(f"user not found for phone: {from_number}")

            # process message through handler
            handler = _get_handler()
            response = handler.respond(text_body, user_id=user_id)

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
        "text": {"body": message},
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
