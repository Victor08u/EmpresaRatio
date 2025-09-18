from django.core.management.base import BaseCommand
from contable.tasks import enviar_vencimientos_email


class Command(BaseCommand):
    help = 'Enviar correos de vencimientos'

    def handle(self, *args, **kwargs):
        enviar_vencimientos_email()
        self.stdout.write(self.style.SUCCESS('Correo de vencimientos enviado correctamente.'))
