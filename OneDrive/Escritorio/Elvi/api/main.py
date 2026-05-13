"""
SERVIDOR PRINCIPAL — FastAPI
Recibe webhooks de Meta y los procesa con los agentes separados por canal.
"""
from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from database.db import init_db, obtener_todos_los_clientes, obtener_conversacion, obtener_estadisticas
from agents.orchestrator import procesar_mensaje
from agents.instagram_agent import procesar_instagram
from agents.messenger_agent import procesar_messenger
import json
from api.meta_webhook import (
    verificar_webhook,
    verificar_firma,
    detectar_canal,
    extraer_mensaje_whatsapp,
    extraer_mensaje_instagram,
    extraer_mensaje_messenger,
)
from api.meta_client import enviar_mensaje, enviar_documento_whatsapp, enviar_imagen_whatsapp
from config.settings import WEBHOOK_BASE_URL

app = FastAPI(
    title="Elvi — Sistema Multi-Agente de Ventas",
    description="Automatización de ventas por WhatsApp, Instagram y Messenger",
    version="2.0.0",
)

@app.on_event("startup")
async def startup():
    init_db()

# Servir directorios estáticos solo si existen
import os
for _dir, _name, _opts in [
    ("paquetes", "paquetes", {}),
    ("referencias", "referencias", {}),
    ("privacy-policy", "privacy-policy", {"html": True}),
]:
    if os.path.isdir(_dir):
        app.mount(f"/{_name}", StaticFiles(directory=_dir, **_opts), name=_name)


