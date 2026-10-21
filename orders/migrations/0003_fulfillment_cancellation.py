from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0002_payment_chat")]

    operations = [
        migrations.AddField(model_name="order", name="cancellation_reason", field=models.TextField(blank=True, default="")),
        migrations.AddField(model_name="order", name="fulfillment_method", field=models.CharField(max_length=12, choices=[("delivery", "Entrega"), ("pickup", "Retirada"), ("arrange", "A combinar")], default="arrange")),
    ]
