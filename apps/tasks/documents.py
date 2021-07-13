from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import Index, Document, fields

from apps.tasks.models import Task

html_strip = analyzer(
    'html_strip',
    tokenize='standard',
    filter=['standard', 'lowercase', 'stop', 'snowball'],
    char_filter=['html_strip']
)
#
posts = Index('tasks')


@registry.register_document
@posts.document
class TaskDocument(Document):
    """Task elasticsearch document"""

    class Index:
        name = 'tasks'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Task
        id = fields.IntegerField(attr='id')
        title = fields.TextField(
            analyzer=html_strip,
            fields={
                'raw': fields.TextField(analyzer='keyword'),
            }
        )
        description = fields.TextField(
            analyzer=html_strip,
            fields={
                'raw': fields.TextField(analyzer='keyword'),
            }
        )
