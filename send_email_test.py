import smtplib
from email.message import EmailMessage

# Datos del correo
EMAIL_ADDRESS = "vmorinigo31@gmail.com"
EMAIL_PASSWORD = "nxoludpbghkaimak"  # App Password

msg = EmailMessage()
msg['Subject'] = "Correo de prueba honorarios"
msg['From'] = EMAIL_ADDRESS
msg['To'] = "victor.morinigo06@unae.edu.py"
msg.set_content("Este es un correo de prueba usando smtplib con SSL ignorado.")

# ⚠️ Ignorar verificación SSL
import ssl
context = ssl._create_unverified_context()

# Conectar y enviar
with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()
    smtp.starttls(context=context)
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)

print("Correo enviado correctamente ✅")
