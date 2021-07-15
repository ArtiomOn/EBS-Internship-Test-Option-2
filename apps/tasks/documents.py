from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import (
    Document,
    fields,
    TextField,
)

from apps.tasks.models import Task

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


@registry.register_document
class TaskDocument(Document):
    class Index:
        name = 'task'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django(object):
        id = fields.IntegerField(attr='id')

        model = Task

        fields = {
            'title': TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.TextField(analyzer='keyword'),
                }
            ),
            'description': TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.TextField(analyzer='keyword'),
                }
            ),
        }
