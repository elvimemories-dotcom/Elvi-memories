"""
AGENTE GEMINI — Elvi Memories
Genera descripciones de referencias visuales y busca imágenes de inspiración
según lo que el cliente describe (color, estilo, ambiente).
"""
import httpx
from google import genai
from config.settings import GOOGLE_AI_API_KEY

client = genai.Client(api_key=GOOGLE_AI_API_KEY)

SYSTEM_PROMPT = """Eres un experto en fotografía de estudio y moda para Elvi Memories.

Cuando el cliente describe una referencia visual (colores, estilos, ambientes, ropa),
tu trabajo es:
1. Entender exactamente qué está pidiendo
2. Traducirlo a términos de fotografía de estudio profesional
3. Generar entre 3 y 5 términos de búsqueda en INGLÉS, simples y directos, para encontrar
   imágenes de referencia en Unsplash relacionadas con fotografía de retrato o estudio.

IMPORTANTE:
- Siempre orientado a sesiones de estudio fotográfico o exteriores (no comercial)
- Si piden algo imposible en estudio, adapta a lo más cercano posible
- Responde SOLO con los términos de búsqueda separados por coma, sin explicación
- Ejemplo de respuesta: "elegant birthday studio portrait, red dress photography, glamour studio shoot"
"""


async def obtener_referencias_gemini(descripcion: str, tipo_sesion: str = "") -> dict:
    """
    Usa Gemini para entender la descripción del cliente y buscar imágenes en Unsplash.
    Retorna:
      - respuesta: texto para el cliente
      - imagenes: lista de URLs de imágenes de referencia
    """
    prompt = f"Tipo de sesión: {tipo_sesion}\nDescripción del cliente: {descripcion}"

    try:
        gemini_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"system_instruction": SYSTEM_PROMPT}
        )
        terminos = gemini_response.text.strip()
    except Exception as e:
        print(f"[GEMINI] Error: {e}")
        terminos = f"{tipo_sesion} portrait studio photography"

    # Buscar imágenes en Unsplash con esos términos
    imagenes_urls = await _buscar_unsplash(terminos)

    if imagenes_urls:
        respuesta = (
            f"¡Me encanta tu visión! 🤍 Aquí te mando algunas referencias de inspiración "
            f"basadas en lo que describes ✨\n\n"
            f"Ten en cuenta que estas son referencias de estilo — en el estudio de Elvi "
            f"adaptamos todo a tu esencia y lo que mejor te quede 📸"
        )
    else:
        respuesta = (
            f"¡Qué estilo tan bonito describes! 🤍 Para mostrarte referencias exactas, "
            f"¿puedes contarme un poco más sobre el ambiente que te imaginas? "
            f"Por ejemplo: ¿colores, tipo de ropa, si prefieres fondo liso o decorado? ✨"
        )

    return {
        "respuesta": respuesta,
        "imagenes": imagenes_urls,
        "terminos": terminos,
    }


async def _buscar_unsplash(terminos: str, cantidad: int = 3) -> list[str]:
    """
    Busca imágenes en Unsplash sin API key usando la búsqueda pública.
    Retorna lista de URLs de imágenes.
    """
    # Usar el primer término de búsqueda (el más relevante)
    primer_termino = terminos.split(",")[0].strip()
    query = primer_termino.replace(" ", "+")

    try:
        # Unsplash Source API — no requiere key, devuelve imágenes públicas
        urls = []
        temas = [t.strip().replace(" ", "+") for t in terminos.split(",")[:cantidad]]
        for tema in temas:
            url = f"https://source.unsplash.com/800x1000/?{tema}"
            urls.append(url)
        return urls
    except Exception as e:
        print(f"[UNSPLASH] Error: {e}")
        return []


def describir_referencia_cliente(mensaje: str, tipo_sesion: str = "") -> str:
    """
    Usa Gemini para generar una respuesta empática cuando el cliente describe
    qué tipo de fotos quiere, antes de mostrar las referencias.
    """
    prompt = f"""El cliente de Elvi Memories (estudio fotográfico) describe lo que quiere:
Tipo de sesión: {tipo_sesion}
Mensaje: {mensaje}

Genera una respuesta corta (2-3 oraciones) muy cálida y emocionante que:
1. Valide su visión con entusiasmo
2. Le diga que vas a buscarle referencias de inspiración
3. Aclare que en el estudio se adapta todo a su estilo personal

Responde en español, tono femenino y cálido, con emojis moderados."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"[GEMINI] Error descripcion: {e}")
        return "¡Me encanta cómo lo describes! 🤍 Déjame buscar referencias de inspiración para ti ✨"
