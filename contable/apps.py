from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class ContableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contable'

    def ready(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore
        from django_apscheduler import util
        from contable.tasks import enviar_vencimientos_email

        try:
            scheduler = BackgroundScheduler(timezone="America/Asuncion")
            scheduler.add_jobstore(DjangoJobStore(), "default")

            # Tarea diaria
            scheduler.add_job(
                enviar_vencimientos_email,
                trigger='cron',
                hour=7,
                minute=0,
                id="enviar_vencimientos_email",
                replace_existing=True,
            )

            scheduler.start()
        except (OperationalError, ProgrammingError):
            # Esto evita errores si la tabla aún no existe
            pass
