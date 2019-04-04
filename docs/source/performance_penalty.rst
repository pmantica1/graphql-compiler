Performance Penalty
===================

If we have many *compound* optionals in the given :code:`GraphQL`,
the above procedure results in the union of a large number of :code:`MATCH` queries.
Specifically, for :code:`n` compound optionals, we generate 2<sup>n</sup> different :code:`MATCH` queries.
For each of the 2<sup>n</sup> subsets :code:`S` of the :code:`n` optional edges:
- We remove the :code:`@optional` restriction for each traversal in :code:`S`.
- For each traverse :code:`t` in the complement of :code:`S`, we entirely discard :code:`t`
  along with all the vertices and directives within it, and we add a filter
  on the previous traverse to ensure that the edge corresponding to :code:`t` does not exist.

Therefore, we get a performance penalty that grows exponentially
with the number of *compound* optional edges.
This is important to keep in mind when writing queries with many optional directives.

If some of those *compound* optionals contain :code:`@optional` vertex fields of their own,
the performance penalty grows since we have to account for all possible subsets of :code:`@optional`
statements that can be satisfied simultaneously.
