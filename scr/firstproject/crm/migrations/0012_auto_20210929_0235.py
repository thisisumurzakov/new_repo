# Generated by Django 3.2.3 on 2021-09-28 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0011_alter_cars_year_of_issue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinformation',
            name='from_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderinformation',
            name='from_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
