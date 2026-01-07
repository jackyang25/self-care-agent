"""whatsapp webhook integration."""

import hashlib
import hmac
import logging
import os
import re
from typing import Any, Dict, Optional

import requests
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from src.channels.base import BaseChannelHandler

logger = logging.getLogger(__name__)

app = FastAPI(title="WhatsApp Webhook")


class WhatsAppHandler(BaseChannelHandler):
    """whatsapp handler - session_id passed explicitly in respond()."""
    pass


handler = WhatsAppHandler()


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
    if not signature or not signature.startswith("sha256="):
        return False

    expected_signature = signature[7:]  # remove "sha256=" prefix
    calculated = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, calculated)


@app.get("/webhook")
async def verify_webhook(request: Request):
    """verify webhook endpoint for whatsapp."""
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning(f"verification failed: mode={hub_mode}")
    raise HTTPException(status_code=403, detail="verification failed")


@app.post("/webhook")
async def handle_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
):
    """handle incoming whatsapp messages."""
    body = await request.body()

    # verify signature if configured
    webhook_secret = os.getenv("WHATSAPP_WEBHOOK_SECRET")
    if webhook_secret:
        if not verify_webhook_signature(body, x_hub_signature_256, webhook_secret):
            logger.warning("invalid webhook signature")
            raise HTTPException(status_code=403, detail="invalid signature")

    # parse webhook payload
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"parse error: {e}")
        raise HTTPException(status_code=400, detail="invalid payload")

    # extract messages from webhook structure
    entry = data.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])

    if not messages:
        return JSONResponse(content={"status": "ok"})

    # process each message
    for message in messages:
        try:
            from_number = message.get("from")
            message_type = message.get("type")

            if message_type != "text":
                continue

            text_body = message.get("text", {}).get("body", "")
            if not text_body:
                continue

            # process message through agent
            response, sources, _ = handler.respond(
                user_message=text_body,
                whatsapp_id=from_number
            )

            # append sources if available
            if sources:
                sources_text = "\n\nSources:\n"
                for i, source in enumerate(sources, 1):
                    similarity = int(source.get("similarity", 0) * 100)
                    title = source.get("title", "Unknown")
                    content_type = source.get("content_type", "")
                    type_label = f" ({content_type})" if content_type else ""
                    sources_text += f"{i}. {title}{type_label} - {similarity}% match\n"
                response += sources_text

            # send response
            send_whatsapp_message(from_number, response)
            logger.info("message sent successfully")

        except Exception as e:
            logger.error(f"processing error: {e}")
            continue

    return JSONResponse(content={"status": "ok"})


def format_whatsapp_text(message: str) -> str:
    """convert markdown to whatsapp-friendly text."""
    if not message:
        return ""

    text = message
    # convert markdown formatting to whatsapp formatting
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)  # bold
    text = re.sub(r"__(.+?)__", r"_\1_", text)  # italic
    text = re.sub(r"`([^`]+)`", r"`\1`", text)  # monospace
    text = re.sub(r"\[(.+?)\]\((https?[^)]+)\)", r"\1 - \2", text)  # links
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)  # headings
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse blank lines
    return text.strip()


def send_whatsapp_message(phone_number: str, message: str) -> Dict[str, Any]:
    """send message via whatsapp api.
    
    args:
        phone_number: recipient phone number
        message: message text to send
    
    returns:
        api response dict
    """
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    if not access_token or not phone_number_id:
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

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
