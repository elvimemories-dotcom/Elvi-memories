import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Meta
META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "elvi_webhook_token_2024")
META_WHATSAPP_TOKEN = os.getenv("META_WHATSAPP_TOKEN")
META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")
META_WHATSAPP_BUSINESS_ID = os.getenv("META_WHATSAPP_BUSINESS_ID")
META_INSTAGRAM_TOKEN = os.getenv("META_INSTAGRAM_TOKEN")
META_INSTAGRAM_ACCOUNT_ID = os.getenv("META_INSTAGRAM_ACCOUNT_ID")

# Servidor
PORT = int(os.getenv("PORT", 8000))
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")

# Negocio
WHATSAPP_NEGOCIO = os.getenv("WHATSAPP_NEGOCIO", "+16787659231")
ZELLE_INFO = os.getenv("ZELLE_INFO", "elvimemories@gmail.com")

# Email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

# Google AI (Gemini)
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

# URLs de Meta Graph API
# WhatsApp Cloud API
WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{META_PHONE_NUMBER_ID}/messages"

# Instagram Login API (cuenta business directa, tokens IGAA)
# Usa graph.instagram.com con el ID de la cuenta de Instagram
INSTAGRAM_API_URL = f"https://graph.instagram.com/v23.0/{META_INSTAGRAM_ACCOUNT_ID}/messages"

# Messenger (Facebook Page → necesita Page Access Token EAA, no IGAA)
MESSENGER_API_URL = "https://graph.facebook.com/v20.0/me/messages"
