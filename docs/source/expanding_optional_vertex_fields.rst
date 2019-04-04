.. _explaining_optional_vertex_fields:

Expanding @optional vertex fields
=================================

Including an optional statement in GraphQL has no performance issues on its own,
but if you continue expanding vertex fields within an optional scope,
there may be significant performance implications.

Going forward, we will refer to two different kinds of :code:`@optional` directives.

A *"simple"* optional is a vertex with an :code:`@optional` directive that does not expand
any vertex fields within it.

For example:

.. code-block:: python3

    {
        Animal {
            name @output(out_name: "name")
            in_Animal_ParentOf @optional {
                name @output(out_name: "parent_name")
            }
        }
    }

OrientDB :code:`MATCH` currently allows the last step in any traversal to be optional.
Therefore, the equivalent `MATCH` traversal for the above `GraphQL` is as follows:

.. code-block::

    SELECT
        Animal___1.name as `name`,
        Animal__in_Animal_ParentOf___1.name as `parent_name`
    FROM (
        MATCH {
            class: Animal,
            as: Animal___1
        }.in('Animal_ParentOf') {
            as: Animal__in_Animal_ParentOf___1
        }
        RETURN $matches
    )

A *"compound"* optional is a vertex with an :code:`@optional` directive which does expand
vertex fields within it.

For example:

.. code-block:: python3

    {
        Animal {
            name @output(out_name: "name")
            in_Animal_ParentOf @optional {
                name @output(out_name: "parent_name")
                in_Animal_ParentOf {
                    name @output(out_name: "grandparent_name")
                }
            }
        }
    }

Currently, this cannot represented by a simple :code:`MATCH` query.
Specifically, the following is *NOT* a valid :code:`MATCH` statement,
because the optional traversal follows another edge:

NOT A VALID QUERY:

.. code-block::

    SELECT
        Animal___1.name as `name`,
        Animal__in_Animal_ParentOf___1.name as `parent_name`
    FROM (
        MATCH {
            class: Animal,
            as: Animal___1
        }.in('Animal_ParentOf') {
            optional: true,
            as: Animal__in_Animal_ParentOf___1
        }.in('Animal_ParentOf') {
            as: Animal__in_Animal_ParentOf__in_Animal_ParentOf___1
        }
        RETURN $matches
    )


Instead, we represent a *compound* optional by taking an union (:code:`UNIONALL`) of two distinct
:code:`MATCH` queries. For instance, the :code:`GraphQL` query above can be represented as follows:

.. code-block::

    SELECT EXPAND($final_match)
    LET
        $match1 = (
            SELECT
                Animal___1.name AS `name`
            FROM (
                MATCH {
                    class: Animal,
                    as: Animal___1,
                    where: (
                        (in_Animal_ParentOf IS null)
                        OR
                        (in_Animal_ParentOf.size() = 0)
                    ),
                }
            )
        ),
        $match2 = (
            SELECT
                Animal___1.name AS `name`,
                Animal__in_Animal_ParentOf___1.name AS `parent_name`
            FROM (
                MATCH {
                    class: Animal,
                    as: Animal___1
                }.in('Animal_ParentOf') {
                    as: Animal__in_Animal_ParentOf___1
                }.in('Animal_ParentOf') {
                    as: Animal__in_Animal_ParentOf__in_Animal_ParentOf___1
                }
            )
        ),
        $final_match = UNIONALL($match1, $match2)


In the first case where the optional edge is not followed,
we have to explicitly filter out all vertices where the edge *could have been followed*.
This is to eliminate duplicates between the two :code:`MATCH` selections.

The previous example is not *exactly* how we implement *compound* optionals
(we also have `SELECT` statements within :code:`$match1` and :code:`$match2`),
but it illustrates the the general idea.
