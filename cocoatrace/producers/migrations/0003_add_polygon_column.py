from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("producers", "0002_remove_producer_eudr_justification_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "IF COL_LENGTH('producers_plot', 'polygon') IS NULL "
                "ALTER TABLE [producers_plot] ADD [polygon] nvarchar(max) NULL"
            ),
            reverse_sql=(
                "IF COL_LENGTH('producers_plot', 'polygon') IS NOT NULL "
                "ALTER TABLE [producers_plot] DROP COLUMN [polygon]"
            ),
        ),
    ]
