# Generated by Django 3.2.3 on 2021-09-16 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_rent_url_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientsfromtg',
            name='photo',
            field=models.URLField(blank=True, null=True),
        ),
    ]
