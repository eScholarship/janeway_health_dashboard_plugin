import csv

from django.core.management.base import BaseCommand, CommandError

from journal.models import Journal
from plugins.health_dashboard.models import Category, JournalCategory
from utils.setting_handler import save_setting


class Command(BaseCommand):
    """Import journal data used by the dashboard"""
    help = "Import journal data used by the dashboard"

    def add_arguments(self, parser):
        parser.add_argument(
            "import_file", help="path to a csv file containing journal info", type=str
        )

    def update_frequency(self, journal, freq):
        save_setting(
            "plugin:health_dashboard",
            "publication_frequency",
            journal,
            freq
        )

    def handle(self, *args, **options):
        import_file = options.get("import_file")
        categories = [
            "Faculty Journal",
            "Graduate Student Journal",
            "Undergraduate",
            "Law Review",
            "Practitioner Journal",
            "Proceedings",
            "Non-Traditional Publication",
            "OJC Title",
        ]

        with open(import_file, mode="r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                print(row)
                if Journal.objects.filter(code=row["id"]):
                    j = Journal.objects.get(code=row["id"])
                    for c in categories:
                        if row[c].strip() == "TRUE":
                            category, _ = Category.objects.get_or_create(label=c)
                            JournalCategory.objects.get_or_create(
                                journal=j,
                                category=category
                            )
                    if "Campus Affiliation" in row:
                        category, _ = Category.objects.get_or_create(
                            label=row["Campus Affiliation"]
                        )
                        JournalCategory.objects.get_or_create(
                            journal=j,
                            category=category
                        )
                    if "Publication Frequency" in row:
                        freq = row["Publication Frequency"]
                        if "Yearly" in freq:
                            self.update_frequency(j, 1)
                        elif "Biannually" in freq:
                            self.update_frequency(j, 2)
                        elif "Triannually" in freq:
                            self.update_frequency(j, 3)
                        elif "Quarterly" in freq:
                            self.update_frequency(j, 4)
                else:
                    print(f"Journal not found {row['id']}")

