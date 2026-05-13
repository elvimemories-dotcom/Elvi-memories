"""
Contexto compartido entre canales.
Guarda el perfil completo descubierto en Instagram/Messenger
para que WhatsApp ya sepa qué tipo de sesión, estilo y detalles quiere la clienta.
"""
import time

_contextos: dict = {}


def guardar_perfil_completo(user_id: str, perfil: dict, canal: str):
    _contextos[user_id] = {
        **perfil,
        "canal": canal,
        "timestamp": time.time(),
    }


def guardar_contexto(user_id: str, sesion: str, canal: str):
    """Compatibilidad con orchestrator y sales_agent existentes."""
    entrada = _contextos.get(user_id, {})
    entrada.update({"sesion": sesion, "canal": canal, "timestamp": time.time()})
    _contextos[user_id] = entrada


def obtener_contexto(user_id: str) -> dict | None:
    return _contextos.get(user_id)


def obtener_contextos_recientes(minutos: int = 60) -> list[dict]:
    cutoff = time.time() - minutos * 60
    return [v for v in _contextos.values() if v["timestamp"] > cutoff]


def limpiar_contexto(user_id: str):
    _contextos.pop(user_id, None)
