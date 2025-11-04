# Generated manually to align centroid columns with existing SQL Server schema

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producers", "0004_alter_plot_polygon"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "IF COL_LENGTH('producers_plot', 'centroid_lat') IS NULL "
                        "    ALTER TABLE [producers_plot] ADD [centroid_lat] float NOT NULL DEFAULT 0"
                    ),
                    reverse_sql=(
                        "IF COL_LENGTH('producers_plot', 'centroid_lat') IS NOT NULL "
                        "    ALTER TABLE [producers_plot] DROP COLUMN [centroid_lat]"
                    ),
                ),
                migrations.RunSQL(
                    sql=(
                        "IF COL_LENGTH('producers_plot', 'centroid_lng') IS NULL "
                        "    ALTER TABLE [producers_plot] ADD [centroid_lng] float NOT NULL DEFAULT 0"
                    ),
                    reverse_sql=(
                        "IF COL_LENGTH('producers_plot', 'centroid_lng') IS NOT NULL "
                        "    ALTER TABLE [producers_plot] DROP COLUMN [centroid_lng]"
                    ),
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="plot",
                    name="centroid_lat",
                    field=models.FloatField(default=0),
                ),
                migrations.AddField(
                    model_name="plot",
                    name="centroid_lng",
                    field=models.FloatField(default=0),
                ),
            ],
        ),
    ]
