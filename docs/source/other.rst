Other
=====

Type coercions
--------------

Type coercions are operations that create a new scope whose type is different than the type of the
enclosing scope of the coercion -- they coerce the enclosing scope into a different type.
Type coercions are represented with GraphQL inline fragments.

Example Use
***********

.. code-block::

    {
        Species {
            name @output(out_name: "species_name")
            out_Species_Eats {
                ... on Food {
                    name @output(out_name: "food_name")
                }
            }
        }
    }

Here, the :code:`out_Species_Eats` vertex field is of the :code:`Union__Food__FoodOrSpecies__Species`
union type. To proceed
with the query, the user must choose which of the types in the :code:`Union__Food__FoodOrSpecies__Species` union to use.
In this example, :code:`... on Food` indicates that the `Food` type was chosen, and any vertices
at that scope that are not of type :code:`Food` are filtered out and discarded.

.. code-block::

    {
        Species {
            name @output(out_name: "species_name")
            out_Entity_Related {
                ... on Species {
                    name @output(out_name: "food_name")
                }
            }
        }
    }

In this query, the :code:`out_Entity_Related` is of :code:`Entity` type. However, the query only wants to
return results where the related entity is a :code:`Species`, which :code:`... on Species` ensures is the case.

Meta fields
-----------

\_\_typename
************

The compiler supports the standard GraphQL meta field :code:`__typename`, which returns the runtime type
of the scope where the field is found. Assuming the GraphQL schema matches the database's schema,
the runtime type will always be a subtype of (or exactly equal to) the static type of the scope
determined by the GraphQL type system. Below, we provide an example query in which
the runtime type is a subtype of the static type, but is not equal to it.

The :code:`__typename` field is treated as a property field of type :code:`String`, and supports
all directives that can be applied to any other property field.

Example Use
~~~~~~~~~~~

.. code-block::

    {
        Entity {
            __typename @output(out_name: "entity_type")
            name @output(out_name: "entity_name")
        }
    }

This query returns one row for each :code:`Entity` vertex. The scope in which :code:`__typename` appears is
of static type :code:`Entity`. However, :code:`Animal` is a type of :code:`Entity`, as are :code:`Species`, :code:`Food`,
and others. Vertices of all subtypes of :code:`Entity` will therefore be returned, and the `entity_type`
column that outputs the :code:`__typename` field will show their runtime type: :code:`Animal`, :code:`Species`,
:code:`Food`, etc.

\_x\_count
**********

The :code:`_x_count` meta field is a non-standard meta field defined by the GraphQL compiler that makes it
possible to interact with the _number_ of elements in a scope marked :code:`@fold`. By applying directives
like :code:`@output` and :code:`@filter` to this meta field, queries can output the number of elements captured
in the :code:`@fold` and filter down results to select only those with the desired fold sizes.

We use the :code:`_x_` prefix to signify that this is an extension meta field introduced by the compiler,
and not part of the canonical set of GraphQL meta fields defined by the GraphQL specification.
We do not use the GraphQL standard double-underscore (:code:`__`) prefix for meta fields,
since all names with that prefix are
`explicitly reserved and prohibited from being used <https://facebook.github
.io/graphql/draft/#sec-Reserved-Names/>`_
in directives, fields, or any other artifacts.

Adding the :code:`_x_count` meta field to your schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since the :code:`_x_count` meta field is not currently part of the GraphQL standard, it has to be
explicitly added to all interfaces and types in your schema. There are two ways to do this.

The preferred way to do this is to use the :code:`EXTENDED_META_FIELD_DEFINITIONS` constant as
a starting point for building your interfaces' and types' field descriptions:

.. code-block:: python3

    from graphql import GraphQLInt, GraphQLField, GraphQLObjectType, GraphQLString
    from graphql_compiler import EXTENDED_META_FIELD_DEFINITIONS

    fields = EXTENDED_META_FIELD_DEFINITIONS.copy()
    fields.update({
        'foo': GraphQLField(GraphQLString),
        'bar': GraphQLField(GraphQLInt),
        # etc.
    })
    graphql_type = GraphQLObjectType('MyType', fields)
    # etc

If you are not able to programmatically define the schema, and instead simply have a pre-made
GraphQL schema object that you are able to mutate, the alternative approach is via the
:code:`insert_meta_fields_into_existing_schema()` helper function defined by the compiler:

.. code-block::

    # assuming that existing_schema is your GraphQL schema object
    insert_meta_fields_into_existing_schema(existing_schema)
    # existing_schema was mutated in-place and all custom meta-fields were added


