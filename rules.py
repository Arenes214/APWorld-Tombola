
from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

from .data import itemlist
from . import cards

if TYPE_CHECKING:
    from .world import APTombolaWorld

def set_all_rules(world: APTombolaWorld) -> None:

    all_cards = cards.generate_cards(world)

    set_all_entrance_rules(world)
    set_all_location_rules(world, all_cards)
    # set_completion_condition(world)


def set_all_entrance_rules(world: APTombolaWorld) -> None:
    # Currently all regions are just accessible, this may be used later for "cardsanity" aka locked cards
    return

def set_all_location_rules(world: APTombolaWorld, all_cards) -> None:

    # Go through all Card locations
    for loc_name, loc_id in world.location_name_to_id.items():
        if loc_id < 10000:
            continue # Skip all non-card
        location = world.get_location(loc_name)

        # Get the type of location it is by its ID
        # TODO This won't work in a future where there are more than 9 cards
        loc_id_str = str(loc_id)
        card_id = int(loc_id_str[0]) - 1
        score_type = int(loc_id_str[1])
        score_count = int(loc_id_str[4])

        # Get the corresponding card's rows
        card_rows = all_cards[card_id]
        actual_rows = []

        # Ignore the zeros and get the item's name
        for row in card_rows:
            temp = []
            for n in row:
                if not n:
                    continue
                actual_item = itemlist.combine_number_name(n, itemlist.numbers[n-1][1])
                temp.append(actual_item)
            actual_rows.append(temp)

        # Set the rule for the location
        match score_type:
            case 6:
                # Decina Function
                # This is probably dumb but it should at least work
                set_rule(location, lambda state: (state.has_from_list(actual_rows[0], world.player, 5)
                                                  and state.has_from_list(actual_rows[1], world.player, 5)
                                                  or state.has_from_list(actual_rows[0], world.player, 5)
                                                  and state.has_from_list(actual_rows[2], world.player, 5)
                                                  or state.has_from_list(actual_rows[1], world.player, 5)
                                                  and state.has_from_list(actual_rows[2], world.player, 5)),
                         )
            case 7:
                # Tombola Function
                single_list = []
                for row in actual_rows:
                    for n in row:
                        single_list.append(n)
                set_rule(location, lambda state: state.has_all(single_list, world.player))

            case _:
                # Ambo through Cinquina can be made in the same function
                set_rule(location, lambda state: state.has_from_list(actual_rows[0], world.player, int(score_type))
                         or state.has_from_list(actual_rows[1], world.player, int(score_type))
                         or state.has_from_list(actual_rows[2], world.player, int(score_type)))

#def set_completion_condition (world: APTombolaWorld) -> None:
    #world.multiworld.completion_condition[world.player] = lambda state: ##TODO









