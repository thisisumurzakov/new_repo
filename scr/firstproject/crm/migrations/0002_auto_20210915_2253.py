# Generated by Django 3.2.3 on 2021-09-15 17:53

import crm.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='bot_token',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.CreateModel(
            name='ClientsFromTg',
            fields=[
                ('client_id', models.AutoField(auto_created=True, primary_key=True, serialize=False, unique=True)),
                ('passport_series', models.CharField(max_length=10, unique=True)),
                ('firstname', models.CharField(max_length=150)),
                ('lastname', models.CharField(max_length=150)),
                ('second_name', models.CharField(max_length=150)),
                ('date_of_birth', models.DateField()),
                ('date_of_issue', models.DateField()),
                ('issued', models.CharField(max_length=250)),
                ('address', models.CharField(max_length=250)),
                ('phone', models.CharField(max_length=20)),
                ('photo', models.ImageField(blank=True, null=True, upload_to=crm.models.clients_dir_path)),
                ('chat_id', models.CharField(max_length=20)),
                ('rent_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.rent')),
            ],
            options={
                'verbose_name': 'ClientFromTg',
                'verbose_name_plural': 'ClientsFromTg',
            },
        ),
    ]