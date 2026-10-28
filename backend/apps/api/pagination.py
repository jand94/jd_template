from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
    """Seitenantwort `{count, next, previous, results}` für Listen-Views."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
