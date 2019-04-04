Filtering Operations
====================

Comparison operators
--------------------

Supported comparison operators:
- Equal to: :code:`=`
- Not equal to: :code:`!=`
- Greater than: :code:`>`
- Less than: :code:`<`
- Greater than or equal to: :code:`>=`
- Less than or equal to: :code:`<=`

Equal to (:code:`=`):
*********************

.. code-block::

    {
        Species {
            name @filter(op_name: "=", value: ["$species_name"])
            uuid @output(out_name: "species_uuid")
        }
    }

This returns one row for every :code:`Species` whose name is equal to the value of the
:code:`$species_name`
parameter, containing the :code:`uuid` of the :code:`Species` in a column named :code:`species_uuid`.

Greater than or equal to (:code:`>=`):
**************************************

.. code-block::

    {
        Animal {
            name @output(out_name: "name")
            birthday @output(out_name: "birthday")
                     @filter(op_name: ">=", value: ["$point_in_time"])
        }
    }

This returns one row for every :code:`Animal` that was born after or on a :code:`$point_in_time`,
containing the animal's name and birthday in columns named :code:`name` and :code:`birthday`, respectively.

Constraints and Rules
*********************

All comparison operators must be on a property field.

name_or_alias
-------------

Allows you to filter on vertices which contain the exact string `$wanted_name_or_alias` in their
:code`name` or `alias` fields.

Example Use
***********

.. code-block::

    {
        Animal @filter(op_name: "name_or_alias", value: ["$wanted_name_or_alias"]) {
            name @output(out_name: "name")
        }
    }

This returns one row for every :code:`Animal` whose name and/or alias is equal to
:code:`$wanted_name_or_alias`,
containing the animal's name in a column named :code:`name`.

The value provided for :code:`$wanted_name_or_alias` must be the full name and/or alias of the :code:`Animal`.
Substrings will not be matched.

Constraints and Rules
*********************

Must be on a vertex field that has `name` and `alias` properties.

between
-------

Example Use
***********

.. code-block::

    {
        Animal {
            name @output(out_name: "name")
            birthday @filter(op_name: "between", value: ["$lower", "$upper"])
                     @output(out_name: "birthday")
        }
    }

This returns:
One row for every :code:`Animal` whose birthday is in between :code:`$lower` and :code:`$upper` dates
(inclusive), containing the animal's name in a column named :code:`name`.

Constraints and Rules
*********************

- Must be on a property field.
- The lower and upper bounds represent an inclusive interval, which means that the output may
  contain values that match them exactly.

in_collection
-------------

Example Use
***********

.. code-block::

    {
        Animal {
            name @output(out_name: "animal_name")
            color @output(out_name: "color")
                  @filter(op_name: "in_collection", value: ["$colors"])
        }
    }

This returns one row for every :code:`Animal` which has a color contained in a list of colors,
containing the :code:`Animal`'s name and color in columns named :code:`animal_name` and :code:`color`, respectively.

Constraints and Rules
*********************

- Must be on a property field that is not of list type.

has_substring
-------------

Example Use
***********


    {
        Animal {
            name @filter(op_name: "has_substring", value: ["$substring"])
                 @output(out_name: "animal_name")
        }
    }

This returns one row for every :code:`Animal` whose name contains the value supplied
for the :code:`$substring` parameter. Each row contains the matching :code:`Animal`'s name
in a column named :code:`animal_name`.

Constraints and Rules
*********************

Must be on a property field of string type.

contains
--------


Example Use
***********

.. code-block::

    {
        Animal {
            alias @filter(op_name: "contains", value: ["$wanted"])
            name @output(out_name: "animal_name")
        }
    }

This returns one row for every :code:`Animal` whose list of aliases contains the value supplied
for the :code:`$wanted` parameter. Each row contains the matching :code:`Animal`'s name
in a column named :code:`animal_name`.

Constraints and Rules
*********************

Must be on a property field of list type.

intersects
----------

Example Use
***********

.. code-block::

    {
        Animal {
            alias @filter(op_name: "intersects", value: ["$wanted"])
            name @output(out_name: "animal_name")
        }
    }

This returns one row for every :code:`Animal` whose list of aliases has a non-empty intersection
with the list of values supplied for the :code:`$wanted` parameter.
Each row contains the matching :code:`Animal`'s name in a column named :code:`animal_name`.

Constraints and Rules
*********************

Must be on a property field of list type.

has_edge_degree
---------------

Example Use
***********

.. code-block::

    {
        Animal {
            name @output(out_name: "animal_name")

            out_Animal_ParentOf @filter(op_name: "has_edge_degree", value: ["$child_count"]) @optional {
                uuid
            }
        }
    }

This returns one row for every :code:`Animal` that has exactly :code:`$child_count` children
(i.e. where the :code:`out_Animal_ParentOf` edge appears exactly :code:`$child_count` times).
Each row contains the matching :code:`Animal`'s name, in a column named :code:`animal_name`.

The :code:`uuid` field within the :code:`out_Animal_ParentOf` vertex field is added simply to satisfy
the GraphQL syntax rule that requires at least one field to exist within any :code:`{}`.
Since this field is not marked with any directive, it has no effect on the query.

*N.B.:* Please note the :code:`@optional` directive on the vertex field being filtered above.
If in your use case you expect to set :code:`$child_count` to 0, you must also mark that
vertex field :code:`@optional`. Recall that absence of :code:`@optional` implies that at least one
such edge must exist. If the :code:`has_edge_degree` filter is used with a parameter set to 0,
that requires the edge to not exist. Therefore, if the :code:`@optional` is not present in this situation,
no valid result sets can be produced, and the resulting query will return no results.

Constraints and Rules
*********************

- Must be on a vertex field that is not the root vertex of the query.
- Tagged values are not supported as parameters for this filter.
- If the runtime parameter for this operator can be :code:`0`, it is *strongly recommended* to also apply
  :code:`@optional` to the vertex field being filtered (see N.B. above for details).
