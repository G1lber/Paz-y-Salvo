import os
from django.apps import AppConfig
from django.contrib.auth import get_user_model


class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'

    def ready(self):
        import mainapp.models
        self._create_superuser()

    def _create_superuser(self):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        if username and password and not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                password=password,
                email=email
            )
    
    