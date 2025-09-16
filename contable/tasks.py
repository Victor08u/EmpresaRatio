# contable/tasks.py
from datetime import date
import smtplib
from email.message import EmailMessage
from django.conf import settings
from contable.models import VencimientoConta
import ssl

def enviar_vencimientos_email():
    hoy = date.today()

    # Filtrar vencimientos del mes actual que aún no fueron notificados
    vencimientos = VencimientoConta.objects.filter(
        fecha_vencimiento__month=hoy.month,
        fecha_vencimiento__year=hoy.year,
        notificado=False
    )

    # Crear contenido del correo
    if not vencimientos.exists():
        contenido = "No hay vencimientos pendientes para este mes."
    else:
        contenido = "Vencimientos de clientes para este mes:\n\n"
        for v in vencimientos:
            contenido += f"- {v.cliente}: {v.tipo_documento}, vence el {v.fecha_vencimiento.strftime('%d/%m/%Y')}\n"

    # Crear mensaje
    msg = EmailMessage()
    msg['Subject'] = f"Vencimientos de clientes - {hoy.strftime('%m/%Y')}"
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = "victor.morinigo06@unae.edu.py"  # puedes poner lista de destinatarios
    msg.set_content(contenido)

    # ⚠️ Ignorar verificación SSL (solo para desarrollo)
    context = ssl._create_unverified_context()

    # Conectar con Gmail y enviar
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        smtp.send_message(msg)

    print("Correo de vencimientos enviado correctamente ✅")
