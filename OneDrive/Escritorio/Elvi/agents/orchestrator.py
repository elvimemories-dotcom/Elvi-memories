"""
AGENTE WHATSAPP — Elvi Memories
Maneja el flujo completo de ventas por WhatsApp:
saludo → paquetes → referencias → agendamiento → depósito → contrato
"""
from database.db import guardar_mensaje
from agents.message_agent import detectar_intencion
from agents.sales_agent import responder_sobre_sesiones, manejar_objecion_precio
from agents.scheduler_agent import gestionar_agendamiento
from agents.contract_agent import preparar_contrato
from agents.style_agent import manejar_referencias
from agents.knowledge_agent import responder_pregunta_paquete
from agents.gemini_agent import obtener_referencias_gemini
from agents.shared_context import obtener_contextos_recientes, obtener_perfil_por_whatsapp
from config.settings import ZELLE_INFO

# Historial de conversaciones por usuario
conversaciones: dict[str, list] = {}

# Mapa de palabras clave → nombre del PDF en paquetes/
PAQUETES_PDF = {
    "CUMPLEAÑOS.pdf": [
        "cumpleaños", "cumpleano", "cumpleanos", "birthday", "fiesta", "celebracion", "celebración"
    ],
    "Copia de GESTACIÓN.pdf": [
        "maternidad", "embarazo", "embarazada", "bebe", "bebé", "gestante", "prenatal",
        "baby shower", "baby", "gestacion", "gestación"
    ],
    "Pareja.pdf": [
        "pareja", "novios", "novio", "novia", "amor", "compromiso", "engagement", "enamorados", "esposos"
    ],
    "BODAS.pdf": [
        "boda", "bodas", "matrimonio", "casamiento", "casarme", "casarnos"
    ],
    "KIDS.pdf": [
        "familia", "familiar", "familias", "hijos", "niños", "ninos", "padres", "kids", "niño", "niña"
    ],
    "XV años_pdf.pdf": [
        "xv", "quince", "quinceañera", "quinceañero", "15 años", "quince años"
    ],
}

# Paquetes que requieren atención de la dueña (agregar PDF cuando esté listo)
PAQUETES_NOTIFICAR_DUENA: dict = {}

# Palabras que indican que el cliente busca algo específico
_PALABRAS_ESPECIFICAS = [
    "sesion de", "sesión de", "fotos de", "paquete de", "quiero fotos",
    "necesito fotos", "busco fotos", "quiero una sesion", "quiero una sesión",
    "me gustaria", "me gustaría", "quisiera", "para mi", "para una"
]

_PALABRAS_SET_CREATIVO = ["set creativo", "sets creativos", "creativo", "creativos"]
_PALABRAS_CUMPLEANOS   = ["cumpleaños", "cumpleano", "cumpleanos", "birthday"]


def _detectar_pdf_por_paquete(mensaje: str, historial: list) -> tuple[str | None, str]:
    """
    Busca qué tipo de sesión mencionó el cliente.
    Retorna (pdf, motivo):
      - pdf=None          → cliente vago → preguntar qué necesita
      - pdf=archivo.pdf   → paquete conocido → enviar PDF
      - motivo="notificar_duena" → requiere atención personal
      - motivo="desconocido"     → pidió algo que no está en la lista
      - motivo="ok"              → paquete normal
    """
    texto = mensaje.lower()
    for turno in historial[-4:]:
        texto += " " + turno.get("content", "").lower()

    for archivo, palabras in PAQUETES_PDF.items():
        for palabra in palabras:
            if palabra in texto:
                return archivo, "ok"

    for archivo, palabras in PAQUETES_NOTIFICAR_DUENA.items():
        for palabra in palabras:
            if palabra in texto:
                return archivo, "notificar_duena"

    pide_algo_especifico = any(p in texto for p in _PALABRAS_ESPECIFICAS)
    if pide_algo_especifico:
        return None, "desconocido"

    return None, "preguntar"


_PALABRAS_DESCRIPCION_VISUAL = [
    "vestido", "color", "rojo", "azul", "verde", "blanco", "negro", "rosado", "rosa",
    "dorado", "plateado", "flores", "encaje", "tela", "outfit", "ropa", "look",
    "fondo", "decorado", "ambiente", "estilo", "elegante", "sexy", "romantico",
    "romántico", "casual", "natural", "boho", "oscuro", "claro", "pastel",
    "como esta foto", "algo asi", "algo así", "parecido a", "tipo", "con luces",
    "con globos", "con flores", "al aire", "en el parque", "en exteriores"
]

def _cliente_describe_algo_especifico(mensaje: str) -> bool:
    """Detecta si el cliente está describiendo visualmente lo que quiere."""
    texto = mensaje.lower()
    return any(p in texto for p in _PALABRAS_DESCRIPCION_VISUAL)


