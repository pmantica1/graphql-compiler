Definitions
===========

GraphQLSchema
-------------

To be able to compile GraphQL, the first thing you will need is a GraphQLSchema object
describing
the underlying database. To build it you can use
:code:`get_graphql_schema_from_orientdb_schema_data` as
demonstrated in the code example below.

.. code-block:: python3

    # Generate GraphQL schema from queried OrientDB schema records
    schema_records = client.command(ORIENTDB_SCHEMA_RECORDS_QUERY)
    schema_data = [x.oRecordData for x in schema_records]
    schema, type_equivalence_hints = get_graphql_schema_from_orientdb_schema_data(schema_data)


Vertex field
------------

A field corresponding to a vertex in the graph. In the below example, :code:`Animal`
and :code:`out_Entity_Related` are vertex fields. The :code:`Animal` field is the field at which querying
starts, and is therefore the **root vertex field**. In any scope, fields with the prefix :code:`out_`
denote vertex fields connected by an outbound edge, whereas ones with the prefix :code:`in_` denote
vertex fields connected by an inbound edge.

.. code-block::

    {
        Animal {
            name @output(out_name: "name")
            out_Entity_Related {
                ... on Species {
                    description @output(out_name: "description")
                }
            }
        }
    }

Property field
--------------

A field corresponding to a property of a vertex in the graph. In the
above example, the `name` and `description` fields are property fields. In any given scope,
**property fields must appear before vertex fields**.

Result set
----------

An assignment of vertices in the graph to scopes (locations) in the query.
As the database processes the query, new result sets may be created (e.g. when traversing edges),
and result sets may be discarded when they do not satisfy filters or type coercions. After all
parts of the query are processed by the database, all remaining result sets are used to form the
query result, by taking their values at all properties marked for output.

Scope
-----

The part of a query between any pair of curly braces. The compiler infers the type
of each scope. For example, in the above query, the scope beginning with :code:`Animal {` is of
type :code:`Animal`, the one beginning with :code:`out_Entity_Related {` is of type :code:`Entity`, and the one
beginning with :code:`... on Species {` is of type :code:`Species`.

Type coercion
-------------

An operation that produces a new scope of narrower type than the
scope in which it exists. Any result sets that cannot satisfy the narrower type are filtered out
and not returned. In the above query, :code:`... on Species` is a type coercion which takes
its enclosing scope of type :code:`Entity`, and coerces it into a narrower scope of
type :code:`Species`. This is possible since :code:`Entity` is an interface, and :code:s`Species`
is a type that implements the :code:`Entity` interface.
