# Generated by Django 3.1 on 2020-12-13 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_remove_listing_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('ELECTRONICS', 'Electronics'), ('HOME_&_OFFICE', 'Home & Office'), ('TOYS', 'Toys'), ('FASHION', 'Fashion'), ('SPORTING_GOODS', 'Sporting Goods'), ('BABY_PRODUCTS', 'Baby Products'), ('OTHER', 'Other')], default='ELECTRONICS', max_length=20),
        ),
    ]
