from __future__ import annotations

import random

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

    # Starting Counts (aka extra from Milestones)
    count_free_mark = 1
    count_free_lochint = 2
    count_shield = 2
    count_traps = 4
    count_fillers = 9

    for item in itemlist.numbers:
        to_pool = world.create_item(itemlist.combine_number_name(item[0],item[1]))
        if world.options.deprioritize_numbers:
            to_pool.classification = ItemClassification.progression_deprioritized_skip_balancing
        itempool.append(to_pool)

    locks = [1,2,3,4,5,6]
    world.random.shuffle(locks)
    to_lock = world.options.cardsanity
    force_lock = world.cards_linked

    while to_lock:
        to_lock -= 1

        if len(force_lock):
            c = force_lock.pop()
            locks.remove(c)
        else:
            c = locks.pop()
        
        to_pool = world.create_item(f"Card {c} Unlock")
        itempool.append(to_pool)
        if world.options.additional_card_unlocks or world.force_extra_unlocks:
            to_pool = world.create_item(f"Card {c} Unlock") # Makes sense that i have to create a copy
            itempool.append(to_pool)
            count_fillers -= 1

    for c in locks:
        to_precollect = world.create_item(f"Card {c} Unlock")
        world.push_precollected(to_precollect)
        count_fillers += 1

    if world.options.rowsanity:
        count_free_mark += 2
        count_free_lochint += 4
        count_shield += 3
        count_traps += 10
        count_fillers += 71

    if world.options.marksanity:
        count_free_mark += 2
        count_free_lochint += 4
        count_shield += 3
        count_traps += 10
        count_fillers += 71

    # Easy Links
    # Free Marks
    mark_name = [0,"Free Mark!!!","Free Mark!!","Free Mark!"]
    if world.special_free_mark.keys():
        for (tier, to_do) in world.special_free_mark.items():
            count = 2
            if tier == 1:
                count = 1
            if to_do:
                for i in range(count):
                    count_free_mark -= 1
                    to_pool = world.create_item(mark_name[tier])
                    itempool.append(to_pool)
    
    # Free Location Hints
    lh_name = [0,"Free Location Hint!!!","Free Location Hint!!","Free Location Hint!"]
    if world.special_free_lochints.keys():
        for (tier, to_do) in world.special_free_lochints.items():
            count = 4
            if tier == 1:
                count = 2
            if to_do:
                for i in range(count):
                    count_free_lochint -= 1
                    to_pool = world.create_item(lh_name[tier])
                    itempool.append(to_pool)
    # Shields & Traps
    shield_name = [0,"Anti-Trap Shield!!!","Anti-Trap Shield!!","Anti-Trap Shield!"]
    blind_name = [0,"Blindness Trap!!!","Blindness Trap!!","Blindness Trap!"]
    lock_name = [0,"Lock Trap!!!","Lock Trap!!","Lock Trap!"]

    if world.special_shieldtrap.keys():
        special_rng = random.Random(world.trap_rng_seed)
        for (tier, to_do) in world.special_shieldtrap.items():
            count_shield_s = 3
            count_trap_s = 10
            if tier == 1:
                count_shield_s = 2
                count_trap_s = 4
            if to_do:
                for i in range(count_shield_s):
                    count_shield -= 1
                    to_pool = world.create_item(shield_name[tier])
                    itempool.append(to_pool)
                
                for i in range(count_trap_s):
                    count_traps -= 1
                    trap_chosen = special_rng.choice([blind_name[tier], lock_name[tier]])
                    to_pool_trap = world.create_item(trap_chosen)
                    itempool.append(to_pool_trap)

    for i in range(count_free_mark):
        to_pool = world.create_item("Free Mark")
        itempool.append(to_pool)
    for i in range(count_free_lochint):
        to_pool = world.create_item("Free Location Hint")
        itempool.append(to_pool)
    for i in range(count_shield):
        to_pool = world.create_item("Anti-Trap Shield")
        itempool.append(to_pool)
    for i in range(count_traps):
        to_pool = create_random_trap(world)
        itempool.append(to_pool)
    for i in range(count_fillers):
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

    # - Usefuls Group
    group_usefuls = set()

    for item in itemlist.usefuls:
        group_usefuls.add(item[1])
    item_groups["Useful Items"] = group_usefuls

    # - Traps Group
    group_traps = set()
    for item in itemlist.traps:
        group_traps.add(item[1])
    item_groups["Traps"] = group_traps

    return item_groups





