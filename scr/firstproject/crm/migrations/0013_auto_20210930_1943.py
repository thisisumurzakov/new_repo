# Generated by Django 3.2.3 on 2021-09-30 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0012_auto_20210929_0235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='car_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='crm.cars'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orders',
            name='client_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='crm.clients'),
            preserve_default=False,
        ),
    ]
