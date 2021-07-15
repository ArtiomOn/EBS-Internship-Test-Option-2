from elasticsearch_dsl.query import Q, MultiMatch

from apps.tasks.documents import TaskDocument


def get_search_query(phrase):
    query = Q(
        'function_score',
        query=MultiMatch(
            fields=['title', 'description'],
            query=phrase
        ),
    )
    return TaskDocument.search().query(query)


def search(phrase):
    return get_search_query(phrase).to_queryset()
