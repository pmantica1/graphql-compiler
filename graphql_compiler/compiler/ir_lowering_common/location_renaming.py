# Copyright 2019-present Kensho Technologies, LLC.
"""Utilities for rewriting IR to replace one set of locations with another."""
import six

from ..expressions import (
    BinaryComposition, ContextField, ContextFieldExistence, FalseLiteral, FoldedContextField,
    Literal, TernaryConditional, TrueLiteral
)
from ..helpers import FoldScopeLocation


def make_revisit_location_translations(query_metadata_table):
    """Return a dict mapping location revisits to the location being revisited, for rewriting."""
    location_translations = dict()

    for location, _ in query_metadata_table.registered_locations:
        location_being_revisited = query_metadata_table.get_revisit_origin(location)
        if location_being_revisited != location:
            location_translations[location] = location_being_revisited

    return location_translations


def make_location_rewriter_visitor_fn(location_translations):
    """Return a visitor function that is able to replace locations with equivalent locations."""
    def visitor_fn(expression):
        """Expression visitor function used to rewrite expressions with updated Location data."""
        if isinstance(expression, (ContextField, ContextFieldExistence)):
            old_location = expression.location
            new_location = location_translations.get(old_location, old_location)

            # The Expression could be one of many types, including:
            #   - ContextField
            #   - ContextFieldExistence
            # We determine its exact class to make sure we return an object of the same class
            # as the replacement expression.
            expression_cls = type(expression)
            return expression_cls(new_location)
        elif isinstance(expression, FoldedContextField):
            # Update the Location within FoldedContextField
            old_location = expression.fold_scope_location.base_location
            new_location = location_translations.get(old_location, old_location)

            fold_path = expression.fold_scope_location.fold_path
            fold_field = expression.fold_scope_location.field
            new_fold_scope_location = FoldScopeLocation(new_location, fold_path, field=fold_field)
            field_type = expression.field_type

            return FoldedContextField(new_fold_scope_location, field_type)
        else:
            return expression

    return visitor_fn
