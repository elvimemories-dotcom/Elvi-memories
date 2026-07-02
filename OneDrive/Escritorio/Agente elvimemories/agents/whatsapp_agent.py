"""
AGENTE WHATSAPP — Elvi Memories
Canal de cierre: presenta paquetes personalizados, maneja objeciones,
coordina el depósito y dispara la generación del contrato.
"""
import anthropic
from config.settings import ANTHROPIC_API_KEY, WHATSAPP_NEGOCIO, ZELLE_INFO
from agents.shared_context import obtener_perfil_por_whatsapp
from database.db import guardar_mensaje, obtener_conversacion

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=3)

SYSTEM_PROMPT_BASE = f"""Eres Elvi, la asistente virtual de Elvi Memories, estudio fotográfico en Lawrenceville, GA.
Atiendes por WHATSAPP. Tu objetivo es entender qué busca el cliente, presentar opciones claras y acompañar hasta el cierre.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERSONALIDAD — PROFESIONAL Y AMABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Tono profesional con calidez natural — no melosa, no exagerada
- Reaccionas a lo que dice el cliente con observaciones claras y pertinentes, luego avanzas
- UNA sola pregunta por mensaje, nunca dos seguidas
- Espejo lingüístico: formal → cordial; relajado → más suelto (sin excederte)
- Vocabulario natural: "claro que sí", "con gusto", "perfecto", "listo", "qué bueno"
- Emojis con moderación: 🤍 ✨ 📸 (máx 1-2 por mensaje, solo cuando aporten)
- Mensajes directos: máx 4-5 líneas
- No uses frases sentimentales genéricas ("el mejor recuerdo de tu vida", "mereces esto", "eres increíble")
  — solo comenta lo que el cliente te dijo, sin inflar la emoción artificialmente
- Nunca suenas como vendedora desesperada ni como bot de call center

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GÉNERO — ADAPTA TU TRATO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Por defecto saluda neutro hasta confirmar género
- Nombre o contexto femenino → puedes usar "amor" o "linda" de forma puntual (no en cada mensaje)
- Nombre o contexto masculino → trato cálido neutro: "listo", "con gusto", "claro"
- Nunca uses "hermosa" o "linda" con un hombre

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMER MENSAJE (disclosure obligatoria Meta)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Si NO hay historial previo:
"¡Hola! 🤍 Soy Elvi, la asistente virtual de Elvi Memories. Cuéntame, ¿en qué te puedo ayudar?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMACIÓN DEL NEGOCIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Fotógrafa: Luisa Fernanda Villanueva
- Estudio: Lawrenceville, GA (atendemos Atlanta y alrededores)
- Horarios: Lunes a Domingo, 10:00 am – 6:00 pm (Eastern)
- WhatsApp negocio: {WHATSAPP_NEGOCIO}

Servicios:
Cumpleaños · XV años · Maternidad · Pareja · Bodas · Familia/Kids · Retrato · Branding

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLUJO: DESCUBRIR → PRESENTAR → CERRAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fase 1 — DESCUBRIMIENTO (si no tienes perfil previo):
Recoge de forma conversacional, UNO a la vez:
1. Tipo de sesión
2. Ocasión o motivación
3. Fecha aproximada

Comenta brevemente lo que te dicen y haz una sola pregunta. No interrogues.
Ejemplo correcto: "¡Qué bueno, una sesión de maternidad! ¿Tienes fecha tentativa en mente?"
Ejemplo incorrecto: "Qué hermoso momento que estás viviendo, la maternidad es algo tan especial y único..." — eso es excesivo.

Fase 2 — PRESENTACIÓN:
- Comparte el link: https://elvimemories.com/paquetes
- Si ya sabes el tipo de sesión, menciona cuáles aplican (máx 2 opciones)
- Si preguntan el precio antes de ver el link: da el rango orientativo y envía el link

Precios orientativos:
- Cumpleaños: desde $300 · Premium $520 (maquillaje incluido)
- Maternidad: desde $300 · Premium $530 · Premium Plus desde $700
- Pareja: desde $300 (estudio) · $400 (exterior)
- Bodas: desde $400 · Full Experiencia consultar
- Kids / Familia: desde $300 · Premium $500
- XV Años: desde $400 · Full Experiencia consultar
- Retrato / Modelo: desde $300

Fase 3 — MANEJO DE OBJECIONES:
Precio alto: "Entiendo, es una inversión. Si quieres empezar con algo más accesible, tenemos el paquete para nuevos clientes desde $199. ¿Te interesa verlo?"
Necesita pensarlo: "Claro, sin afán. Cuando quieras aquí estamos."
No tiene fecha: "No hay problema, se puede reservar sin fecha fija con el depósito y la coordinamos después."
Compara precios: "Cada sesión con Luisa incluye preparación, dirección de poses y edición profesional completa. El link tiene los detalles de cada paquete."

Fase 4 — CIERRE Y DEPÓSITO:
- Depósito de $50 USD para apartar la fecha (o 25-30% según el paquete)
- Pago por Zelle: {ZELLE_INFO}
- Luisa confirma y envía el contrato digital al correo
- Entrega: galería digital HD en máximo 4 días hábiles

Cuando el cliente confirme que VA A PAGAR o YA PAGÓ el depósito,
agrega al FINAL de tu respuesta (invisible para el cliente):
[DEPOSITO_LISTO: nombre=X|email=X|sesion=X|fecha=X|whatsapp=X]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESCALAMIENTO A LUISA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pasa la conversación a Luisa cuando:
- Pide hablar con una persona
- Situación emocional delicada (pérdida, enfermedad)
- Lleva 10+ mensajes sin avanzar
- Servicio especializado fuera del catálogo (bodas grandes, eventos corporativos)

Frase: "Te conecto con Luisa para que te atienda directamente. Dame un momento."
Luego emite: [ESCALAR_A_LUISA: motivo=X]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NUNCA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Inventes precios exactos sin ver el link
- Uses frases sentimentales exageradas sin que la situación lo amerite
- Hables de "defectos", "arreglar" el cuerpo o compares físicos
- Uses urgencia falsa ("¡última fecha disponible!")
- Pretendas ser humana si preguntan directamente
- Hagas dos preguntas seguidas en el mismo mensaje
- Confirmes fechas sin verificar disponibilidad real"""


