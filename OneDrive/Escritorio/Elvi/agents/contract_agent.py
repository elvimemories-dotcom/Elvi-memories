"""
AGENTE 4 — CONTRACT AGENT (Elvi Memories)
Genera el contrato PDF con los datos del cliente y lo envia por email.
"""
import os
import smtplib
import anthropic
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fpdf import FPDF
from config.settings import ANTHROPIC_API_KEY, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ====================================================================
# DATOS FIJOS DEL NEGOCIO
# ====================================================================
NEGOCIO = {
    "nombre_fotografa": "Luisa Fernanda Villanueva",
    "studio": "Elvi Memories",
    "telefono": "678.765.9231",
    "direccion": "76 Stonehurst Way SW, Lawrenceville, GA 30044",
    "email": "elvimemories@gmail.com",
}

SYSTEM_PROMPT = """Eres Elvi, coordinadora de Elvi Memories. Cuando el deposito del cliente
fue confirmado, tu tarea es recopilar los datos que falten para generar el contrato:
- Nombre completo del cliente
- Correo electronico
- Telefono
- Paquete elegido y descripcion
- Precio total acordado
- Fecha y hora de la sesion

Si ya tienes todos los datos, confirma al cliente que el contrato sera enviado a su email.
Tono: calido, profesional. Mensajes cortos."""


FONT_DIR = r"C:\Windows\Fonts"

class ContratoElviPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Arial", "", f"{FONT_DIR}\\arial.ttf")
        self.add_font("Arial", "B", f"{FONT_DIR}\\arialbd.ttf")
        self.add_font("Arial", "I", f"{FONT_DIR}\\ariali.ttf")

    def header(self):
        self.set_font("Arial", "B", 16)
        self.set_text_color(80, 50, 100)
        self.cell(0, 10, "Contrato de Fotografía", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Arial", "I", 11)
        self.set_text_color(120, 80, 140)
        self.cell(0, 7, "Autorización de toma de fotos", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-20)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, "Elvi Memories | elvimemories@gmail.com | 678.765.9231", align="C")


