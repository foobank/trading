# Generated by Django 5.1.4 on 2024-12-27 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TradeOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('market', models.CharField(max_length=20)),
                ('side', models.CharField(max_length=4)),
                ('volume', models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('order_type', models.CharField(default='limit', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='requested', max_length=20)),
            ],
        ),
    ]