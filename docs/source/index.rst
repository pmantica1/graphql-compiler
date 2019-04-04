GraphQL Compiler
============================================


Quick Overview
--------------
Through the GraphQL compiler, users can write powerful queries that uncover
deep relationships in the data while not having to worry about the underlying database query
language. The GraphQL compiler turns read-only queries written in GraphQL syntax to different
query languages.

Furthermore, the GraphQL compiler validates queries through the use of a GraphQL schema
that specifies the underlying schema of the database. We can currently autogenerate a
GraphQL schema by introspecting an OrientDB database.

In the near future, we plan to add schema autogeneration from SQLAlchemy metadata as well.

For a more detailed overview and getting started guide, please see
`our blog post`_.

.. _our blog post: https://blog.kensho.com/compiled-graphql-as-a-database-query-language-72e106844282./


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Language Specification

   graphql_schema
   definitions
   directives
   filtering_operations
   other

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Miscellaneous

   expanding_optional_vertex_fields
   type_equivalence_hints
   performance_penalty

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: License

   license

