from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producers", "0005_add_centroid_fields"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "IF COL_LENGTH('producers_plot', 'centroid_lon') IS NULL "
                        "BEGIN "
                        "    IF COL_LENGTH('producers_plot', 'centroid_lng') IS NOT NULL "
                        "        EXEC sp_rename 'producers_plot.centroid_lng', 'centroid_lon', 'COLUMN'; "
                        "    ELSE "
                        "        ALTER TABLE [producers_plot] ADD [centroid_lon] float NOT NULL DEFAULT 0; "
                        "END"
                    ),
                    reverse_sql=(
                        "IF COL_LENGTH('producers_plot', 'centroid_lng') IS NULL "
                        "BEGIN "
                        "    IF COL_LENGTH('producers_plot', 'centroid_lon') IS NOT NULL "
                        "        EXEC sp_rename 'producers_plot.centroid_lon', 'centroid_lng', 'COLUMN'; "
                        "    ELSE "
                        "        ALTER TABLE [producers_plot] ADD [centroid_lng] float NOT NULL DEFAULT 0; "
                        "END"
                    ),
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="plot",
                    name="centroid_lng",
                    field=models.FloatField(default=0, db_column="centroid_lon"),
                ),
            ],
        ),
    ]
