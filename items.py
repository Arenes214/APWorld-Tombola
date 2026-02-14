from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from data import itemlist

if TYPE_CHECKING:
    from .world import APTombolaWorld


def all_items_to_id():
    the_list = {}

    for item in itemlist.numbers: # Add Numbers
        key = itemlist.combine_number_name(item[0],item[1])
        the_list[key] = item[0]

    for item in itemlist.fillers: # Add Fillers
        the_list[item[1]] = item[0]

    return the_list

def all_default_classifications():
    classifications = {}

    for item in itemlist.numbers: # Numbers
        key = itemlist.combine_number_name(item[0],item[1])
        classifications[key] = ItemClassification.progression

    for item in itemlist.fillers: # Fillers
        classifications[item[1]] = ItemClassification.filler

    return classifications
