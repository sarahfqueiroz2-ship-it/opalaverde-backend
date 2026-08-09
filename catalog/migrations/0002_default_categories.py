from django.db import migrations


DEFAULT_CATEGORIES = [
    ("Folhas Verdes", "folhas"),
    ("Legumes", "legumes"),
    ("Frutas", "frutas"),
    ("Ervas Aromáticas", "ervas"),
    ("Raízes", "raizes"),
]


def create_default_categories(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    for name, slug in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(slug=slug, defaults={"name": name})


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    slugs = [slug for _, slug in DEFAULT_CATEGORIES]
    Category.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]
