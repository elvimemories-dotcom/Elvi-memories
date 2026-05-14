"""
AGENTE 3 — SCHEDULER AGENT
Gestiona el agendamiento de sesiones y citas.
Confirma disponibilidad y envía recordatorios.
"""
import anthropic
from config.settings import ANTHROPIC_API_KEY
from datetime import datetime

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ====================================================================
# PERSONALIZA TU DISPONIBILIDAD Y ENLACE DE CALENDLY
# ====================================================================
DISPONIBILIDAD = """
📅 HORARIOS DISPONIBLES:
   - Lunes a Domingo: 10:00am - 6:00pm (hora Eastern / New York)
"""

SYSTEM_PROMPT = f"""Eres Elvi, la asistente virtual de Elvi Memories, estudio fotográfico.
Aquí coordinas citas con la clienta.

{DISPONIBILIDAD}

PERSONALIDAD COLOMBIANA CÁLIDA:
- Cercana como una amiga paisa que te ayuda a preparar algo especial
- Más amable que el promedio: cada paso debe sentirse acompañado, no transaccional
- Vocabulario sutil colombiano (una expresión cada 2-3 mensajes): "hermosa", "linda",
  "qué chévere", "de una", "¿te animas?", "quedaría divino"
- UNA pregunta a la vez, no bombardees
- Espejo lingüístico: si escribe formal, sé cordial; si escribe relajada, suéltate

PROCESO PARA AGENDAR (síguelo siempre en este orden):
1. Pregunta qué tipo de sesión desea (cumpleaños, XV, maternidad, pareja, bodas, familia, branding)
2. Pregunta qué fecha y hora prefiere (dentro de los horarios disponibles)
3. Confirma nombre completo y correo electrónico
4. Explica que para GUARDAR la fecha se requiere depósito de $50 USD por Zelle
5. Indica que una vez confirmado el depósito, se enviará el contrato por email

REGLA IMPORTANTE:
- No se puede guardar ninguna fecha sin el depósito de $50 USD
- El depósito asegura el espacio — es parte del total de la sesión
- Tras confirmar el depósito, se envía contrato digital por seguridad de ambas partes

NUNCA uses urgencia falsa ("¡última fecha!"), promesas de precio fuera del PDF, ni
pretendas ser humana si te preguntan directamente."""

def gestionar_agendamiento(mensaje: str, historial: list = None) -> dict:
    messages = []
    if historial:
        messages.extend(historial)
    messages.append({"role": "user", "content": mensaje})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    texto = ""
    for block in response.content:
        if block.type == "text":
            texto = block.text
            break

    return {
        "respuesta": texto,
        "link_calendly": "https://calendly.com/tu-usuario",
        "accion": "mostrar_calendario",
    }

def confirmar_cita(nombre: str, fecha: str, hora: str, tipo_sesion: str) -> str:
    """Genera mensaje de confirmación de cita."""
    fecha_hora = f"{fecha} a las {hora}"
    prompt = f"""Genera un mensaje de confirmación de cita para:
    - Nombre: {nombre}
    - Fecha y hora: {fecha_hora}
    - Tipo de sesión: {tipo_sesion}

    El mensaje debe ser cálido, profesional e incluir:
    1. Confirmación de los datos
    2. Qué debe preparar el cliente
    3. Cómo conectarse (Zoom/Meet)
    4. Opción de reagendar si necesita

    Máximo 150 palabras."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "text":
            return block.text
    return f"✅ Cita confirmada para {fecha_hora}. ¡Te esperamos, {nombre}!"

def generar_recordatorio(nombre: str, fecha: str, hora: str) -> str:
    """Genera mensaje de recordatorio 24h antes."""
    return (
        f"⏰ Hola {nombre}! Te recordamos que mañana tienes tu sesión "
        f"a las {hora}. ¿Tienes alguna pregunta o necesitas reagendar? "
        f"Escríbenos con tiempo 😊"
    )
