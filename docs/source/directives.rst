Directives
===========

@optional
---------

Without this directive, when a query includes a vertex field, any results matching that query
must be able to produce a value for that vertex field. Applied to a vertex field,
this directive prevents result sets that are unable to produce a value for that field from
being discarded, and allowed to continue processing the remainder of the query.

Example Use
***********
.. code-block:: python3


    {
        Animal {
            name @output(out_name: "name")
            out_Animal_ParentOf @optional {
                name @output(out_name: "child_name")
            }
        }
    }

For each :code:`Animal`:

- if it is a parent of another animal, at least one row containing the
  parent and child animal's names, in the :code:`name` and :code:`child_name` columns respectively;
- if it is not a parent of another animal, a row with its name in the :code:`name` column,
  and a :code:`null` value in the :code:`child_name` column.

Constraints and Rules
*********************
- :code:`@optional` can only be applied to vertex fields, except the root vertex field.
- It is allowed to expand vertex fields within an :code:`@optional` scope.
  However, doing so is currently associated with a performance penalty in :code:`MATCH`.
  For more detail, see: :doc:`expanding_optional_vertex_fields`.
- :code:`@recurse`, :code:`@fold`, or :code:`@output_source` may not be used at the same vertex field as `@optional`.
- :code:`@output_source` and :code:`@fold` may not be used anywhere within a scope
  marked :code:`@optional`.

If a given result set is unable to produce a value for a vertex field marked :code:`@optional`,
any fields marked :code:`@output` within that vertex field return the :code:`null` value.

When filtering (via :code:`@filter`) or type coercion (via e.g. :code:`... on Animal`) are applied
at or within a vertex field marked :code:`@optional`, the :code:`@optional` is given precedence:
- If a given result set cannot produce a value for the optional vertex field, it is preserved:
the :code:`@optional` directive is applied first, and no filtering or type coercion can happen.
- If a given result set is able to produce a value for the optional vertex field,
the :code:`@optional` does not apply, and that value is then checked against the filtering or type
coercion. These subsequent operations may then cause the result set to be discarded if it does
not match.s

@output
-------

Denotes that the value of a property field should be included in the output.
Its :code:`out_name` argument specifies the name of the column in which the
output value should be returned.

Example Use
-----------

.. code-block::

    {
        Animal {
            name @output(out_name: "animal_name")
        }
    }


This query returns the name of each :code:`Animal` in the graph, in a column named :code:`animal_name`.

Constraints and Rules
---------------------

- :code:`@output` can only be applied to property fields.
- The value provided for :code:`out_name` may only consist of upper or lower case letters
  (:code:`A-Z`, :code:`a-z`), or underscores (:code:`_`).
- The value provided for :code:`out_name` cannot be prefixed with :code:`___` (three underscores)
  This namespace is reserved for compiler internal use.
- For any given query, all :code:`out_name` values must be unique. In other words, output columns must
  have unique names.

If the property field marked :code:`@output` exists within a scope marked :code:`@optional`, result sets that
are unable to assign a value to the optional scope return the value :code:`null` as the output
of that property field.
