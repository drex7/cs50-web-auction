# Generated by Django 3.1 on 2020-11-28 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_auto_20201125_1046'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='user',
            new_name='created_by',
        ),
        migrations.AlterField(
            model_name='listing',
            name='starting_bid',
            field=models.IntegerField(),
        ),
    ]
