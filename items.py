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

# Create the lists with ids and classifications to mimic APQuest behaviour
ITEM_NAME_TO_ID = all_items_to_id()
DEFAULT_ITEM_CLASSIFICATIONS = all_default_classifications()


class APTombolaItem(Item):
    game = "AP Tombola"


def get_random_filler_item_name(world: APTombolaWorld) -> str:
    return "Orange Peel" # TODO actually give a random filler, so far only one exists so it's ok to hardcode it

def create_item_with_correct_classification(world: APTombolaWorld, name: str) -> APTombolaItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    return APTombolaItem(name, classification, ITEM_NAME_TO_ID[name], world.player)

def create_all_items(world: APTombolaWorld) -> None:
    itempool: list[Item] = []

    for item in itemlist.numbers:
        to_pool = world.create_item(itemlist.combine_number_name(item[0],item[1]))
        itempool.append(to_pool)

    # TODO filler and other stuff planned

    world.multiworld.itempool += itempool




