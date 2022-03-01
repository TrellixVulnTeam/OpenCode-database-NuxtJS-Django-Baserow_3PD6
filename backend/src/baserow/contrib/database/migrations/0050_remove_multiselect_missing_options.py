# Generated by Django 3.2.6 on 2021-12-03 09:09

from django.db import migrations, connection, transaction


# noinspection PyPep8Naming
def forward(apps, schema_editor):
    batch_size = 100
    SelectOption = apps.get_model("database", "SelectOption")
    MultipleSelectField = apps.get_model("database", "MultipleSelectField")

    option_table_name = SelectOption.objects.model._meta.db_table

    total = MultipleSelectField.objects.count()

    for start in range(0, total, batch_size):
        for field in MultipleSelectField.objects.all()[start : start + batch_size]:
            # Transaction by batch to avoid opening too many tables in same transaction
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # No SQL injection here so it's safe to use % operator
                    cursor.execute(
                        (
                            "DELETE FROM %(table)s "  # nosec
                            "WHERE %(select_column)s NOT IN "
                            "(SELECT id FROM %(option_table)s)"
                        )
                        % {
                            "select_column": (
                                f"multipleselectfield{field.id}selectoption_id"
                            ),
                            "table": f"database_multipleselect_{field.id}",
                            "option_table": option_table_name,
                        },
                    )


class Migration(migrations.Migration):

    dependencies = [
        ("database", "0049_urlfield_2_textfield"),
    ]

    operations = [
        # We disable transaction here to be able to manage it.
        migrations.RunPython(forward, migrations.RunPython.noop, atomic=False),
    ]
