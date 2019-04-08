
SQL
---

The following table outlines GraphQL compiler features, and their support (if any) by various
relational database flavors:

.. list-table::
   :header-rows: 1

   * - Feature/Dialect
     - Required Edges
     - @filter
     - @output
     - @recurse
     - @fold
     - @optional
     - @output_source
   * - PostgreSQL
     - No
     - Limited, `intersects <#intersects>`_\ , `has_edge_degree <#has_edge_degree>`_\ , and `name_or_alias <#name_or_alias>`_ filter unsupported
     - Limited, `__typename <#__typename>`_ output metafield unsupported
     - No
     - No
     - No
     - No
   * - SQLite
     - No
     - Limited, `intersects <#intersects>`_\ , `has_edge_degree <#has_edge_degree>`_\ , and `name_or_alias <#name_or_alias>`_ filter unsupported
     - Limited, `__typename <#__typename>`_ output metafield unsupported
     - No
     - No
     - No
     - No
   * - Microsoft SQL Server
     - No
     - Limited, `intersects <#intersects>`_\ , `has_edge_degree <#has_edge_degree>`_\ , and `name_or_alias <#name_or_alias>`_ filter unsupported
     - Limited, `__typename <#__typename>`_ output metafield unsupported
     - No
     - No
     - No
     - No
   * - MySQL
     - No
     - Limited, `intersects <#intersects>`_\ , `has_edge_degree <#has_edge_degree>`_\ , and `name_or_alias <#name_or_alias>`_ filter unsupported
     - Limited, `__typename <#__typename>`_ output metafield unsupported
     - No
     - No
     - No
     - No
   * - MariaDB
     - No
     - Limited, `intersects <#intersects>`_\ , `has_edge_degree <#has_edge_degree>`_\ , and `name_or_alias <#name_or_alias>`_ filter unsupported
     - Limited, `__typename <#__typename>`_ output metafield unsupported
     - No
     - No
     - No
     - No


Configuring SQLAlchemy
^^^^^^^^^^^^^^^^^^^^^^

Relational databases are supported by compiling to SQLAlchemy core as an intermediate
language, and then relying on SQLAlchemy's compilation of the dialect specific SQL string to query
the target database.

For the SQL backend, GraphQL types are assumed to have a SQL table of the same name, and with the
same properties. For example, a schema type

.. code-block::

   type Animal {
       name: String
   }

is expected to correspond to a SQLAlchemy table object of the same name, case insensitive. For this
schema type this could look like:

.. code-block:: python

   from sqlalchemy import MetaData, Table, Column, String
   # table for GraphQL type Animal
   metadata = MetaData()
   animal_table = Table(
       'animal', # name of table matches type name from schema
       metadata,
       Column('name', String(length=12)), # Animal.name GraphQL field has corresponding 'name' column
   )

If a table of the schema type name does not exist, an exception will be raised at compile time. See
`Configuring the SQL Database to Match the GraphQL Schema <#configuring-the-sql-database-to-match-the-graphql-schema>`_
for a possible option to resolve such naming discrepancies.

End-To-End SQL Example
^^^^^^^^^^^^^^^^^^^^^^

An end-to-end example including relevant GraphQL schema and SQLAlchemy engine preparation follows.

This is intended to show the setup steps for the SQL backend of the GraphQL compiler, and
does not represent best practices for configuring and running SQLAlchemy in a production system.

.. code-block:: python

   from graphql import parse
   from graphql.utils.build_ast_schema import build_ast_schema
   from sqlalchemy import MetaData, Table, Column, String, create_engine
   from graphql_compiler.compiler.ir_lowering_sql.metadata import SqlMetadata
   from graphql_compiler import graphql_to_sql

   # Step 1: Configure a GraphQL schema (note that this can also be done programmatically)
   schema_text = '''
   schema {
       query: RootSchemaQuery
   }
   # IMPORTANT NOTE: all compiler directives are expected here, but not shown to keep the example brief

   directive @filter(op_name: String!, value: [String!]!) on FIELD | INLINE_FRAGMENT

   # < more directives here, see the GraphQL schema section of this README for more details. >

   directive @output(out_name: String!) on FIELD

   type Animal {
       name: String
   }
   '''
   schema = build_ast_schema(parse(schema_text))

   # Step 2: For all GraphQL types, bind all corresponding SQLAlchemy Tables to a single SQLAlchemy
   # metadata instance, using the expected naming detailed above.
   # See https://docs.sqlalchemy.org/en/latest/core/metadata.html for more details on this step.
   metadata = MetaData()
   animal_table = Table(
       'animal', # name of table matches type name from schema
       metadata,
       # Animal.name schema field has corresponding 'name' column in animal table
       Column('name', String(length=12)),
   )

   # Step 3: Prepare a SQLAlchemy engine to query the target relational database.
   # See https://docs.sqlalchemy.org/en/latest/core/engines.html for more detail on this step.
   engine = create_engine('<connection string>')

   # Step 4: Wrap the SQLAlchemy metadata and dialect as a SqlMetadata GraphQL compiler object
   sql_metadata = SqlMetadata(engine.dialect, metadata)

   # Step 5: Prepare and compile a GraphQL query against the schema
   graphql_query = '''
   {
       Animal {
           name @output(out_name: "animal_name")
                @filter(op_name: "in_collection", value: ["$names"])
       }
   }
   '''
   parameters = {
       'names': ['animal name 1', 'animal name 2'],
   }

   compilation_result = graphql_to_sql(schema, graphql_query, parameters, sql_metadata)

   # Step 6: Execute compiled query against a SQLAlchemy engine/connection.
   # See https://docs.sqlalchemy.org/en/latest/core/connections.html for more details.
   query = compilation_result.query
   query_results = [dict(result_proxy) for result_proxy in engine.execute(query)]

Configuring the SQL Database to Match the GraphQL Schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For simplicity, the SQL backend expects an exact match between SQLAlchemy Tables and GraphQL types,
and between SQLAlchemy Columns and GraphQL fields. What if the table name or column name in the
database doesn't conform to these rules? Eventually the plan is to make this aspect of the
SQL backend more configurable. In the near-term, a possible way to address this is by using
SQL views.

For example, suppose there is a table in the database called ``animal_table`` and it has a column
called ``animal_name``. If the desired schema has type

.. code-block::

   type Animal {
       name: String
   }

Then this could be exposed via a view like:

.. code-block:: sql

   CREATE VIEW animal AS
       SELECT
           animal_name AS name
       FROM animal_table

At this point, the ``animal`` view can be used in the SQLAlchemy Table for the purposes of compiling.
