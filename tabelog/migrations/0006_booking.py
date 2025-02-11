# Generated by Django 4.2.11 on 2025-01-12 12:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tabelog', '0005_customuser_favorite_shop'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateField(verbose_name='予約日')),
                ('booking_time', models.TimeField(verbose_name='予約時間')),
                ('head_count', models.IntegerField(verbose_name='予約人数')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tabelog.shop')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
