import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Program


class Command(BaseCommand):
    help = "Load Dafara's six program introductions; preserve case links and images."

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(__file__).resolve().parents[2] / "data" / "dafara_programs.json"
        for record in json.loads(source.read_text()):
            slug = record.pop("slug")
            obj, created = Program.objects.update_or_create(
                slug=slug, defaults={**record, "published": True}
            )
            self.stdout.write(f"{'Created' if created else 'Updated'}: {obj.title}")
        # Retire only the unused original sample category. Keep real case pages accessible.
        community = Program.objects.filter(slug="community", title="Community support").first()
        if community and not community.case_set.exists():
            community.published = False
            community.save(update_fields=["published"])
        elif community and community.published:
            self.stdout.write(self.style.WARNING(
                "Community support retained because it has cases. Reassign them in management before unpublishing it."
            ))
        self.stdout.write(self.style.SUCCESS("Program content loaded. Cases, funding, and images preserved."))
