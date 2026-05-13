"""
AGENTE DE CONOCIMIENTO — Elvi Memories
Conoce el contenido completo de todos los paquetes.
Responde preguntas específicas sobre precios, incluye, tiempos, formas de pago, etc.
"""
import anthropic
from config.settings import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=3)

# ====================================================================
# BASE DE CONOCIMIENTO — extraída directamente de los PDFs
# ====================================================================
CONOCIMIENTO_PAQUETES = """
============================
INFORMACIÓN GENERAL DE ELVI MEMORIES
============================
Fotógrafa: Luisa Fernanda Villanueva
Estudio: Elvi Memories — Lawrenceville, GA (Atlanta y alrededores)
WhatsApp: +1 678-765-9231
Instagram: @elvimemoriesfotografia

PROCESO GENERAL PARA TODAS LAS SESIONES:
1. Planificación personalizada: conversamos sobre estilo, vestuario, locaciones y detalles
2. Programación: acordamos fecha y hora, se reserva con depósito
3. Sesión de fotos: acompañamiento profesional en poses y confianza ante la cámara
4. Entrega: galería con marca de agua para selección, luego edición profesional y entrega en HD

FORMAS DE PAGO (aplica a todos los paquetes):
- Efectivo
- Tarjeta de crédito
- Tarjeta de débito
- Transferencia bancaria (Zelle): elvimemories@gmail.com

RESERVA: Depósito de $50 USD o el 25-30% del valor total según el paquete
ENTREGA: Galería digital lista en máximo 4 días hábiles (sesiones estudio)
Las fotos llegan por link digital descargable en HD desde cualquier dispositivo (celular, computador, tablet)

FOTO ADICIONAL: $20 USD por imagen adicional, editada profesionalmente en alta resolución
ACOMPAÑANTE: Máximo 1 persona puede acompañar en la sesión sin costo adicional. Más personas tienen costo extra.

============================
PAQUETE CUMPLEAÑOS
============================
Archivo PDF: CUMPLEAÑOS.pdf
Sesión para: mujeres que desean celebrar su cumpleaños con fotos profesionales

PAQUETE PREMIUM — $520 USD (sin maquillaje: $400 USD)
- Set decorativo con diseño de globos, champán, número de cumpleaños, sparkles fireworks, pastel de diseño elegido por el cliente
- 1 hora de sesión
- Hasta 3 cambios de outfit
- Maquillaje profesional incluido
- Dirección de poses y acompañamiento
- 13 fotografías finales editadas en HD
- Link digital para descarga
- Regalo: videoclip o reel cinético

PAQUETE ESTÁNDAR — $300 USD
- Set plano unicolor con globos, champán, número de cumpleaños, sparkles fireworks, pastel con diseños del catálogo
- 1 hora de sesión
- Hasta 2 cambios de outfit
- Dirección de poses y acompañamiento
- 9 fotografías finales editadas en HD
- Link digital para descarga

RESERVA: $50 USD o 25% del valor
ENTREGA: Máximo 4 días hábiles
PREGUNTAS FRECUENTES CUMPLEAÑOS:
- ¿Con cuánto tiempo reservar? Entre 1 y 2 semanas antes
- ¿Ayuda a posar? Sí, guía en todo momento, no necesitas experiencia
- ¿Puedo traer acompañante? Sí, máximo 1 persona sin costo adicional
- ¿Puedo elegir fotos adicionales? Sí, $20 USD por imagen extra

============================
PAQUETE MATERNIDAD / GESTACIÓN
============================
Archivo PDF: Copia de GESTACIÓN.pdf
Sesión para: futuras mamás que desean guardar el momento del embarazo

PREMIUM PLUS — Desde $700 USD
- Concepto creativo de fantasía con temática personalizada
- 1 hora 30 minutos de sesión
- Hasta 3 cambios de outfit (opcional)
- Diseño y elaboración de vestuario acorde al concepto (opcional)
- Maquillaje profesional artístico
- Dirección de poses
- 15 fotografías finales editadas artísticamente
- Regalo: videoclip o reel cinético

PREMIUM — $530 USD (sin maquillaje: $400 USD)
- Set decorativo con diseño personalizado
- 1 vestuario de maternidad del inventario del estudio (opcional)
- 1 hora de sesión
- Hasta 3 cambios de outfit (opcional)
- Maquillaje profesional
- Dirección de poses
- 13 fotografías finales editadas en HD
- Link digital para descarga
- Regalo: videoclip o reel cinético

PAQUETE ESTÁNDAR — $300 USD
- Set plano unicolor, estilos minimalistas o set decorativo básico (telones, efectos de luces)
- 1 hora de sesión
- Hasta 2 cambios de outfit
- Dirección de poses
- 9 fotografías finales editadas en HD
- Link digital para descarga

PAQUETE EXTERIOR (AL AIRE LIBRE) — precio varía
- Locación a elección (parque, jardín o sitio especial en Atlanta y alrededores)
- 1 hora de sesión
- Dirección de poses
- Link digital en HD
- Fotos editadas profesionalmente

RESERVA: $50 USD o 25% del valor

============================
PAQUETE PAREJA
============================
Archivo PDF: Pareja.pdf
Sesión para: parejas que quieren capturar su historia y conexión

PAQUETE EN STUDIO — $300 USD
- 1 hora de sesión en estudio con iluminación profesional
- Acompañamiento y dirección de poses
- 9 fotografías finales editadas en HD
- Link digital para descarga desde cualquier dispositivo
- Regalo: videoclip o reel cinematográfico

PAQUETE EN EXTERIOR — $400 USD
- Locación a elección (parque, jardín, sitio especial en Atlanta y alrededores)
- 1 hora de sesión
- Dirección de poses y acompañamiento
- 12 fotografías finales editadas en HD
- Link digital para descarga
- Regalo: videoclip o reel cinético

RESERVA: $50 USD

============================
PAQUETE BODAS
============================
Archivo PDF: BODAS.pdf
Sesión para: parejas que se casan o van a comprometerse

PAQUETE PROPUESTA — $400 USD
- Locación: ayuda a elegir lugar en Atlanta y alrededores (o locación del cliente)
- 1 hora de sesión
- Fotos espontáneas y dirigidas
- 15 fotografías finales editadas en HD
- Link digital para descarga

PAQUETE SAVE THE DATE — $300 USD (si se contrata con paquete de boda) / $400 USD independiente
- 1 hora de sesión
- Acompañamiento profesional
- Diseño de periódico para save the date (opcional)
- 9 fotografías finales editadas en HD
- Link digital para descarga

PAQUETE CIVIL ÍNTIMO — $400 USD
- Sesión exterior en lugar preferido del cliente (corte o parque)
- 1 hora de cobertura
- Fotos espontáneas y dirigidas
- Acompañamiento profesional
- 15 fotografías finales editadas en HD
- Link digital para descarga

PAQUETE A TU MEDIDA (cobertura personalizada)
- Duración: desde 3 hasta 10 horas
- Fotografías: desde 15 hasta 90 editadas en HD
- Opción de video cinematográfico de 1 a 5 minutos
- Hasta 3 locaciones
- Servicio de impresión disponible (álbumes, fotos, retratos)
- Precio: depende del paquete personalizado

PAQUETE FULL EXPERIENCIA (cobertura completa de boda)
- 11 horas continuas de cobertura en hasta 3 locaciones
- Desde la preparación hasta la fiesta
- 90 fotografías finales editadas en HD
- Entrega en crudo de todas las fotos tomadas
- Link digital de descarga
- Video cinematográfico de 2 a 5 minutos
- Edición profesional completa
- Precio: consultar

RESERVA BODAS: 30% del valor total
PAGO RESTANTE: un día antes o un día después de la boda
ENTREGA: mínimo 4 a 25 días según el paquete

============================
PAQUETE KIDS / FAMILIA
============================
Archivo PDF: KIDS.pdf
Sesión para: bebés, niños y familias

PREMIUM PLUS — Desde $700 USD
- Concepto creativo de fantasía con temática personalizada
- Maqueta de pastel creativa
- 1 hora 30 minutos de sesión
- Acompañamiento durante toda la sesión (bebé siempre cómodo)
- 12 fotografías finales editadas artísticamente
- Regalo: videoclip o reel cinematográfico

PREMIUM — $500 USD
- Set decorativo de globos del color preferido por el cliente
- Número de cumpleaños en madera o luz
- Maqueta de pastel
- 1 hora de sesión
- Acompañamiento durante toda la sesión
- 12 fotografías finales editadas
- Regalo: videoclip o reel cinematográfico

BÁSICO — $300 USD
- Set plano unicolor
- Globo número de cumpleaños (opcional)
- 1 hora de sesión
- Acompañamiento durante toda la sesión
- 8 fotografías finales editadas
- Regalo: videoclip o reel cinematográfico

RESERVA: $50 USD o 25% del valor
FORMAS DE PAGO: efectivo, tarjeta de crédito, tarjeta de débito, Zelle

============================
PAQUETE XV AÑOS
============================
Archivo PDF: XV años_pdf.pdf
Sesión para: quinceañeras

PAQUETE PEQUEÑO — $400 USD
- Sesión exterior en lugar preferido del cliente (iglesia o parque)
- 1 hora de cobertura
- Fotos espontáneas y dirigidas
- Acompañamiento profesional (fotos en pareja y en familia)
- 15 fotografías finales editadas en HD
- Álbum digital para descarga

PAQUETE A TU MEDIDA (cobertura personalizada)
- Duración: desde 3 hasta 10 horas
- Fotografías: desde 15 hasta 90 editadas en HD
- Opción de video cinematográfico
- Hasta 3 locaciones
- Servicio de impresión disponible
- Precio: depende del paquete personalizado

PAQUETE FULL EXPERIENCIA
- 10 horas continuas de cobertura en hasta 3 locaciones
- Desde la preparación (maquillaje) hasta la fiesta
- 90 fotografías finales editadas en HD
- Entrega en crudo de todas las fotos
- Video cinematográfico de 2 a 5 minutos
- Edición completa profesional

RESERVA XV AÑOS: 30% del valor total
PAGO RESTANTE: un día antes o después del evento
ENTREGA: mínimo 4 a 25 días según el paquete
"""

