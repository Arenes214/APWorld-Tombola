# TODO TEST WHEN RULES.PY IS DONE REMOVE THE COMMENTS IN WORLD.PY

from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

from .data import itemlist

if TYPE_CHECKING:
    from .world import APTombolaWorld

def set_all_rules(world: APTombolaWorld) -> None:

    all_cards = cards.generate_cards(world)

    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: APTombolaWorld) -> None:
    # Currently all regions are just accessible, this may be used later for "cardsanity" aka locked cards
    return

def set_all_location_rules(world: APTombolaWorld) -> None:

    # Go through all Card locations
    for (loc_id, loc_name) in world.id_to_location_name:
        if loc_id < 10000:
            continue # Skip all non-card
        location = world.get_location(loc_name)

        # Get the type of location it is by its ID
        # TODO This won't work in a future where there are more than 9 cards
        loc_id_str = str(loc_id)
        card_id = int(loc_id_str(0)) - 1
        score_type = int(loc_id_str(1))
        score_count = int(loc_id_str(5))

        card_rows = all_cards[card_id]
        actual_rows = []

        # Ignore the zeros and get the item's name
        for row in rows:
            temp = []
            for n in row:
                if not n:
                    continue
                actual_item = itemlist.combine_number_name(number, itemlist.numbers[number])
                temp.append(actual_item)
            actual_rows.append(temp)

        # Set the rule for the location
        match score_type:
            case 6:
                # Decina Function
                set_rule(location, lambda state: check_decina(state, world.player, actual_rows))
            case 7:
                # Tombola Function
                single_list = []
                for row in actual_rows:
                    for n in row:
                        single_list.append(n)
                set_rule(location, lambda state: state.has_all(single_list, world.player))

            case _:
                # Ambo through Cinquina can be made in the same function
                set_rule(location, lambda state: state.has_from_list(rows[0], world.player, int(score_type))
                         or state.has_from_list(rows[1], world.player, int(score_type))
                         or state.has_from_list(rows[2], world.player, int(score_type)))


        # Get the i
       # for number in all_cards[card_id-1]:
            #item_name = itemlist.combine_number_name(number, itemlist.numbers[number])


def check_decina(self, state: CollectionState, player: int, rows) -> bool:
    counter = 0
    for row in rows:
        if (state.has_all(row, player)):
            counter += 1
            if counter == 2:
                return true
    return false


def set_completion_condition (world: APTombolaWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: ##TODO









