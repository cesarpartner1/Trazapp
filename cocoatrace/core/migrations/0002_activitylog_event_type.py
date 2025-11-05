from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="activitylog",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("create", "Creación"),
                    ("update", "Actualización"),
                    ("delete", "Eliminación"),
                ],
                default="create",
                max_length=20,
            ),
        ),
    ]
