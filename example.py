from graphql_compiler import (
    get_graphql_schema_from_orientdb_schema_data, graphql_to_match
)
from graphql_compiler.schema_generation.utils import ORIENTDB_SCHEMA_RECORDS_QUERY
from graphql_compiler.tests.conftest import init_integration_graph_client


# Step 1: Initialize dummy OrientDB database and get pyorient OrientDB client
client = init_integration_graph_client()

# Step 2: Generate GraphQL schema from queried OrientDB schema records
schema_records = client.command(ORIENTDB_SCHEMA_RECORDS_QUERY)
schema_data = [x.oRecordData for x in schema_records]
schema, type_equivalence_hints = get_graphql_schema_from_orientdb_schema_data(schema_data)

# Step 3: Write GraphQL query to get the names of all animals with a particular net worth
# Note that we prefix net_worth with '$' and surround it with quotes to indicate it's a parameter
graphql_query = '''
{
    Animal {
        name @output(out_name: "animal_name")
        net_worth @filter(op_name: "=", value: ["$net_worth"])
    }
}
'''
parameters = {
    'net_worth': '100',
}

# Step 4: Use autogenerated GraphQL schema to compile GraphQL query into Match, an OrientDB query
compilation_result = graphql_to_match(schema, graphql_query, parameters, type_equivalence_hints)

# Step 5: Run query in OrientDB
query = compilation_result.query
results = [row.oRecordData for row in client.command(query)]
assert results == [{'animal_name': 'Animal 1'}]
