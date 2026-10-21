from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("orders", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name="order", name="payment_status", field=models.CharField(choices=[("pending", "A combinar"), ("agreed", "Pagamento combinado"), ("paid", "Pagamento confirmado")], default="pending", max_length=12)),
        migrations.AddField(model_name="order", name="payment_method", field=models.CharField(blank=True, max_length=60)),
        migrations.CreateModel(name="Conversation", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("created_at", models.DateTimeField(auto_now_add=True)), ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="customer_conversations", to=settings.AUTH_USER_MODEL)), ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="received_conversations", to=settings.AUTH_USER_MODEL)), ("order", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="conversations", to="orders.order"))]),
        migrations.CreateModel(name="Message", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("content", models.TextField(max_length=3000)), ("created_at", models.DateTimeField(auto_now_add=True)), ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="orders.conversation")), ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL))], options={"ordering": ["created_at", "id"]}),
    ]
