# Generated by Django 3.2.14 on 2022-07-29 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('field_number', models.IntegerField(blank=True)),
                ('order_number', models.IntegerField(primary_key=True, serialize=False)),
                ('cost_in_dollars', models.IntegerField()),
                ('deliver_time', models.DateField(blank=True)),
                ('cost_in_rubles', models.DecimalField(decimal_places=2, max_digits=50)),
            ],
            options={
                'ordering': ('field_number',),
            },
        ),
    ]