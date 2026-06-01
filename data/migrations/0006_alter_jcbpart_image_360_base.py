# Generated migration to change image_360_base to CloudinaryField

from django.db import migrations
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_seed_vendors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jcbpart',
            name='image_360_base',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
