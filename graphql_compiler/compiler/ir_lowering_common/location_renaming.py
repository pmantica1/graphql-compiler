# Copyright 2019-present Kensho Technologies, LLC.
"""Utilities for rewriting IR to replace one set of locations with another."""
import six

from ..expressions import (
    BinaryComposition, ContextField, ContextFieldExistence, FalseLiteral, FoldedContextField,
    Literal, TernaryConditional, TrueLiteral
)
from ..helpers import FoldScopeLocation


def flatten_location_translations(location_translations):
    """If location A translates to B, and B to C, then make A translate directly to C.

    Args:
        location_translations: dict of Location -> Location, where the key translates to the value.
                               Mutated in place for efficiency and simplicity of implementation.
    """
    sources_to_process = set(six.iterkeys(location_translations))

    def _update_translation(source):
        """Return the proper (fully-flattened) translation for the given location."""
        destination = location_translations[source]
        if destination not in location_translations:
            # "destination" cannot be translated, no further flattening required.
            return destination
        else:
            # "destination" can itself be translated -- do so,
            # and then flatten "source" to the final translation as well.
            sources_to_process.discard(destination)
            final_destination = _update_translation(destination)
            location_translations[source] = final_destination
            return final_destination

    while sources_to_process:
        _update_translation(sources_to_process.pop())


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
