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

Databases and Query Languages
-----------------------------

We currently support a single database, OrientDB version 2.2.28+, and two query languages that OrientDB supports: the OrientDB dialect of gremlin, and OrientDB's own custom SQL-like query language that we refer to as MATCH, after the name of its graph traversal operator. With OrientDB, MATCH should be the preferred choice for most users, since it tends to run faster than gremlin, and has other desirable properties. See the Execution model section for more details.
Support for relational databases including PostgreSQL, MySQL, SQLite,
and Microsoft SQL Server is a work in progress. A subset of compiler features are available for
these databases. See the :doc:`sql` section for more details.


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
   :caption: Supported Targets

   orientdb
   sql

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Developer Documentation

   contributing
   troubleshooting
   code_of_conduct

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Other

   faq
   change_log

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Miscellaneous

   expanding_optional_vertex_fields
   type_equivalence_hints
   performance_penalty
   execution_model

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Licenses

   license
