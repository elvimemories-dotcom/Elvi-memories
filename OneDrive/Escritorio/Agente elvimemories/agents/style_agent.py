"""
AGENTE 5 — STYLE AGENT (Elvi Memories)
Ayuda al cliente a elegir el estilo de su sesión mostrando referencias visuales.
Hace preguntas para detectar el estilo y devuelve las imágenes correspondientes.
"""
import os
import anthropic
from config.settings import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=3)

REFERENCIAS_DIR = "referencias"

# Mapa de sesión → carpeta
SESIONES_MAP = {
    "cumpleanos": ["cumpleaños", "cumpleano", "cumpleanos", "birthday", "años", "fiesta"],
    "maternidad": ["maternidad", "embarazo", "embarazada", "bebe", "bebé", "prenatal", "baby",
                   "set creativo", "sets creativos", "set creativo", "creativos", "creativo"],
    "pareja":     ["pareja", "novios", "novio", "novia", "amor", "engagement", "enamorados", "boda"],
    "familia":    ["familia", "familiar", "hijos", "niños", "padres"],
    "lifestyle":  ["lifestyle", "natural", "casual", "cotidiano"],
}

# Mapa de estilo → carpeta
ESTILOS_MAP = {
    "elegante":  ["elegante", "elegancia", "sofisticado", "formal", "lujoso", "glamour"],
    "casual":    ["casual", "relajado", "comodo", "cómodo", "natural", "sencillo", "simple"],
    "sexy":      ["sexy", "atrevido", "sensual", "atrevida", "atrevido", "provocador"],
    "romantico": ["romantico", "romántico", "romantica", "romántica", "tierno", "dulce", "suave"],
    "natural":   ["natural", "aire libre", "boho", "bohemio", "organico", "orgánico"],
    "formal":    ["formal", "serio", "profesional", "clasico", "clásico"],
}

SYSTEM_PROMPT = """Eres Elvi, asistente de estilo de Elvi Memories, estudio fotográfico.

TU MISIÓN:
Ayudar al cliente a definir el estilo de su sesión para mostrarle referencias visuales perfectas.

FLUJO (síguelo en orden):
1. Si no sabes qué tipo de sesión es, pregúntalo primero.
2. Una vez que sepas el tipo de sesión, pregunta por el estilo con opciones claras.
   Ejemplo para cumpleaños:
   "¡Qué emoción tu cumpleaños! 🎂🤍 Para mostrarte referencias que te encanten,
   cuéntame: ¿qué estilo te llama más?
   ✨ *Elegante* — vestidos, luces, glamour
   🌸 *Romántico* — flores, tonos suaves, femenino
   😏 *Sexy/Atrevido* — looks atrevidos, actitud
   🌿 *Casual/Natural* — relajado, tú misma sin poses forzadas"

3. Cuando el cliente elija un estilo, confirma con entusiasmo y di que le vas a mostrar ejemplos.
   Cierra SIEMPRE con: [SESION: nombre_sesion] [ESTILO: nombre_estilo]
   Donde nombre_sesion es uno de: cumpleanos, maternidad, pareja, familia, lifestyle
   Y nombre_estilo es uno de: elegante, casual, sexy, romantico, natural, formal

IMPORTANTE:
- Si el cliente menciona varios estilos, elige el más dominante.
- Si no encaja perfecto, elige el más cercano.
- Tono cálido, emocionante, como amiga experta en moda y fotografía 🤍"""


def manejar_referencias(mensaje: str, historial: list = None) -> dict:
    """
    Conduce la conversación de estilo con el cliente.
    Retorna:
      - respuesta: texto para el cliente
      - sesion: carpeta de sesión detectada (o None si aún no se sabe)
      - estilo: carpeta de estilo detectada (o None si aún no se sabe)
      - imagenes: lista de rutas de imágenes a enviar (vacía si aún no hay)
    """
    messages = []
    if historial:
        messages.extend(historial)
    messages.append({"role": "user", "content": mensaje})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    texto = ""
    for block in response.content:
        if block.type == "text":
            texto = block.text
            break

    # Extraer sesion y estilo de las etiquetas
    sesion = _extraer_etiqueta(texto, "SESION")
    estilo = _extraer_etiqueta(texto, "ESTILO")
    texto_limpio = _limpiar_etiquetas(texto)

    imagenes = []
    if sesion and estilo:
        imagenes = _obtener_imagenes(sesion, estilo)

    return {
        "respuesta": texto_limpio,
        "sesion": sesion,
        "estilo": estilo,
        "imagenes": imagenes,
    }


def detectar_sesion_desde_historial(mensaje: str, historial: list) -> str | None:
    """Detecta la sesión desde el mensaje e historial sin llamar a Claude."""
    texto = mensaje.lower()
    for turno in historial[-6:]:
        texto += " " + turno.get("content", "").lower()
    for sesion, palabras in SESIONES_MAP.items():
        for palabra in palabras:
            if palabra in texto:
                return sesion
    return None


def _extraer_etiqueta(texto: str, etiqueta: str) -> str | None:
    """Extrae el valor de [ETIQUETA: valor] del texto."""
    marca = f"[{etiqueta}:"
    if marca not in texto:
        return None
    try:
        inicio = texto.index(marca) + len(marca)
        fin = texto.index("]", inicio)
        return texto[inicio:fin].strip().lower()
    except ValueError:
        return None


def _limpiar_etiquetas(texto: str) -> str:
    """Elimina las etiquetas [SESION:...] y [ESTILO:...] del texto visible."""
    import re
    return re.sub(r"\[SESION:[^\]]*\]|\[ESTILO:[^\]]*\]", "", texto).strip()


def _obtener_imagenes(sesion: str, estilo: str | None, max_imagenes: int = 3) -> list[str]:
    """
    Retorna las rutas de las imágenes en referencias/{sesion}/{estilo}/.
    Si no hay subcarpeta de estilo, usa directamente referencias/{sesion}/.
    Máximo max_imagenes para no saturar al cliente.
    """
    extensiones = {".jpg", ".jpeg", ".png", ".webp"}

    def _listar(carpeta: str) -> list[str]:
        if not os.path.isdir(carpeta):
            return []
        return [
            os.path.join(carpeta, f)
            for f in os.listdir(carpeta)
            if os.path.splitext(f)[1].lower() in extensiones
        ]

    # Intentar primero con subcarpeta de estilo
    if estilo:
        archivos = _listar(os.path.join(REFERENCIAS_DIR, sesion, estilo))
        if archivos:
            return archivos[:max_imagenes]

    # Fallback: imágenes directamente en la carpeta de sesión
    archivos = _listar(os.path.join(REFERENCIAS_DIR, sesion))
    return archivos[:max_imagenes]
