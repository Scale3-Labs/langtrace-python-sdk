import asyncio
from .basic import search
from langtrace_python_sdk import with_langtrace_root_span


class Neo4jGraphRagRunner:
    @with_langtrace_root_span("Neo4jGraphRagRunner")
    def run(self):
        asyncio.run(search())
