from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.AUTH_USER_MODEL.objects.filter(username="admin").exists():
            settings.AUTH_USER_MODEL.objects.create_superuser("admin", "admin@admin.com", "admin")