# ====================================================================
# VERIFICACIÓN DEL WEBHOOK
# ====================================================================
@app.get("/webhook")
async def verificar(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    return PlainTextResponse(
        verificar_webhook(hub_mode, hub_verify_token, hub_challenge)
    )


# ====================================================================
# RECEPCIÓN DE MENSAJES
# ====================================================================
@app.post("/webhook")
async def recibir_mensaje(request: Request):
    raw = await request.body()
    firma = request.headers.get("x-hub-signature-256", "")
    if not verificar_firma(raw, firma):
        print(f"[META-WEBHOOK] Firma HMAC inválida — solicitud rechazada")
        return JSONResponse({"status": "forbidden"}, status_code=403)

    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        return JSONResponse({"status": "ok", "msg": "json inválido"})

    canal = detectar_canal(body)

    try:
        # ── WHATSAPP ─────────────────────────────────────────────────────
        if canal == "whatsapp":
            datos = extraer_mensaje_whatsapp(body)
            if not datos:
                return JSONResponse({"status": "ok", "msg": "sin mensaje"})

            user_id, recipient_id, mensaje = datos
            resultado = procesar_mensaje(user_id, mensaje, "whatsapp")
            respuesta = resultado["respuesta"]
            pdf = resultado.get("pdf")
            imagenes = resultado.get("imagenes", [])

            resultado_envio = await enviar_mensaje("whatsapp", recipient_id, respuesta)
            print(f"[META-SEND] {resultado_envio}")

            if pdf:
                from urllib.parse import quote
                url_pdf = f"{WEBHOOK_BASE_URL}/paquetes/{quote(pdf)}"
                await enviar_documento_whatsapp(
                    recipient_id, url_pdf, pdf,
                    caption="🤍 Aquí tienes nuestro PDF de paquetes ✨"
                )

            for ruta in imagenes:
                partes = ruta.replace("\\", "/").split("/")
                url_img = f"{WEBHOOK_BASE_URL}/" + "/".join(partes)
                await enviar_imagen_whatsapp(recipient_id, url_img)

        # ── INSTAGRAM ────────────────────────────────────────────────────
        elif canal == "instagram":
            datos = extraer_mensaje_instagram(body)
            if not datos:
                return JSONResponse({"status": "ok", "msg": "sin mensaje"})

            user_id, recipient_id, mensaje = datos
            respuesta = procesar_instagram(user_id, mensaje)
            await enviar_mensaje("instagram", recipient_id, respuesta)

        # ── MESSENGER ────────────────────────────────────────────────────
        elif canal == "messenger":
            datos = extraer_mensaje_messenger(body)
            if not datos:
                return JSONResponse({"status": "ok", "msg": "sin mensaje"})

            user_id, recipient_id, mensaje = datos
            respuesta = procesar_messenger(user_id, mensaje)
            await enviar_mensaje("messenger", recipient_id, respuesta)

        else:
            return JSONResponse({"status": "ok", "msg": "canal desconocido"})

    except Exception as e:
        print(f"[ERROR] {canal}: {e}")
        return JSONResponse({"status": "error", "msg": str(e)}, status_code=200)

    return JSONResponse({"status": "ok", "canal": canal})


# ====================================================================
# ENDPOINTS DE UTILIDAD
# ====================================================================
@app.get("/")
async def root():
    return {"mensaje": "Elvi — Sistema Multi-Agente v2.0 activo ✅"}


# ====================================================================
# PANEL DE ADMINISTRACIÓN
# ====================================================================
@app.get("/admin")
async def panel_admin():
    from fastapi.responses import HTMLResponse
    stats = obtener_estadisticas()
    clientes = obtener_todos_los_clientes()

    filas = ""
    for c in clientes:
        ultimo = (c["ultimo_mensaje"] or "")[:60]
        canal_emoji = {"whatsapp": "💬", "instagram": "📸", "messenger": "💙"}.get(c["canal"], "📱")
        filas += f"""
        <tr onclick="window.location='/admin/chat/{c['user_id']}'" style="cursor:pointer">
            <td>{canal_emoji} {c['canal']}</td>
            <td>{c['user_id']}</td>
            <td>{c['total_mensajes']}</td>
            <td>{c['ultima_intencion'] or '-'}</td>
            <td>{ultimo}</td>
            <td>{c['ultimo_contacto'][:16]}</td>
        </tr>"""

    por_canal = " | ".join([f"{r['canal']}: {r['total']}" for r in stats["por_canal"]])

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Elvi Memories — Panel</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 0; background: #f8f4f0; color: #333; }}
  header {{ background: #2d2d2d; color: white; padding: 20px 30px; }}
  header h1 {{ margin: 0; font-size: 22px; }}
  header p {{ margin: 5px 0 0; opacity: 0.7; font-size: 13px; }}
  .stats {{ display: flex; gap: 20px; padding: 20px 30px; flex-wrap: wrap; }}
  .stat {{ background: white; border-radius: 12px; padding: 20px 30px; min-width: 150px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .stat h2 {{ margin: 0; font-size: 36px; color: #c8956c; }}
  .stat p {{ margin: 5px 0 0; font-size: 13px; color: #888; }}
  .tabla-wrap {{ padding: 0 30px 30px; }}
  table {{ width: 100%; background: white; border-radius: 12px; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; }}
  th {{ background: #2d2d2d; color: white; padding: 12px 16px; text-align: left; font-size: 13px; }}
  td {{ padding: 12px 16px; border-bottom: 1px solid #f0ece8; font-size: 13px; }}
  tr:hover td {{ background: #fdf6f0; }}
  tr:last-child td {{ border-bottom: none; }}
  .badge {{ background: #f0ece8; padding: 2px 8px; border-radius: 20px; font-size: 11px; }}
</style>
</head><body>
<header>
  <h1>🤍 Elvi Memories — Panel de Conversaciones</h1>
  <p>{por_canal}</p>
</header>
<div class="stats">
  <div class="stat"><h2>{stats['total_clientes']}</h2><p>Clientes</p></div>
  <div class="stat"><h2>{stats['total_mensajes']}</h2><p>Mensajes totales</p></div>
  {''.join([f'<div class="stat"><h2>{r["total"]}</h2><p>{r["intencion"]}</p></div>' for r in stats["top_intenciones"]])}
</div>
<div class="tabla-wrap">
  <table>
    <thead><tr><th>Canal</th><th>Cliente</th><th>Mensajes</th><th>Última intención</th><th>Último mensaje</th><th>Fecha</th></tr></thead>
    <tbody>{filas if filas else '<tr><td colspan="6" style="text-align:center;padding:40px;color:#aaa">Sin conversaciones aún</td></tr>'}</tbody>
  </table>
</div>
</body></html>"""
    return HTMLResponse(html)


@app.get("/admin/chat/{user_id}")
async def ver_chat(user_id: str):
    from fastapi.responses import HTMLResponse
    mensajes = obtener_conversacion(user_id, limite=100)

    burbujas = ""
    for m in mensajes:
        es_usuario = m["rol"] == "user"
        alineacion = "flex-start" if es_usuario else "flex-end"
        color = "#f0ece8" if es_usuario else "#2d2d2d"
        texto_color = "#333" if es_usuario else "white"
        etiqueta = f'<span style="font-size:10px;opacity:0.5;display:block;margin-bottom:3px">{"Cliente" if es_usuario else "Elvi Bot"} — {m["timestamp"][:16]}</span>'
        intencion = f'<span style="font-size:10px;background:#c8956c;color:white;padding:1px 6px;border-radius:10px;margin-left:6px">{m["intencion"]}</span>' if m.get("intencion") and es_usuario else ""
        burbujas += f"""
        <div style="display:flex;justify-content:{alineacion};margin:8px 0">
          <div style="max-width:70%;background:{color};color:{texto_color};padding:12px 16px;border-radius:16px;font-size:14px;line-height:1.5">
            {etiqueta}{m['contenido']}{intencion}
          </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Chat — {user_id}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 0; background: #f8f4f0; }}
  header {{ background: #2d2d2d; color: white; padding: 16px 24px; display:flex; align-items:center; gap:16px; }}
  a {{ color: #c8956c; text-decoration: none; }}
  .chat {{ padding: 20px 30px; max-width: 800px; margin: 0 auto; }}
</style>
</head><body>
<header>
  <a href="/admin">← Volver</a>
  <span>💬 Conversación con {user_id}</span>
</header>
<div class="chat">
  {burbujas if burbujas else '<p style="text-align:center;color:#aaa;margin-top:60px">Sin mensajes</p>'}
</div>
</body></html>"""
    return HTMLResponse(html)


@app.post("/sms")
async def recibir_sms_twilio(request: Request):
    """Recibe SMS entrantes de Twilio — muestra el código de verificación de Meta."""
    form = await request.form()
    remitente = form.get("From", "desconocido")
    cuerpo = form.get("Body", "")
    print(f"\n{'='*50}")
    print(f"📱 SMS recibido de: {remitente}")
    print(f"💬 Contenido: {cuerpo}")
    print(f"{'='*50}\n")
    return PlainTextResponse(
        '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )


@app.post("/test")
async def test_agente(request: Request):
    """Prueba los agentes sin pasar por Meta."""
    body = await request.json()
    mensaje = body.get("mensaje", "Hola")
    canal = body.get("canal", "whatsapp")
    user_id = body.get("user_id", "test_user")

    if canal == "whatsapp":
        return procesar_mensaje(user_id, mensaje, canal)
    elif canal == "instagram":
        return {"respuesta": procesar_instagram(user_id, mensaje)}
    elif canal == "messenger":
        return {"respuesta": procesar_messenger(user_id, mensaje)}
    return {"error": "canal no válido"}


if __name__ == "__main__":
    import uvicorn
    from config.settings import PORT
    uvicorn.run("api.main:app", host="0.0.0.0", port=PORT, reload=True)