SYSTEM_PROMPT = f"""Eres Elvi, asistente de ventas experta de Elvi Memories, estudio fotográfico en Lawrenceville, GA.
Estás atendiendo por WHATSAPP — el canal de ventas principal.

TIENES ACCESO AL CONOCIMIENTO COMPLETO DE TODOS LOS PAQUETES:
{CONOCIMIENTO_PAQUETES}

TU MISIÓN:
- Responder CUALQUIER pregunta sobre paquetes con información precisa y detallada
- Si preguntan por precio, darlo con confianza y detallar qué incluye
- Si preguntan por tiempo de entrega, responder exactamente (4 días hábiles en general)
- Si preguntan si pueden ver las fotos en el celular, responder SÍ — link digital descargable desde cualquier dispositivo
- Si preguntan cuántas fotos, dar el número exacto según el paquete
- Si preguntan por maquillaje, informar qué paquetes lo incluyen
- Si preguntan por formas de pago, mencionar todas: efectivo, tarjeta crédito, débito, Zelle
- Comparar paquetes cuando el cliente lo pida
- Guiar al cliente hacia el paquete que más se ajuste a lo que quiere

TONO: Cálido, emocionante, como amiga experta en fotografía 🤍
NO menciones WhatsApp — ya estás ahí.
NO inventes información que no está en los paquetes.
Si el cliente pregunta algo que no está cubierto, di que lo puedes consultar con Luisa."""


