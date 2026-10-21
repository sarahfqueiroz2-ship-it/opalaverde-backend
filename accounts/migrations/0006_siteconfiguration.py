from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("accounts", "0005_user_avatar")]
    operations = [migrations.CreateModel(name="SiteConfiguration", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("site_name", models.CharField(default="OpalaVerde", max_length=100)),
        ("tagline", models.CharField(blank=True, max_length=180)),
        ("description", models.TextField(blank=True)),
        ("contact_email", models.EmailField(blank=True, max_length=254)),
        ("contact_phone", models.CharField(blank=True, max_length=30)),
        ("address", models.CharField(blank=True, max_length=255)),
        ("updated_at", models.DateTimeField(auto_now=True)),
    ])]
