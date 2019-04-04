The GraphQL schema
==================

This section assumes that the reader is familiar with the way schemas work in the
`reference implementation of GraphQL <http://graphql.org/learn/schema/>`_.

The GraphQL schema used with the compiler must contain the custom directives and custom :code:`Date`
and :code:`DateTime` scalar types defined by the compiler:

.. code-block::

    directive @recurse(depth: Int!) on FIELD

    directive @filter(value: [String!]!, op_name: String!) on FIELD | INLINE_FRAGMENT

    directive @tag(tag_name: String!) on FIELD

    directive @output(out_name: String!) on FIELD

    directive @output_source on FIELD

    directive @optional on FIELD

    directive @fold on FIELD

    scalar DateTime

    scalar Date

If constructing the schema programmatically, one can simply import the the Python object
representations of the custom directives and the custom types:

.. code-block::

    from graphql_compiler import DIRECTIVES  # the list of custom directives
    from graphql_compiler import GraphQLDate, GraphQLDateTime  # the custom types


Since the GraphQL and OrientDB type systems have different rules, there is no one-size-fits-all
solution to writing the GraphQL schema for a given database schema.
However, the following rules of thumb are useful to keep in mind:
- Generally, represent OrientDB abstract classes as GraphQL interfaces. In GraphQL's type system,
  GraphQL interfaces cannot inherit from other GraphQL interfaces.
- Generally, represent OrientDB non-abstract classes as GraphQL types,
  listing the GraphQL interfaces that they implement. In GraphQL's type system, GraphQL types
  cannot inherit from other GraphQL types.
- Inheritance relationships between two OrientDB non-abstract classes,
  or between two OrientDB abstract classes, introduce some difficulties in GraphQL.
  When modelling your data in OrientDB, it's best to avoid such inheritance if possible.
- If it is impossible to avoid having two non-abstract OrientDB classes :code:`A` and :code:`B` such that
  :code:`B` inherits from :code:`A`, you have two options:
    - You may choose to represent the :code:`A` OrientDB class as a GraphQL interface,
      which the GraphQL type corresponding to :code:`B` can implement.
      In this case, the GraphQL schema preserves the inheritance relationship
      between :code:`A` and :code:`B`, but sacrifices the representation of any inheritance relationships
      :code:`A` may have with any OrientDB superclasses.
    - You may choose to represent both :code:`A` and `B` as GraphQL types. The tradeoff in this case is
      exactly the opposite from the previous case: the GraphQL schema
      sacrifices the inheritance relationship between :code:`A` and `B`, but preserves the
      inheritance relationships of :code:`A` with its superclasses.
      In this case, it is recommended to create a GraphQL union type :code:`A | B`,
      and to use that GraphQL union type for any vertex fields that
      in OrientDB would be of type :code:`A`.
- If it is impossible to avoid having two abstract OrientDB classes :code:`A` and :code:`B` such that
  :code:`B` inherits from :code:`A`, you similarly have two options:
    - You may choose to represent :code:`B` as a GraphQL type that can implement the GraphQL interface
      corresponding to :code:`A`. This makes the GraphQL schema preserve the inheritance relationship
      between :code:`A` and :code:`B`, but sacrifices the ability for other GraphQL types to inherit from :code:`B`.
    - You may choose to represent both :code:`A` and :code:`B` as GraphQL interfaces, sacrificing the schema's
      representation of the inheritance between :code:`A` and :code:`B`, but allowing GraphQL types
      to inherit from both :code:`A` and :code:`B`. If necessary, you can then create a GraphQL
      union type :code:`A | B` and use it for any vertex fields that in OrientDB would be of type :code:`A`.
- It is legal to fully omit classes and fields that are not representable in GraphQL. The compiler
  currently does not support OrientDB's :code:`EmbeddedMap` type nor embedded non-primitive typed fields,
  so such fields can simply be omitted in the GraphQL representation of their classes.
  Alternatively, the entire OrientDB class and all edges that may point to it may be omitted
  entirely from the GraphQL schema.
