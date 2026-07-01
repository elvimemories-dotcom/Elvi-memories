"""
Base de datos SQLite — Elvi Memories
Guarda todas las conversaciones, mensajes y clientes.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "elvi_memories.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas si no existen."""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            canal TEXT NOT NULL,
            primer_contacto TEXT NOT NULL,
            ultimo_contacto TEXT NOT NULL,
            total_mensajes INTEGER DEFAULT 0,
            whatsapp_cliente TEXT,
            perfil_completo INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            canal TEXT NOT NULL,
            rol TEXT NOT NULL,
            contenido TEXT NOT NULL,
            intencion TEXT,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS conversaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            canal TEXT NOT NULL,
            resumen TEXT,
            estado TEXT DEFAULT 'activa',
            creada TEXT NOT NULL,
            actualizada TEXT NOT NULL
        );
        """)
        columnas = [r[1] for r in conn.execute("PRAGMA table_info(clientes)").fetchall()]
        if "perfil_completo" not in columnas:
            conn.execute("ALTER TABLE clientes ADD COLUMN perfil_completo INTEGER DEFAULT 0")
    print("[DB] Base de datos inicializada")


def guardar_mensaje(user_id: str, canal: str, rol: str, contenido: str, intencion: str = None):
    """Guarda un mensaje en la base de datos."""
    now = datetime.now().isoformat()
    with get_conn() as conn:
        # Guardar mensaje
        conn.execute(
            "INSERT INTO mensajes (user_id, canal, rol, contenido, intencion, timestamp) VALUES (?,?,?,?,?,?)",
            (user_id, canal, rol, contenido, intencion, now)
        )
        # Actualizar o crear cliente
        conn.execute("""
            INSERT INTO clientes (user_id, canal, primer_contacto, ultimo_contacto, total_mensajes)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                ultimo_contacto = ?,
                total_mensajes = total_mensajes + 1
        """, (user_id, canal, now, now, now))


def obtener_conversacion(user_id: str, limite: int = 50) -> list:
    """Retorna los últimos mensajes de un usuario."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT rol, contenido, intencion, timestamp FROM mensajes WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limite)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def marcar_perfil_completo(user_id: str):
    """Marca que el bot ya completó el descubrimiento con este cliente.
    A partir de aquí se considera 'cliente con conversación previa establecida'."""
    with get_conn() as conn:
        conn.execute("UPDATE clientes SET perfil_completo=1 WHERE user_id=?", (user_id,))


def cliente_tiene_perfil_completo(user_id: str) -> bool:
    """True si ya se completó el flujo de descubrimiento con este cliente alguna vez."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT perfil_completo FROM clientes WHERE user_id=?", (user_id,)
        ).fetchone()
    return bool(row and row["perfil_completo"])


def guardar_whatsapp_cliente(user_id: str, whatsapp: str):
    """Guarda el número WhatsApp del cliente para que Luisa lo contacte manualmente."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE clientes SET whatsapp_cliente=? WHERE user_id=?",
            (whatsapp, user_id)
        )


def obtener_todos_los_clientes() -> list:
    """Retorna todos los clientes para el panel."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT c.user_id, c.canal, c.primer_contacto, c.ultimo_contacto, c.total_mensajes,
                   c.whatsapp_cliente,
                   (SELECT contenido FROM mensajes WHERE user_id=c.user_id ORDER BY id DESC LIMIT 1) as ultimo_mensaje,
                   (SELECT intencion FROM mensajes WHERE user_id=c.user_id AND rol='user' ORDER BY id DESC LIMIT 1) as ultima_intencion
            FROM clientes c
            ORDER BY c.ultimo_contacto DESC
        """).fetchall()
    return [dict(r) for r in rows]


def obtener_estadisticas() -> dict:
    """Estadísticas generales para el dashboard."""
    with get_conn() as conn:
        total_clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        total_mensajes = conn.execute("SELECT COUNT(*) FROM mensajes").fetchone()[0]
        por_canal = conn.execute(
            "SELECT canal, COUNT(DISTINCT user_id) as total FROM clientes GROUP BY canal"
        ).fetchall()
        intenciones = conn.execute(
            "SELECT intencion, COUNT(*) as total FROM mensajes WHERE rol='user' AND intencion IS NOT NULL GROUP BY intencion ORDER BY total DESC LIMIT 5"
        ).fetchall()
    return {
        "total_clientes": total_clientes,
        "total_mensajes": total_mensajes,
        "por_canal": [dict(r) for r in por_canal],
        "top_intenciones": [dict(r) for r in intenciones],
    }
