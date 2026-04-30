from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .data import itemlist

if TYPE_CHECKING:
    from .world import APTombolaWorld


def all_items_to_id():
    the_list = {}

    for item in itemlist.numbers: # Add Numbers
        key = itemlist.combine_number_name(item[0],item[1])
        the_list[key] = item[0]

    for item in itemlist.fillers: # Add Fillers
        the_list[item[1]] = item[0]

    for item in itemlist.unlocks: # Add Cardsanity Unlocks
        the_list[item[1]] = item[0]

    for item in itemlist.usefuls: # Add Usefuls
        the_list[item[1]] = item[0]

    for item in itemlist.traps: # Add Traps
        the_list[item[1]] = item[0]

    return the_list

def all_default_classifications():
    classifications = {}

    for item in itemlist.numbers: # Numbers
        key = itemlist.combine_number_name(item[0],item[1])
        classifications[key] = ItemClassification.progression

    for item in itemlist.fillers: # Fillers
        classifications[item[1]] = ItemClassification.filler

    for item in itemlist.unlocks: # Cardsanity unlocks
        classifications[item[1]] = ItemClassification.progression

    for item in itemlist.usefuls: # Usefuls
        classifications[item[1]] = ItemClassification.useful

    for item in itemlist.traps: # Traps
        classifications[item[1]] = ItemClassification.trap

    return classifications

# Create the lists with ids and classifications to mimic APQuest behaviour
ITEM_NAME_TO_ID = all_items_to_id()
DEFAULT_ITEM_CLASSIFICATIONS = all_default_classifications()


class APTombolaItem(Item):
    game = "AP Tombola"


def get_random_filler_item_name(world: APTombolaWorld) -> str:
    item = world.random.choice(itemlist.fillers)
    return item[1]

def create_random_trap(world: APTombolaWorld):
    traps = ["Blindness Trap","Lock Trap"]
    return world.create_item(world.random.choice(traps))

def create_item_with_correct_classification(world: APTombolaWorld, name: str) -> APTombolaItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    return APTombolaItem(name, classification, ITEM_NAME_TO_ID[name], world.player)

def create_all_items(world: APTombolaWorld) -> None:
    itempool: list[Item] = []

    for item in itemlist.numbers:
        to_pool = world.create_item(itemlist.combine_number_name(item[0],item[1]))
        itempool.append(to_pool)

    locks = [1,2,3,4,5,6]
    world.random.shuffle(locks)
    to_lock = world.options.cardsanity

    while to_lock:
        to_lock -= 1
        c = locks.pop()
        to_pool = world.create_item(f"Card {c} Unlock")
        itempool.append(to_pool)

    for c in locks:
        to_precollect = world.create_item(f"Card {c} Unlock")
        world.push_precollected(to_precollect)
        item = get_random_filler_item_name(world)
        to_pool = world.create_item(item)
        itempool.append(to_pool)


    # Item counts of non-fillers are manually specified
    # MILESTONES
    for i in range(1): # Yes it seems dumb, i just have it like this in case i change my mind and wanna add more
        to_pool = world.create_item("Free Mark!!!")
        itempool.append(to_pool)
    for i in range(2):
        to_pool = world.create_item("Free Location Hint")
        itempool.append(to_pool)
    for i in range(2):
        to_pool = world.create_item("Anti-Trap Shield")
        itempool.append(to_pool)
    for i in range(4):
        to_pool = create_random_trap(world)
        itempool.append(to_pool)
    for i in range(9):
        item = get_random_filler_item_name(world)
        to_pool = world.create_item(item)
        itempool.append(to_pool)


    # ROWSANITY
    if world.options.rowsanity:
        for i in range(2): # Free Mark
            to_pool = world.create_item("Free Mark!!!")
            itempool.append(to_pool)
        for i in range(4): # Free Location Hint
            to_pool = world.create_item("Free Location Hint")
            itempool.append(to_pool)
        for i in range(3): # Anti-Trap Shield
            to_pool = world.create_item("Anti-Trap Shield")
            itempool.append(to_pool)
        for i in range(10): # Traps
            to_pool = create_random_trap(world)
            itempool.append(to_pool)
        for i in range(71): # Filler
            item = get_random_filler_item_name(world)
            to_pool = world.create_item(item)
            itempool.append(to_pool)

    world.multiworld.itempool += itempool

def create_all_item_groups():
    item_groups = {}

    # - Numbers Group
    group_numbers = set()

    for item in itemlist.numbers:
        item_name = itemlist.combine_number_name(item[0],item[1])

        # Add to Numbers Group
        group_numbers.add(item_name)

        # Create single number group for easy hinting
        singular_group = set()
        singular_group.add(item_name)
        item_groups[str(item[0])] = singular_group

    # Add the Numbers group to item_groups
    item_groups["Numbers"] = group_numbers

    # - Unlocks Group
    group_unlocks = set()

    for item in itemlist.unlocks:
        group_unlocks.add(item[1])

    item_groups["Unlocks"] = group_unlocks

    # TODO Create filler list when filler will actually exist

    return item_groups





