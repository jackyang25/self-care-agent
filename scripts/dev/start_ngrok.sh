#!/bin/bash
# start ngrok tunnel for webhook server

PORT=${1:-8000}

echo "starting ngrok tunnel on port $PORT..."
echo "webhook server should be running on port $PORT"
echo ""
echo "check ngrok output above for the public url"
echo "or visit http://localhost:4040 to see the ngrok dashboard"
echo ""
echo "use the ngrok url + /webhook in your whatsapp webhook configuration"
echo "example: https://abc123.ngrok.io/webhook"
echo ""

ngrok http $PORT

