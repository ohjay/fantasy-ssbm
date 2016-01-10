from django.core.management.base import BaseCommand
from ...models import UserProfile

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not UserProfile.objects.filter(username="owenjow").exists():
            UserProfile.objects.create_superuser("owenjow", "owen@owen.com", "changethis")
