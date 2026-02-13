from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from data import itemlist

if TYPE_CHECKING:
    from .world import APTombolaWorld

def all_items_to_id():
    the_list = {}

    for item in itemlist.numbers: # Add Numbers
        number = item[0]
        name = item[1]
        key = f"{number} - {name}"
        the_list[key] = number

    return the_list
