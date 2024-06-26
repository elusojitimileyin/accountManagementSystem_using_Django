# Generated by Django 5.0.6 on 2024-06-13 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='account_type',
            field=models.CharField(choices=[('S', 'SAVINGS'), ('C', 'CURRENT'), ('D', 'DOM')], default='S', max_length=1),
        ),
    ]