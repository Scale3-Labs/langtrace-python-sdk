import os
from langtrace_python_sdk import langtrace
from neo4j import GraphDatabase

langtrace.init()

def execute_query():
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"), 
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    )

    records, summary, keys = driver.execute_query(
        "MATCH (p:Person {age: $age}) RETURN p.name AS name",
        age=42,
        database_=os.getenv("NEO4J_DATABASE"),
    )

    # Loop through results and do something with them
    for person in records:
        print(person)
    # Summary information
    print("The query `{query}` returned {records_count} records in {time} ms.".format(
        query=summary.query, records_count=len(records),
        time=summary.result_available_after,
    ))
