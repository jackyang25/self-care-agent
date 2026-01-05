"""webhook server entry point for channel integrations."""

import os
from dotenv import load_dotenv
import uvicorn
from src.presentation.messaging.whatsapp.handler import app

load_dotenv()


def main():
    """run webhook server."""
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()