Example Use
~~~~~~~~~~~

.. code-block::

    {
        Animal {
            name @output(out_name: "name")
            out_Animal_ParentOf @fold {
                _x_count @output(out_name: "number_of_children")
                name @output(out_name: "child_names")
            }
        }
    }

This query returns one row for each :code:`Animal` vertex, containing its name, and the number and names
of its children. While the output type of the :code:`child_names` selection is a list of strings,
the output type of the :code:`number_of_children` selection is an integer.

.. code-block::

    {
        Animal {
            name @output(out_name: "name")
            out_Animal_ParentOf @fold {
                _x_count @filter(op_name: ">=", value: ["$min_children"])
                        @output(out_name: "number_of_children")
                name @filter(op_name: "has_substring", value: ["$substr"])
                     @output(out_name: "child_names")
            }
        }
    }

Here, we've modified the above query to add two more filtering constraints to the returned rows:
- child :code:`Animal` vertices must contain the value of :code:`$substr` as a substring in their name, and
- :code:`Animal` vertices must have at least :code:`$min_children` children that satisfy the above filter.

Importantly, any filtering on :code:`_x_count` is applied *after* any other filters and type coercions
that are present in the :code:`@fold` in question. This order of operations matters a lot: selecting
:code:`Animal` vertices with 3+ children, then filtering the children based on their names is not the same
as filtering the children first, and then selecting :code:`Animal` vertices that have 3+ children that
matched the earlier filter.

Constraints and Rules
~~~~~~~~~~~~~~~~~~~~~

- The :code:`_x_count` field is only allowed to appear within a vertex field marked :code:`@fold`.
- Filtering on :code:`_x_count` is always applied *after* any other filters and type coercions present
  in that :code:`@fold`.
- Filtering or outputting the value of the :code:`_x_count` field must always be done at the innermost
  scope of the :code:`@fold`. It is invalid to expand vertex fields within a :code:`@fold` after filtering
  or outputting the value of the :code:`_x_count` meta field.

How is filtering on :code:`_x_count` different from :code:`@filter` with :code:`has_edge_degree`?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :code:`has_edge_degree` filter allows filtering based on the number of edges of a particular type.
There are situations in which filtering with :code:`has_edge_degree` and filtering using :code:`=` on :code:`_x_count`
produce equivalent queries. Here is one such pair of queries:

.. code-block::

    {
        Species {
            name @output(out_name: "name")
            in_Animal_OfSpecies @filter(op_name: "has_edge_degree", value: ["$num_animals"]) {
                uuid
            }
        }
    }


and

.. code-block::

    {
        Species {
            name @output(out_name: "name")
            in_Animal_OfSpecies @fold {
                _x_count @filter(op_name: "=", value: ["$num_animals"])
            }
        }
    }

In both of these queries, we ask for the names of the :code:`Species` vertices that have precisely
:code:`$num_animals` members. However, we have expressed this question in two different ways: once
as a property of the :code:`Species` vertex ("the degree of the :code:`in_Animal_OfSpecies` is :code:`$num_animals`"),
and once as a property of the list of :code:`Animal` vertices produced by the :code:`@fold` ("the number of
elements in the :code:`@fold` is :code:`$num_animals`").

When we add additional filtering within the :code:`Animal` vertices of the :code:`in_Animal_OfSpecies` vertex
field, this distinction becomes very important. Compare the following two queries:
.. code-block::

    {
        Species {
            name @output(out_name: "name")
            in_Animal_OfSpecies @filter(op_name: "has_edge_degree", value: ["$num_animals"]) {
                out_Animal_LivesIn {
                    name @filter(op_name: "=", value: ["$location"])
                }
            }
        }
    }

versus

.. code-block::

    {
        Species {
            name @output(out_name: "name")
            in_Animal_OfSpecies @fold {
                out_Animal_LivesIn {
                    _x_count @filter(op_name: "=", value: ["$num_animals"])
                    name @filter(op_name: "=", value: ["$location"])
                }
            }
        }
    }

In the first, for the purposes of the :code:`has_edge_degree` filtering, the location where the animals
live is irrelevant: the :code:`has_edge_degree` only makes sure that the :code:`Species` vertex has the
correct number of edges of type :code:`in_Animal_OfSpecies`, and that's it. In contrast, the second query
ensures that only :code:`Species` vertices that have :code:`$num_animals` animals that live in the selected
location are returned -- the location matters since the :code:`@filter` on the :code:`_x_count` field applies
to the number of elements in the :code:`@fold` scope.
