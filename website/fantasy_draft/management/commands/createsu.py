from django.core.management.base import BaseCommand
from ...models import UserProfile

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not UserProfile.objects.filter(username="admin").exists():
            UserProfile.objects.create_superuser("admin", "admin@admin.com", "admin")