def _es_set_creativo_cumpleanos(mensaje: str, historial: list) -> bool:
    texto = mensaje.lower()
    for turno in historial[-4:]:
        texto += " " + turno.get("content", "").lower()
    tiene_set    = any(p in texto for p in _PALABRAS_SET_CREATIVO)
    tiene_cumple = any(p in texto for p in _PALABRAS_CUMPLEANOS)
    return tiene_set and tiene_cumple


def _contexto_canal_previo() -> str:
    """Si hay clientes recientes de Instagram/Messenger, agrega contexto al saludo."""
    recientes = obtener_contextos_recientes(minutos=60)
    if not recientes:
        return ""
    tipos = list({c["sesion"] for c in recientes if c.get("sesion")})
    if tipos:
        return f" (clientes recientes interesados en: {', '.join(tipos)})"
    return ""


def _saludo_personalizado(perfil: dict) -> tuple[str, str | None]:
    """Genera saludo y PDF para clienta que viene de IG/Messenger con perfil completo."""
    sesion  = perfil.get("sesion", "")
    estilo  = perfil.get("estilo", "")
    fecha   = perfil.get("fecha", "")
    detalles = perfil.get("detalles", "")
    pdf, motivo = _detectar_pdf_por_paquete(sesion, [])

    partes = []
    if sesion:
        partes.append(f"sesión de *{sesion}*")
    if estilo:
        partes.append(f"estilo _{estilo}_")
    if fecha:
        partes.append(f"para _{fecha}_")

    descripcion = ", ".join(partes) if partes else "tu sesión"
    if detalles:
        descripcion += f" — {detalles}"

    saludo = (
        f"¡Hola hermosa! 🤍 Qué alegría que nos escribas por WhatsApp.\n\n"
        f"Ya sé que buscas una {descripcion} ✨\n\n"
        f"Aquí te mando el paquete que más te conviene según lo que nos contaste 📸"
    )

    if motivo not in ("ok",) or not pdf:
        saludo = (
            f"¡Hola hermosa! 🤍 Qué alegría que nos escribas por WhatsApp.\n\n"
            f"Ya sé que buscas una {descripcion} ✨\n\n"
            f"Cuéntame un poco más para enviarte el paquete exacto que necesitas 🥰"
        )

    return saludo, pdf


def procesar_mensaje(
    user_id: str,
    mensaje: str,
    canal: str = "whatsapp",
) -> dict:
    """
    Punto de entrada principal para WhatsApp.
    Retorna {"respuesta": str, "pdf": str | None, "imagenes": list}
    """
    historial = conversaciones.get(user_id, [])

    # Primera vez que escribe — buscar si ya tiene perfil de IG/Messenger
    if not historial and canal == "whatsapp":
        perfil_previo = obtener_perfil_por_whatsapp(user_id)
        if perfil_previo:
            saludo, pdf = _saludo_personalizado(perfil_previo)
            guardar_mensaje(user_id, canal, "user", mensaje, "INFO_PAQUETES")
            guardar_mensaje(user_id, canal, "assistant", saludo)
            conversaciones[user_id] = [
                {"role": "user", "content": mensaje},
                {"role": "assistant", "content": saludo},
            ]
            print(f"[WA] {user_id} | perfil_previo:{perfil_previo.get('canal')} | {mensaje[:40]}")
            return {"respuesta": saludo, "pdf": pdf, "imagenes": []}

    resultado = detectar_intencion(mensaje, canal, historial)
    intencion = resultado["intencion"]

    try:
        print(f"[WA] {user_id} | {intencion} | {mensaje[:40]}".encode("utf-8", errors="replace").decode("utf-8"))
    except Exception:
        print(f"[WA] {user_id} | {intencion}")

    respuesta_final = resultado["respuesta"]
    pdf_a_enviar = None
    imagenes_a_enviar = []

    if intencion == "INFO_PAQUETES":
        pdf_a_enviar, motivo = _detectar_pdf_por_paquete(mensaje, historial)

        if motivo == "preguntar":
            # Cliente vago — preguntar qué necesita, sin PDF aún
            respuesta_final = responder_sobre_sesiones(mensaje, historial)
            pdf_a_enviar = None

        elif motivo == "notificar_duena":
            respuesta_final = responder_pregunta_paquete(mensaje, historial)
            _notificar_servicio_desconocido(user_id, "whatsapp", mensaje)

        elif motivo == "desconocido":
            respuesta_final = responder_sobre_sesiones(mensaje, historial)
            _notificar_servicio_desconocido(user_id, "whatsapp", mensaje)

        else:
            # Paquete conocido — responder con conocimiento completo del paquete y enviar PDF
            respuesta_final = responder_pregunta_paquete(mensaje, historial)

    elif intencion == "OBJECION_PRECIO":
        respuesta_final = manejar_objecion_precio(mensaje, historial)

    elif intencion == "ANALIZAR_IMAGEN":
        respuesta_final = (
            "¡Qué referencia tan bonita! 🤍 Me encanta tu estilo ✨ "
            "Dime qué tipo de sesión estás planeando y te muestro ejemplos similares de nuestro trabajo 📸"
        )

    elif intencion == "AGENDAR_SESION":
        resultado_agenda = gestionar_agendamiento(mensaje, historial)
        respuesta_final = resultado_agenda["respuesta"]

    elif intencion == "SOLICITAR_DEPOSITO":
        respuesta_final = (
            f"¡Qué emoción! 🤍 Para guardar tu fecha y hora elegida, "
            f"se requiere un depósito de reserva de *$50 USD*.\n\n"
            f"💳 *Zelle:* {ZELLE_INFO}\n\n"
            f"Una vez que envíes el comprobante aquí mismo, confirmo tu cita ✅ "
            f"y te envío el contrato por email para tu seguridad 📄✨\n\n"
            f"¿Ya tienes lista la fecha que deseas reservar? 🗓️"
        )
        _notificar_deposito_pendiente(user_id, "whatsapp", mensaje)

    elif intencion == "PEDIR_REFERENCIAS":
        if _es_set_creativo_cumpleanos(mensaje, historial):
            _notificar_set_creativo_cumpleanos(user_id, "whatsapp", mensaje)

        if _cliente_describe_algo_especifico(mensaje):
            # Cliente describe colores, ropa, ambiente → usar Gemini
            import asyncio
            from agents.style_agent import detectar_sesion_desde_historial
            tipo_sesion = detectar_sesion_desde_historial(mensaje, historial) or ""
            resultado_gemini = asyncio.run(obtener_referencias_gemini(mensaje, tipo_sesion))
            respuesta_final = resultado_gemini["respuesta"]
            imagenes_a_enviar = resultado_gemini["imagenes"]
        else:
            # Cliente pide referencias generales → flujo normal con carpetas
            resultado_refs = manejar_referencias(mensaje, historial)
            respuesta_final = resultado_refs["respuesta"]
            imagenes_a_enviar = resultado_refs["imagenes"]

    elif intencion == "ENVIAR_CONTRATO":
        resultado_contrato = preparar_contrato(mensaje, historial)
        respuesta_final = resultado_contrato["respuesta"]

    # Guardar en base de datos
    guardar_mensaje(user_id, canal, "user", mensaje, intencion)
    guardar_mensaje(user_id, canal, "assistant", respuesta_final)

    # Actualizar historial en memoria
    historial.append({"role": "user", "content": mensaje})
    historial.append({"role": "assistant", "content": respuesta_final})
    if len(historial) > 20:
        historial = historial[-20:]
    conversaciones[user_id] = historial

    return {"respuesta": respuesta_final, "pdf": pdf_a_enviar, "imagenes": imagenes_a_enviar}


