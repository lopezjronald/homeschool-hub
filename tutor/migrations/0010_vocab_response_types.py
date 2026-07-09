# Hand-authored: adds the matching / fill-blank vocabulary response types.
# Choices-only change — state update, no schema SQL.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0009_alter_question_passage_alter_question_response_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='response_type',
            field=models.CharField(choices=[('text', 'Typed answer'), ('markup', 'Mark up the sentence (draw)'), ('characters', 'A box per character'), ('matching', 'Match words to numbered definitions'), ('fill_blank', 'Fill in the blank from a word bank')], default='text', max_length=10),
        ),
    ]
