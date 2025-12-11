# WhatsApp Webhook Setup

## Overview

The WhatsApp webhook integration allows the self-care agent to receive and respond to messages via WhatsApp.

## Quick Reference: Where to Get Each Credential

| Credential | Where to Get It | Example Value |
|------------|----------------|---------------|
| **WHATSAPP_VERIFY_TOKEN** | You create this yourself (any secure random string) | `my_secure_token_123` |
| **WHATSAPP_ACCESS_TOKEN** | Meta App Dashboard → WhatsApp → API Setup → Temporary access token | `EAABwzLix...` |
| **WHATSAPP_PHONE_NUMBER_ID** | Meta App Dashboard → WhatsApp → API Setup → Phone number ID | `123456789012345` |
| **WHATSAPP_WEBHOOK_SECRET** | Meta App Dashboard → Settings → Basic → App Secret | `abc123def456...` |
| **Callback URL** | Your public webhook URL (ngrok for dev, your domain for prod) | `https://abc123.ngrok.io/webhook` |

## Getting Credentials from Meta WhatsApp Business API

### Step 1: Create a Meta Developer Account

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Sign in with your Facebook account or create a new one
3. Create a new app or select an existing app

### Step 2: Set Up WhatsApp Business API

1. In your Meta App dashboard, go to **Add Product** → **WhatsApp**
2. Complete the WhatsApp Business API setup wizard
3. You'll need:
   - A Meta Business Account (create one if you don't have it)
   - A WhatsApp Business Account (created automatically)

### Step 3: Get Your Phone Number ID

1. In Meta App Dashboard → **WhatsApp** → **API Setup**
2. Find **"Phone number ID"** - this is your `WHATSAPP_PHONE_NUMBER_ID`
3. Copy this value (it looks like: `123456789012345`)

### Step 4: Get Your Access Token

**Option A: Temporary Token (for quick testing)**
1. In Meta App Dashboard → **WhatsApp** → **API Setup**
2. Find **"Temporary access token"** and copy it
3. Note: This expires after a few hours

**Option B: Permanent System User Token (recommended)**
1. Go to **Business Settings** → **Users** → **System Users**
2. Click **"Add"** or **"Create System User"**
3. Name it (e.g., "WhatsApp Bot") and click **"Create System User"**
4. Select the System User → Click **"Assign Assets"** or **"Add Assets"**
5. Select your App and assign permissions:
   - **WhatsApp Business Management**
   - **WhatsApp Business Messaging**
6. Click **"Save Changes"**
7. Still in System User page → Click **"Generate New Token"**
8. Select your App and permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
9. Click **"Generate Token"** and **copy it immediately** (you won't see it again)
10. This is your permanent `WHATSAPP_ACCESS_TOKEN` (doesn't expire)

### Step 5: Create Your Verification Token

**This is a custom string you create yourself** (not from Meta):

1. Choose a random, secure string (e.g., `my_secure_webhook_token_2024`)
2. This will be your `WHATSAPP_VERIFY_TOKEN`
3. You'll use this same token when configuring the webhook in Meta

### Step 6: Get Your Webhook Secret (Optional but Recommended)

1. In Meta App Dashboard → **WhatsApp** → **Configuration** → **Webhook**
2. Click **"Edit"** on your webhook
3. Find **"App Secret"** - this is your `WHATSAPP_WEBHOOK_SECRET`
4. Or go to **Settings** → **Basic** → **App Secret** → **Show**

## Local Development with ngrok

### 1. Install ngrok

Download and install ngrok from [ngrok.com](https://ngrok.com/download)

### 2. Set Environment Variables

Add to your `.env` file:

```bash
# required for webhook verification (one-time setup)
# create this yourself - any secure random string
WHATSAPP_VERIFY_TOKEN=your_verification_token_here

# required for sending messages back to users
# get from Meta App Dashboard → WhatsApp → API Setup
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here

# optional, for signature verification of incoming requests
# get from Meta App Dashboard → Settings → Basic → App Secret
WHATSAPP_WEBHOOK_SECRET=your_webhook_secret_here

# optional server configuration
WEBHOOK_PORT=8000  # defaults to 8000
```

**Important:** 
- **Verify Token**: Custom string you create (not the access token). Used only during initial webhook setup.
- **Access Token**: Your WhatsApp Business API access token (different from verify token). Used to send messages.
- **Phone Number ID**: Your WhatsApp Business phone number ID from Meta.

### 3. Start the Webhook Server

```bash
python webhook_server.py
```

The server will start on `http://localhost:8000`

### 4. Start ngrok

In a separate terminal:

```bash
ngrok http 8000
```

ngrok will provide a public URL like `https://abc123.ngrok.io`

### 5. Configure WhatsApp Webhook in Meta Dashboard

1. Go to Meta App Dashboard → **WhatsApp** → **Configuration** → **Webhook**
2. Click **"Edit"** or **"Add Callback URL"**
3. Enter your webhook URL:
   - **Callback URL**: `https://abc123.ngrok.io/webhook` (use your ngrok URL)
   - **Verify Token**: Enter the same value as `WHATSAPP_VERIFY_TOKEN` in your `.env`
4. Click **"Verify and Save"**

### 6. Verify Webhook

When you click "Verify and Save", Meta will:
1. Send a GET request to your webhook URL with the verification token
2. Your server (running `webhook_server.py`) will automatically respond correctly
3. If successful, the webhook will show as "Verified" in Meta dashboard

**Note**: Make sure your webhook server is running (`python webhook_server.py`) and ngrok is active before clicking "Verify and Save" in Meta dashboard.

## Production Deployment

For production, use a proper domain and SSL certificate instead of ngrok.

## Webhook Endpoints

### GET /webhook

Webhook verification endpoint. WhatsApp calls this to verify the webhook URL.

**Query Parameters:**
- `hub.mode`: Should be "subscribe"
- `hub.verify_token`: Must match `WHATSAPP_VERIFY_TOKEN`
- `hub.challenge`: Challenge string from WhatsApp

### POST /webhook

Receives incoming WhatsApp messages and processes them through the agent.

**Headers:**
- `X-Hub-Signature-256`: Webhook signature (optional, if `WHATSAPP_WEBHOOK_SECRET` is set)

## Implementation Notes

- The webhook payload structure may vary depending on your WhatsApp provider (Meta Business API, Twilio, etc.)
- Update the payload parsing in `src/channels/whatsapp.py` based on your provider's format
- Implement `send_whatsapp_message()` function to send responses back to users
- Conversation history storage/retrieval needs to be implemented for multi-turn conversations

## Testing

You can test the webhook locally using curl:

```bash
# Test verification
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=your_token&hub.challenge=test123"

# Test message (adjust payload structure for your provider)
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "+1234567890",
            "id": "msg123",
            "type": "text",
            "text": {"body": "I have a headache"}
          }]
        }
      }]
    }]
  }'
```

