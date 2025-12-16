from django.core.management.base import BaseCommand
from main.models import FoodItem
from restaurants.models import Restaurant


class Command(BaseCommand):
    help = "Fix FoodItem.restaurant values that are strings instead of Restaurant objects"

    def handle(self, *args, **kwargs):
        fixed = 0
        not_found = 0

        for f in FoodItem.objects.all():
            value = f.restaurant

            # Case 1: restaurant stored incorrectly as a string
            if isinstance(value, str):
                try:
                    r = Restaurant.objects.get(name=value)
                    f.restaurant = r
                    f.save()
                    fixed += 1
                    self.stdout.write(self.style.SUCCESS(f"✔ Updated: {f.name} -> {r.name}"))
                except Restaurant.DoesNotExist:
                    not_found += 1
                    self.stdout.write(self.style.WARNING(f"⚠ No Restaurant found for '{value}' (Food: {f.name})"))

            # Case 2: invalid type (neither string nor Restaurant)
            elif not isinstance(value, Restaurant):
                not_found += 1
                self.stdout.write(self.style.WARNING(
                    f"⚠ Invalid type for {f.name}: {value}"
                ))

        self.stdout.write("\n----- SUMMARY -----")
        self.stdout.write(f"Fixed: {fixed}")
        self.stdout.write(f"Not Fixed (Errors): {not_found}")
        self.stdout.write("-------------------")