# ====================================================================
# NOTIFICACIONES POR EMAIL
# ====================================================================

def _notificar_deposito_pendiente(user_id: str, canal: str, mensaje: str):
    import smtplib
    from email.mime.text import MIMEText
    from config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    if not SMTP_PASS:
        return
    try:
        msg = MIMEText(
            f"Un cliente está listo para hacer el depósito Zelle.\n\n"
            f"Canal: {canal.upper()}\nUsuario: {user_id}\nMensaje: {mensaje}\n\n"
            f"Revisa la conversación y confirma el pago cuando lo recibas.",
            "plain", "utf-8"
        )
        msg["Subject"] = "💳 Cliente listo para depositar — Elvi Memories"
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_USER
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"[NOTIF] Error email: {e}")


def _notificar_servicio_desconocido(user_id: str, canal: str, mensaje: str):
    import smtplib
    from email.mime.text import MIMEText
    from config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    if not SMTP_PASS:
        return
    try:
        msg = MIMEText(
            f"Un cliente está pidiendo algo fuera de los paquetes actuales.\n\n"
            f"Canal: {canal.upper()}\nUsuario: {user_id}\nMensaje: {mensaje}\n\n"
            f"Entra a la conversación para atenderlo personalmente.",
            "plain", "utf-8"
        )
        msg["Subject"] = "⚠️ Cliente pide servicio no listado — Elvi Memories"
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_USER
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"[ALERTA] Error email: {e}")


def _notificar_set_creativo_cumpleanos(user_id: str, canal: str, mensaje: str):
    import smtplib
    from email.mime.text import MIMEText
    from config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    if not SMTP_PASS:
        return
    try:
        msg = MIMEText(
            f"Un cliente está interesado en sets creativos para cumpleaños.\n\n"
            f"Canal: {canal.upper()}\nUsuario: {user_id}\nMensaje: {mensaje}\n\n"
            f"Entra a la conversación para atenderlo personalmente.",
            "plain", "utf-8"
        )
        msg["Subject"] = "🎂 Cliente interesado en sets creativos de cumpleaños — Elvi Memories"
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_USER
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"[SETS] Error email: {e}")


def limpiar_historial(user_id: str):
    if user_id in conversaciones:
        del conversaciones[user_id]
