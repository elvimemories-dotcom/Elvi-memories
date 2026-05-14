"""
Cliente para enviar mensajes a través de la API de Meta
(WhatsApp Business, Instagram DM via Instagram Login API, Messenger)
"""
import httpx
from config.settings import (
    META_WHATSAPP_TOKEN,
    META_PAGE_ACCESS_TOKEN,
    META_INSTAGRAM_TOKEN,
    WHATSAPP_API_URL,
    INSTAGRAM_API_URL,
    MESSENGER_API_URL,
)


def _es_token_eaa(token: str | None) -> bool:
    """Heurística: tokens de Página de Facebook empiezan con 'EAA'."""
    return bool(token) and token.startswith("EAA")

async def enviar_whatsapp(numero: str, mensaje: str) -> dict:
    """Envía mensaje de texto por WhatsApp Business API."""
    headers = {
        "Authorization": f"Bearer {META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {"preview_url": False, "body": mensaje},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, headers=headers, json=payload)
        return response.json()

async def enviar_instagram_dm(recipient_id: str, mensaje: str) -> dict:
    """
    Envía DM por Instagram usando Instagram Login API (tokens IGAA).
    Endpoint: graph.instagram.com/v23.0/{ig-user-id}/messages
    """
    if not META_INSTAGRAM_TOKEN:
        return {"error": "META_INSTAGRAM_TOKEN no configurado"}

    headers = {
        "Authorization": f"Bearer {META_INSTAGRAM_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": mensaje},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(INSTAGRAM_API_URL, headers=headers, json=payload)
        return response.json()


async def enviar_messenger(recipient_id: str, mensaje: str) -> dict:
    """
    Envía mensaje por Facebook Messenger.
    Requiere Page Access Token (EAA), NO Instagram token (IGAA).
    """
    if not _es_token_eaa(META_PAGE_ACCESS_TOKEN):
        print(
            "[META-WARN] META_PAGE_ACCESS_TOKEN no parece ser un Page Token (EAA...). "
            "Messenger no funcionará hasta que configures un token de Página de Facebook. "
            "Si solo usas Instagram + WhatsApp, ignora este aviso."
        )
        return {"error": "Page Access Token (EAA) no configurado"}

    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": mensaje},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            MESSENGER_API_URL,
            headers=headers,
            json=payload,
            params={"access_token": META_PAGE_ACCESS_TOKEN},
        )
        return response.json()

async def enviar_imagen_whatsapp(numero: str, url_imagen: str, caption: str = "") -> dict:
    """Envía una imagen por WhatsApp usando una URL pública."""
    headers = {
        "Authorization": f"Bearer {META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "image",
        "image": {"link": url_imagen, "caption": caption},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, headers=headers, json=payload)
        return response.json()

async def enviar_documento_whatsapp(numero: str, url_pdf: str, nombre_archivo: str, caption: str = "") -> dict:
    """Envía un documento PDF por WhatsApp usando una URL pública."""
    headers = {
        "Authorization": f"Bearer {META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "document",
        "document": {
            "link": url_pdf,
            "filename": nombre_archivo,
            "caption": caption,
        },
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, headers=headers, json=payload)
        return response.json()

async def enviar_mensaje(canal: str, recipient_id: str, mensaje: str) -> dict:
    """Router principal para enviar mensajes por el canal correcto."""
    if canal == "whatsapp":
        return await enviar_whatsapp(recipient_id, mensaje)
    elif canal == "instagram":
        return await enviar_instagram_dm(recipient_id, mensaje)
    elif canal == "messenger":
        return await enviar_messenger(recipient_id, mensaje)
    else:
        raise ValueError(f"Canal no soportado: {canal}")


async def obtener_nombre_instagram(sender_id: str) -> str | None:
    """Obtiene el nombre del usuario de Instagram via Graph API."""
    if not META_INSTAGRAM_TOKEN:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://graph.instagram.com/v23.0/{sender_id}",
                params={"fields": "name", "access_token": META_INSTAGRAM_TOKEN},
            )
            data = response.json()
            return data.get("name") or None
    except Exception:
        return None


async def obtener_nombre_messenger(sender_id: str) -> str | None:
    """Obtiene el nombre del usuario de Messenger via Graph API."""
    if not META_PAGE_ACCESS_TOKEN:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://graph.facebook.com/v20.0/{sender_id}",
                params={"fields": "first_name,last_name", "access_token": META_PAGE_ACCESS_TOKEN},
            )
            data = response.json()
            nombre = (data.get("first_name", "") + " " + data.get("last_name", "")).strip()
            return nombre or None
    except Exception:
        return None