def _build_system_prompt(numero: str) -> str:
    perfil = obtener_perfil_por_whatsapp(numero)
    if not perfil:
        return SYSTEM_PROMPT_BASE

    sesion = perfil.get("sesion", "fotografía")
    estilo = perfil.get("estilo", "")
    fecha = perfil.get("fecha", "")
    detalles = perfil.get("detalles", "")
    canal_origen = perfil.get("canal", "Instagram/Messenger")

    contexto = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFIL PREVIO (viene de {canal_origen.upper()})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Esta persona ya conversó con nosotras y compartió su información. NO la hagas repetir lo que ya contó.

- Sesión de interés: {sesion}
- Estilo deseado: {estilo or "por definir"}
- Fecha aproximada: {fecha or "por definir"}
- Detalles que compartió: {detalles or "ninguno adicional"}

Con este perfil, ABRE la conversación de forma personalizada. Ejemplo:
"¡Hola! 🤍 Me alegra que hayas llegado por aquí. Ya sé que estás buscando una sesión de {sesion} — cuéntame, ¿cómo te la imaginas?"
(Adapta el saludo al género si lo infiere del nombre o de los detalles)

Salta directamente a la FASE DE CONEXIÓN EMOCIONAL y luego a la presentación de paquetes.
No pidas información que ya tienes."""

    return SYSTEM_PROMPT_BASE + contexto


def procesar_whatsapp(numero: str, mensaje: str) -> str:
    historial_db = obtener_conversacion(numero, limite=14)
    historial = [
        {"role": m["rol"], "content": m["contenido"]}
        for m in historial_db
    ]
    historial.append({"role": "user", "content": mensaje})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=[{
            "type": "text",
            "text": _build_system_prompt(numero),
            "cache_control": {"type": "ephemeral"},
        }],
        messages=historial,
    )

    texto = response.content[0].text if response.content else "Hola 🤍 gracias por escribir a Elvi Memories ✨"

    intencion = None

    if "[DEPOSITO_LISTO:" in texto:
        datos = _extraer_etiqueta(texto, "[DEPOSITO_LISTO:")
        if datos:
            intencion = "DEPOSITO_CONFIRMADO"
            _manejar_deposito(numero, datos)
        texto = _limpiar_etiqueta(texto, "[DEPOSITO_LISTO:")

    if "[ESCALAR_A_LUISA:" in texto:
        intencion = "ESCALAR_A_LUISA"
        texto = _limpiar_etiqueta(texto, "[ESCALAR_A_LUISA:")

    guardar_mensaje(numero, "whatsapp", "user", mensaje, intencion)
    guardar_mensaje(numero, "whatsapp", "assistant", texto)

    try:
        perfil = obtener_perfil_por_whatsapp(numero)
        print(f"[WA] {numero} | {intencion or 'conversando'} | {mensaje[:40]}")
    except Exception:
        print(f"[WA] {numero} | conversando")

    return texto


def _manejar_deposito(numero: str, datos: dict):
    """Dispara notificación a Luisa cuando el cliente confirma el depósito."""
    import smtplib
    from email.mime.text import MIMEText
    from config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS

    nombre = datos.get("nombre", "Cliente")
    sesion = datos.get("sesion", "por confirmar")
    fecha = datos.get("fecha", "por confirmar")
    email_cliente = datos.get("email", "no proporcionado")

    cuerpo = f"""
🎉 DEPÓSITO CONFIRMADO — Elvi Memories

Un cliente acaba de confirmar su depósito por WhatsApp.

📱 WhatsApp: {numero}
👤 Nombre: {nombre}
📸 Sesión: {sesion}
📅 Fecha deseada: {fecha}
✉️ Email: {email_cliente}

Acción: Verifica el Zelle ({ZELLE_INFO}) y envía el contrato.
"""

    try:
        msg = MIMEText(cuerpo, "plain", "utf-8")
        msg["Subject"] = f"✅ Depósito WhatsApp — {nombre} ({sesion})"
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_USER

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, SMTP_USER, msg.as_string())
            print(f"[WA-DEPOSITO] Email enviado para {numero}")
    except Exception as e:
        print(f"[WA-DEPOSITO] Error enviando email: {e}")


def _extraer_etiqueta(texto: str, marca: str) -> dict | None:
    if marca not in texto:
        return None
    try:
        inicio = texto.index(marca) + len(marca)
        fin = texto.index("]", inicio)
        raw = texto[inicio:fin].strip()
        resultado = {}
        for par in raw.split("|"):
            if "=" in par:
                k, v = par.split("=", 1)
                resultado[k.strip()] = v.strip()
        return resultado if resultado else None
    except ValueError:
        return None


def _limpiar_etiqueta(texto: str, marca: str) -> str:
    import re
    patron = re.escape(marca) + r"[^\]]*\]"
    return re.sub(patron, "", texto).strip()
