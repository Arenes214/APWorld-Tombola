
from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

from .data import itemlist
from . import cards, locations

if TYPE_CHECKING:
    from .world import APTombolaWorld

def set_all_rules(world: APTombolaWorld) -> None:

    all_cards = world.all_cards

    set_all_entrance_rules(world)
    set_all_location_rules(world, all_cards)
    set_completion_condition(world)


def set_all_entrance_rules(world: APTombolaWorld) -> None:
    if world.options.cardsanity:
        # Get entrance
        # set_rule(entrance, lamba: the rule)
        for card in world.cardsanity_to_lock:
            entrance = world.get_entrance(f"Look at Card {card}")
            set_rule(entrance, lambda state, card_l=card: state.has(f"Card {card_l} Unlock", world.player))

    return

def set_all_location_rules(world: APTombolaWorld, all_cards) -> None:

    # Set rules for all Card Score locations
    for loc_name, loc_id in locations.create_all_card_score_locations().items():
        location = world.get_location(loc_name)

        # Set Item Rule for location
        set_anti_meta_rule(world, location)

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

        # Set the access rule for the location, aka what numbers are needed
        match score_type:
            case 6:
                # Decina Function
                # This is probably dumb but it should at least work
                set_rule(location, lambda state, actual_rows_l=actual_rows: (state.has_from_list(actual_rows_l[0], world.player, 5)
                                                  and state.has_from_list(actual_rows_l[1], world.player, 5)
                                                  or state.has_from_list(actual_rows_l[0], world.player, 5)
                                                  and state.has_from_list(actual_rows_l[2], world.player, 5)
                                                  or state.has_from_list(actual_rows_l[1], world.player, 5)
                                                  and state.has_from_list(actual_rows_l[2], world.player, 5)),
                         )
            case 7:
                # Tombola Function
                single_list = []
                for row in actual_rows:
                    for n in row:
                        single_list.append(n)
                set_rule(location, lambda state, single_list_l=single_list: state.has_all(single_list_l, world.player))
                # Also set rule of Tombola Event
                event_location = world.get_location(f"EVENT: Card {card_id+1} - Tombola Scored")
                set_rule(event_location, lambda state, single_list_l=single_list: state.has_all(single_list_l, world.player))

            case _:
                # Ambo through Cinquina can be made in the same function
                score_type_int = int(score_type)
                set_rule(location, lambda state, actual_rows_l=actual_rows, n=score_type_int: (state.has_from_list(actual_rows_l[0], world.player, n)
                                                  or state.has_from_list(actual_rows_l[1], world.player, n)
                                                  or state.has_from_list(actual_rows_l[2], world.player, n)),
                        )

    # Set cardsanity unlock rules if they exist
    if world.options.cardsanity:
        for card in world.cardsanity_to_lock:
            location = world.get_location(f"Card {card} Unlocked")

            # Set item rule
            set_anti_meta_rule(world, location)

            # Set location rule
            set_rule(location, lambda state, card_l=card: state.has(f"Card {card_l} Unlock", world.player))

def set_anti_meta_rule(world: APTombolaWorld, location: APTombolaLocation):
        if world.options.prevent_other_meta_game_items:
            location.item_rule = lambda item: item.game != "AP Tombola" and item.game != "APBingo"
        else:
            location.item_rule = lambda item: item.game != "AP Tombola"

def set_completion_condition (world: APTombolaWorld) -> None:

    # Define rule for "Requirement Reached" locations
    tombola_goal_count = world.options.tombola_victory_count
    tombola_count_reached_loc = world.get_location("EVENT: Tombola Count Requirement Reached")
    set_rule(tombola_count_reached_loc, lambda state, c=tombola_goal_count: state.count("Tombola Scored", world.player) >= c)

    # Set Goal condition
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory Token", world.player)