def generar_contrato_pdf(
    nombre_cliente: str,
    fecha_sesion: str,
    hora_sesion: str,
    telefono_cliente: str,
    email_cliente: str,
    descripcion_paquete: str,
    precio_total: float,
    deposito: float = 50.0,
) -> str:
    """
    Genera el PDF del contrato y lo guarda en contratos/.
    Retorna la ruta del archivo generado.
    """
    saldo_restante = precio_total - deposito

    pdf = ContratoElviPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    def campo(etiqueta, valor):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(55, 7, etiqueta + ":", new_x="RIGHT", new_y="LAST")
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, valor, new_x="LMARGIN", new_y="NEXT")

    # Intro
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, "El presente contrato nos permite y autoriza tomar fotografias para la siguiente cliente.")
    pdf.ln(3)

    campo("Nombre de Cliente", nombre_cliente)
    campo("Direccion del estudio", NEGOCIO["direccion"])
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "(Nuestro studio esta ubicado en casa residencial, gracias por tu comprension)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    campo("Fecha y Hora", f"{fecha_sesion} a las {hora_sesion}")
    campo("Numero telefonico", telefono_cliente)
    campo("Correo electronico", email_cliente)
    pdf.ln(4)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7,
        f"En virtud de la celebracion del presente contrato, me permite a mi "
        f"{NEGOCIO['nombre_fotografa']} y a mi equipo realizar la cobertura fotografica "
        f"para el cliente en la fecha y lugar acordado para la sesion de fotografia."
    )
    pdf.ln(5)

    # Precio
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(80, 50, 100)
    pdf.cell(0, 8, "Precio y forma de pago.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 11)

    pdf.multi_cell(0, 7,
        f"El Cliente realizara el pago total por el servicio: ${precio_total:.0f} USD, "
        f"el cual realizara en dos partes."
    )
    pdf.ln(2)
    pdf.multi_cell(0, 7,
        f"a) El cliente agendo la sesion fotografica con un deposito de ${deposito:.0f} USD "
        f"que se restaran al valor total. (este deposito fue cancelado al momento de reservar)"
    )
    pdf.ln(2)
    pdf.multi_cell(0, 7,
        f"b) El pago restante de ${saldo_restante:.0f} USD se debera cancelar una vez "
        f"finalicemos la sesion de fotos."
    )
    pdf.ln(2)
    pdf.multi_cell(0, 7,
        "c) Por cualquier motivo por el que se decida cancelar la sesion por parte del cliente, "
        "el deposito no sera reembolsado, ya que este deposito guarda un espacio exclusivo para "
        "usted que puede ser utilizado por otro cliente."
    )
    pdf.ln(5)

    # Terminos
    terminos = [
        "El material sera entregado a la clienta en 5 dias habiles a la sesion fotografica.",
        "d) Puntualidad: El cliente se compromete a llegar puntualmente. En caso de retraso, "
        "se aplicara un recargo de $20 USD por cada 10 minutos de tardanza.",
        "e) Las fotografias realizadas por Elvi Memories son propiedad del fotografo y podran "
        "ser usadas con fines promocionales en redes sociales y portafolio. En caso de "
        "exclusividad puede comunicarselo al fotografo con costo adicional.",
        "f) Todas las fotografias tomadas seran enviadas con marca de agua para que puedas "
        "seleccionar tus favoritas. Recibiras las fotografias finales editadas segun el paquete "
        "elegido, en alta calidad y sin marca de agua.",
        "g) Tendras acceso a tu album digital durante 3 meses a partir de la fecha de entrega. "
        "Te recomendamos descargar tus fotografias dentro de este plazo.",
    ]
    for t in terminos:
        pdf.multi_cell(0, 7, t)
        pdf.ln(2)

    # Paquete elegido
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(80, 50, 100)
    pdf.cell(0, 8, "Paquete elegido por el cliente:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, descripcion_paquete)
    pdf.ln(10)

    # Firma
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, "Firma del cliente:", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.line(20, pdf.get_y(), 100, pdf.get_y())
    pdf.ln(10)

    # Info fotografa
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, f"Sra. {NEGOCIO['nombre_fotografa']}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, f"Telefono: {NEGOCIO['telefono']}  |  {NEGOCIO['direccion']}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Correo: {NEGOCIO['email']}", align="R", new_x="LMARGIN", new_y="NEXT")

    # Guardar
    os.makedirs("contratos", exist_ok=True)
    nombre_archivo = f"contratos/contrato_{nombre_cliente.replace(' ', '_')}.pdf"
    pdf.output(nombre_archivo)
    return nombre_archivo


def enviar_contrato_email(
    email_cliente: str,
    nombre_cliente: str,
    ruta_pdf: str,
    fecha_sesion: str,
    hora_sesion: str,
) -> bool:
    """Envia el contrato PDF al cliente y una copia al negocio."""
    if not SMTP_PASS:
        print("[CONTRATO] SMTP_PASS no configurado")
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = email_cliente
        msg["Subject"] = "Contrato de Sesion Fotografica - Elvi Memories"

        cuerpo = (
            f"Hola {nombre_cliente},\n\n"
            f"Muchas gracias por confiar en Elvi Memories.\n"
            f"Adjunto encontraras tu contrato para la sesion fotografica del "
            f"{fecha_sesion} a las {hora_sesion}.\n\n"
            f"Tu deposito de $50 USD ya fue recibido y tu fecha esta confirmada "
            f"y reservada exclusivamente para ti.\n\n"
            f"El dia de tu sesion recuerda llegar puntualmente. "
            f"Si tienes alguna duda estamos disponibles por WhatsApp al +16787659231.\n\n"
            f"Con carino,\nLuisa Fernanda Villanueva\nElvi Memories\n"
            f"678.765.9231 | elvimemories@gmail.com"
        )
        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

        with open(ruta_pdf, "rb") as f:
            adjunto = MIMEApplication(f.read(), _subtype="pdf")
            adjunto.add_header(
                "Content-Disposition",
                "attachment",
                filename=f"Contrato_ElviMemories_{nombre_cliente.replace(' ', '_')}.pdf"
            )
            msg.attach(adjunto)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"[CONTRATO] Enviado a {email_cliente}")
        return True

    except Exception as e:
        print(f"[CONTRATO] Error: {e}")
        return False


def preparar_contrato(mensaje: str, historial: list = None) -> dict:
    """Responde al cliente cuando el deposito fue confirmado."""
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

    return {"respuesta": texto, "accion": "solicitar_datos_contrato"}


def generar_mensaje_post_contrato(nombre: str, paquete: str) -> str:
    """Mensaje para enviar por WhatsApp despues de enviar el contrato."""
    return (
        f"Hola {nombre}! Te acabo de enviar el contrato de tu sesion de *{paquete}* "
        f"a tu correo. Por favor revisalo con atencion. "
        f"Tu fecha esta 100% reservada. Cualquier duda aqui estamos. "
    )
