from .query_text import (
    create,
    insert,
    query_data_bm25,
    query_fetch_object_by_id,
    query_fetch_objects,
    query_hybrid,
    query_near_object,
    query_data_near_text,
    query_data_near_vector,
)
from langtrace_python_sdk import with_langtrace_root_span


class WeaviateRunner:
    @with_langtrace_root_span("Weaviate")
    def run(self):
        create()
        insert()
        query_data_bm25()
        # query_fetch_object_by_id()
        # query_fetch_objects()
        # query_hybrid()
        # query_near_object()
        # query_data_near_text()
        # query_data_near_vector()
