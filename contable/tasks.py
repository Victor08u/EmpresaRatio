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

    # Si no hay vencimientos
    if not vencimientos.exists():
        vencimientos_html = "<p style='color:#555;'>✅ No hay vencimientos pendientes para este mes.</p>"
    else:
        vencimientos_html = ""
        for v in vencimientos:
            vencimientos_html += f"""
            <div style="background:#f9f9f9; 
                        border:1px solid #ddd; 
                        border-radius:8px; 
                        padding:15px; 
                        margin-bottom:12px;
                        font-family:Arial, sans-serif;">
                <p style="margin:0; font-size:16px;">
                    <strong>Cliente:</strong> {v.cliente}
                </p>
                <p style="margin:0; font-size:16px;">
                    <strong>Documento:</strong> {v.tipo_documento}
                </p>
                <p style="margin:0; font-size:16px; color:#d9534f;">
                    <strong>Fecha de vencimiento:</strong> {v.fecha_vencimiento.strftime('%d/%m/%Y')}
                </p>
            </div>
            """

    # Plantilla HTML del correo
    contenido_html = f"""
    <html>
      <body style="font-family:Arial, sans-serif; background:#f4f6f9; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
          
          <!-- Encabezado -->
          <div style="background:#2575fc; padding:20px; text-align:center; color:white;">
            <h1 style="margin:0; font-size:22px;">📊 Vencimientos de Clientes</h1>
            <p style="margin:0;">Periodo: {hoy.strftime('%m/%Y')}</p>
          </div>

          <!-- Contenido -->
          <div style="padding:20px;">
            <h2 style="color:#333; font-size:18px;">Detalle de vencimientos:</h2>
            {vencimientos_html}
          </div>

          <!-- Footer -->
          <div style="background:#f4f6f9; padding:15px; font-size:12px; color:#555; text-align:center;">
            <p><strong>Confidencialidad:</strong> Este correo y sus archivos adjuntos son confidenciales y dirigidos exclusivamente a su destinatario. Si usted ha recibido este mensaje por error, notifíquelo inmediatamente y elimínelo.</p>
          </div>
        </div>
      </body>
    </html>
    """

    # Crear mensaje
    msg = EmailMessage()
    msg['Subject'] = f"📅 Vencimientos de clientes - {hoy.strftime('%m/%Y')}"
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = "victor.morinigo06@unae.edu.py"  # destinatarios
    msg.set_content("Este correo requiere un cliente que soporte HTML.")  # fallback de texto
    msg.add_alternative(contenido_html, subtype="html")

    # ⚠️ Ignorar verificación SSL (solo para desarrollo)
    context = ssl._create_unverified_context()

    # Conectar con Gmail y enviar
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        smtp.send_message(msg)

    print("📧 Correo de vencimientos enviado correctamente ✅")
    