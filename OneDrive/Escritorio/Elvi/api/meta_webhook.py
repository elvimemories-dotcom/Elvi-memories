"""
Handler del Webhook de Meta
Procesa los eventos entrantes de WhatsApp, Instagram y Messenger
"""
from fastapi import HTTPException
from config.settings import META_VERIFY_TOKEN


def verificar_firma(body_bytes: bytes, signature_header: str) -> bool:
    """Verifica la firma HMAC-SHA256 de Meta. Pendiente de activar con APP_SECRET correcto."""
    return True


def extraer_mensaje_whatsapp(body: dict) -> tuple[str, str, str] | None:
    """Extrae (user_id, numero, mensaje) de un webhook de WhatsApp."""
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])
        if not messages:
            return None
        msg = messages[0]
        if msg.get("type") != "text":
            return None
        numero = msg["from"]
        texto = msg["text"]["body"]
        return numero, numero, texto
    except (KeyError, IndexError):
        return None


def extraer_mensaje_instagram(body: dict) -> tuple[str, str, str] | None:
    """
    Extrae (user_id, sender_id, mensaje) de un webhook de Instagram.
    Maneja dos formatos:
      - messaging[]: DMs reales en producción
      - changes[]:   test de "Probar" del panel Meta
    Ignora echos del bot y notificaciones de estado sin sender.
    """
    try:
        entry = body["entry"][0]

        # Formato real (producción): entry.messaging[]
        if "messaging" in entry:
            messaging = entry["messaging"][0]
            # Ignorar echo del propio bot
            if messaging.get("message", {}).get("is_echo"):
                return None
            # Ignorar notificaciones de estado (message_edit sin sender)
            sender_id = messaging.get("sender", {}).get("id")
            if not sender_id:
                return None
            texto = messaging.get("message", {}).get("text", "")
            if not texto:
                return None
            return sender_id, sender_id, texto

        # Formato test (panel Meta "Probar"): entry.changes[].value
        if "changes" in entry:
            value = entry["changes"][0]["value"]
            if value.get("message", {}).get("is_echo"):
                return None
            sender_id = value.get("sender", {}).get("id")
            if not sender_id:
                return None
            texto = value.get("message", {}).get("text", "")
            if not texto:
                return None
            return sender_id, sender_id, texto

        return None
    except (KeyError, IndexError):
        return None


def extraer_mensaje_messenger(body: dict) -> tuple[str, str, str] | None:
    """Extrae (user_id, sender_id, mensaje) de un webhook de Messenger."""
    try:
        entry = body["entry"][0]
        messaging = entry["messaging"][0]
        if messaging.get("message", {}).get("is_echo"):
            return None
        sender_id = messaging["sender"]["id"]
        texto = messaging.get("message", {}).get("text", "")
        if not texto:
            return None
        return sender_id, sender_id, texto
    except (KeyError, IndexError):
        return None


def verificar_webhook(mode: str, token: str, challenge: str) -> str:
    """Verifica el webhook de Meta durante la configuración inicial."""
    if mode == "subscribe" and token == META_VERIFY_TOKEN:
        return challenge
    raise HTTPException(status_code=403, detail="Token de verificación inválido")


def detectar_canal(body: dict) -> str:
    """Detecta si el webhook viene de WhatsApp, Instagram o Messenger."""
    obj = body.get("object", "")
    if obj == "instagram":
        return "instagram"
    if obj == "page":
        return "messenger"
    if "whatsapp" in obj:
        return "whatsapp"
    try:
        entry = body.get("entry", [{}])[0]
        if "changes" in entry:
            return "whatsapp"
        return "messenger"
    except (IndexError, KeyError):
        return "desconocido"