def responder_pregunta_paquete(mensaje: str, historial: list = None) -> str:
    """
    Responde preguntas específicas sobre paquetes usando la base de conocimiento completa.
    Usado cuando el cliente hace preguntas de detalles, precios, tiempos, etc.
    """
    messages = []
    if historial:
        messages.extend(historial)
    messages.append({"role": "user", "content": mensaje})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    for block in response.content:
        if block.type == "text":
            return block.text
    return "Claro, con gusto te explico 🤍 ¿Sobre cuál paquete tienes preguntas?"


def obtener_resumen_paquete(tipo_sesion: str) -> str:
    """Retorna el resumen del paquete específico para incluir en el contexto."""
    tipo = tipo_sesion.lower()
    if any(p in tipo for p in ["cumple", "birthday", "años"]):
        return "CUMPLEAÑOS: Estándar $300 (9 fotos, 2 outfits, 1h) | Premium $520 (13 fotos, 3 outfits, 1h, maquillaje)"
    elif any(p in tipo for p in ["maternidad", "gestac", "embaraz", "bebe", "baby"]):
        return "MATERNIDAD: Estándar $300 (9 fotos) | Premium $530 (13 fotos, maquillaje) | Premium Plus desde $700 (15 fotos, concepto creativo)"
    elif any(p in tipo for p in ["pareja", "novio", "amor"]):
        return "PAREJA: Studio $300 (9 fotos) | Exterior $400 (12 fotos)"
    elif any(p in tipo for p in ["boda", "matrimonio"]):
        return "BODAS: Civil $400 | Save the Date $300 | Propuesta $400 | Full Experiencia 11h consultar"
    elif any(p in tipo for p in ["kids", "familia", "niño", "bebe"]):
        return "KIDS: Básico $300 (8 fotos) | Premium $500 (12 fotos) | Premium Plus desde $700 (12 fotos, concepto artístico)"
    elif any(p in tipo for p in ["xv", "quince"]):
        return "XV AÑOS: Pequeño $400 (15 fotos, 1h) | A tu medida | Full Experiencia 10h"
    return "Tenemos paquetes de Cumpleaños, Maternidad, Pareja, Bodas, Kids y XV Años 🤍"
