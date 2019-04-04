Type equivalence hints
======================

This compilation parameter is a workaround for the limitations of the GraphQL and Gremlin
type systems:
- GraphQL does not allow :code:`type` to inherit from another :code:`type`, only to implement an
:code:`interface`.
- Gremlin does not have first-class support for inheritance at all.

Assume the following GraphQL schema:
.. code-block::

    type Animal {
        name: String
    }

    type Cat {
        name: String
    }

    type Dog {
        name: String
    }

    union AnimalCatDog = Animal | Cat | Dog

    type Foo {
        adjacent_animal: AnimalCatDog
    }


An appropriate :code:`type_equivalence_hints` value here would be :code:`{ Animal: AnimalCatDog }`.
This lets the compiler know that the :code:`AnimalCatDog` union type is implicitly equivalent to
the :code:`Animal` type, as there are no other types that inherit from :code:`Animal` in the database schema.
This allows the compiler to perform accurate type coercions in Gremlin, as well as optimize away
type coercions across edges of union type if the coercion is coercing to the
union's equivalent type.

Setting :code:`type_equivalence_hints = { Animal: AnimalCatDog }` during compilation
would enable the use of a :code:`@fold` on the :code:`adjacent_animal` vertex field of :code:`Foo`:

.. code-block::

    {
        Foo {
            adjacent_animal @fold {
                ... on Animal {
                    name @output(out_name: "name")
                }
            }
        }
    }

