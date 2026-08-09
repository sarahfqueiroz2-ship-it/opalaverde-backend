import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Cria (ou atualiza a senha de) um usuário administrador a partir das
    variáveis de ambiente ADMIN_EMAIL e ADMIN_PASSWORD.

    Feito para rodar automaticamente a cada deploy (via build.sh), já que
    planos gratuitos do Render não têm acesso a shell interativo — sem isso,
    não haveria como rodar `createsuperuser` manualmente.

    É seguro rodar toda vez: se o admin já existe, não faz nada (não some,
    não duplica, não estraga a senha que você já usa).
    """

    help = "Cria o superusuário admin a partir de ADMIN_EMAIL/ADMIN_PASSWORD (variáveis de ambiente)"

    def handle(self, *args, **options):
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "ADMIN_EMAIL/ADMIN_PASSWORD não configurados — pulando criação do admin."
                )
            )
            return

        User = get_user_model()

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Admin '{email}' já existe — nada a fazer."))
            return

        User.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            first_name="Administrador",
            user_type="admin",
        )
        self.stdout.write(self.style.SUCCESS(f"Admin '{email}' criado com sucesso!"))
