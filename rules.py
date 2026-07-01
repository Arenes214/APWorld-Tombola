
from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState, ItemClassification, MultiWorld, Location
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import add_rule, set_rule

from .data import itemlist, milestonelist
from . import cards, locations

if TYPE_CHECKING:
    from .world import APTombolaWorld

class APTombolaTotalCount(LogicMixin):
    aptombola_total_count: dict[int, set[str]]
    aptombola_even_count: dict[int, set[str]]
    aptombola_odd_count: dict[int, set[str]]

    def init_mixin(self, multiworld: Multiworld) -> None:
        self.aptombola_total_count = {
            player: 0 for player in multiworld.get_game_players("AP Tombola")
        }

        self.aptombola_even_count = {
            player: 0 for player in multiworld.get_game_players("AP Tombola")
        }

        self.aptombola_odd_count = {
            player: 0 for player in multiworld.get_game_players("AP Tombola")
        }


    def copy_mixin(self, new_state: CollectionState) -> CollectionState:
        new_state.aptombola_total_count = {
            player: count for player, count in self.aptombola_total_count.items()
        }

        new_state.aptombola_even_count = {
            player: count for player, count in self.aptombola_even_count.items()
        }

        new_state.aptombola_odd_count = {
            player: count for player, count in self.aptombola_odd_count.items()
        }

        return new_state

def set_all_rules(world: APTombolaWorld) -> None:

    all_cards = world.all_cards

    set_all_entrance_rules(world)
    set_all_milestone_rules(world, all_cards)
    set_all_regular_location_rules(world, all_cards)

    if world.options.rowsanity:
        set_all_rowsanity_rules(world, all_cards)

    if world.options.marksanity:
        set_all_marksanity_rules(world)


    set_completion_condition(world)


def set_all_entrance_rules(world: APTombolaWorld) -> None:
    for card in range (1,7):
        entrance = world.get_entrance(f"Look at Card {card}")
        set_rule(entrance, lambda state, card_l=card: state.has(f"Card {card_l} Unlock", world.player))

    return

def set_all_regular_location_rules(world: APTombolaWorld, all_cards) -> None:

    # Set rules for all Card Score locations
    for loc_name, loc_id in locations.create_all_regular_card_score_locations().items():
        location = world.get_location(loc_name)

        # Set Item Rule for location
        set_anti_meta_rule(world, location)

        # Get the type of location it is by its ID
        # TODO This wouldn't work in a future where there are more than 9 cards
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
                # This is dumb but it should at least work
                set_rule(location, lambda state, actual_rows_l=actual_rows: (state.has_from_list(actual_rows_l[0], world.player, 5)
                                                  and state.has_from_list(actual_rows_l[1], world.player, 5)
                                                  or state.has_from_list(actual_rows_l[0], world.player, 5)
                                                  and state.has_from_list(actual_rows_l[2], world.player, 5)
                                                  or state.has_from_list(actual_rows_l[1], world.player, 5)
                                                  and state.has_from_list(actual_rows_l[2], world.player, 5)),
                         )

                # Set rule for Decina Event
                event_location = world.get_location(f"EVENT: Card {card_id+1} - Decina Scored")
                set_rule(event_location, lambda state, actual_rows_l=actual_rows: (state.has_from_list(actual_rows_l[0], world.player, 5)
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

                # Set rule of Tombola Event
                event_location = world.get_location(f"EVENT: Card {card_id+1} - Tombola Scored")
                set_rule(event_location, lambda state, single_list_l=single_list: state.has_all(single_list_l, world.player))

            case _:
                # Ambo through Cinquina can be made in the same function
                score_type_int = int(score_type)
                set_rule(location, lambda state, actual_rows_l=actual_rows, n=score_type_int: (state.has_from_list(actual_rows_l[0], world.player, n)
                                                  or state.has_from_list(actual_rows_l[1], world.player, n)
                                                  or state.has_from_list(actual_rows_l[2], world.player, n)),
                        )

                # Set rule for Event
                all_possible_scores = ["Ambo","Terno","Quaterna","Cinquina"]
                score_name = all_possible_scores[score_type_int-2]

                event_location = world.get_location(f"EVENT: Card {card_id+1} - {score_name} Scored")

                set_rule(event_location, lambda state, actual_rows_l=actual_rows, n=score_type_int: (state.has_from_list(actual_rows_l[0], world.player, n)
                                                  or state.has_from_list(actual_rows_l[1], world.player, n)
                                                  or state.has_from_list(actual_rows_l[2], world.player, n)),
                        )

    # Set  unlock rules
    for card in range(1,7):
        location = world.get_location(f"Card {card} Unlocked")

        # Set item rule
        set_anti_meta_rule(world, location)

        # Set location rule
        set_rule(location, lambda state, card_l=card: state.has(f"Card {card_l} Unlock", world.player))

def set_all_rowsanity_rules(world: APTombolaWorld, all_cards) -> None:
    # Yes this is duplicated code
    for loc_name, loc_id in locations.create_all_rowsanity_score_locations().items():
        location = world.get_location(loc_name)

        # Set Item Rule for location
        set_anti_meta_rule(world, location)

        # Get the type of location it is by its ID
        # TODO This wouldn't work in a future where there are more than 9 cards
        loc_id_str = str(loc_id)
        card_id = int(loc_id_str[0]) - 1
        score_type = int(loc_id_str[1])
        score_discriminator = int(loc_id_str[3])

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

            match score_type:
                case 6: # DECINA
                    other_row = 0
                    if score_discriminator == 3:
                        other_row = 1
                    else:
                        other_row = score_discriminator + 1
                    set_rule(location, lambda state, actual_rows_l=actual_rows, dis=score_discriminator-1, other_row_l = other_row-1: state.has_from_list(actual_rows_l[dis], world.player, 5) and state.has_from_list(actual_rows_l[other_row_l], world.player, 5))

                case _:
                    score_type_int = int(score_type)
                    set_rule(location, lambda state, actual_rows_l=actual_rows, n=score_type_int, dis=score_discriminator-1: state.has_from_list(actual_rows_l[dis], world.player, n))

def set_all_milestone_rules(world: APTombolaWorld, all_cards):
    all_scores = ["Ambo","Terno","Quaterna","Cinquina","Decina","Tombola"]
    for loc_name, loc_id in world.milestones_chosen:
        location = world.get_location(loc_name)
        event_location = world.get_location(f"EVENT: {loc_name} Achieved")
        # Set Item Rule for location
        set_anti_meta_rule(world, location)

        loc_id_str = str(loc_id)
        score_type = loc_id_str[1]

        match int(score_type):
            case 1: # Score Collect
                score_type_id = int(loc_id_str[2])
                score_type = all_scores[score_type_id-2]
                score_count = loc_id_str[3]
                set_rule(location, lambda state, count_l=int(score_count),score_l=score_type: state.count(f"{score_l} Scored", world.player) >= count_l)

                # Set Rule for Event
                set_rule(event_location, lambda state, count_l=int(score_count),score_l=score_type: state.count(f"{score_l} Scored", world.player) >= count_l)

            case 2: # Collections of Numbers
                numbers = []
                for item in milestonelist.collections:
                    if item[0] == loc_name:
                        for idx in item[2]:
                            actual_item = itemlist.combine_number_name(idx, itemlist.numbers[idx-1][1])
                            numbers.append(actual_item)

                set_rule(location, lambda state, numbers_l=numbers: state.has_all(numbers_l, world.player))

                # Set Rule for Event
                set_rule(event_location, lambda state, numbers_l=numbers: state.has_all(numbers_l, world.player))


            case 3: # Total Count
                target = 0
                for item in milestonelist.total_counts:
                    if item[0] == loc_name:
                        target = item[2]
                        break
                set_rule(location, lambda state, target_l = target: state.aptombola_total_count[world.player] >= target_l)

                # Event
                set_rule(event_location, lambda state, target_l = target: state.aptombola_total_count[world.player] >= target_l)

            case 4: # Even/Odd
                even_or_odd = int(loc_id_str[2]) % 2
                target = (int(loc_id_str[3])*10) + int(loc_id_str[4])

                if even_or_odd == 1: #
                    set_rule(location, lambda state, target_l=target: state.aptombola_odd_count[world.player] >= target_l)
                    set_rule(event_location, lambda state, target_l=target: state.aptombola_odd_count[world.player] >= target_l)
                else:
                    set_rule(location, lambda state, target_l=target: state.aptombola_even_count[world.player] >= target_l)
                    set_rule(event_location, lambda state, target_l=target: state.aptombola_even_count[world.player] >= target_l)

def set_all_marksanity_rules(world: APTombolaWorld):
    for loc_name, loc_id in locations.create_all_marksanity_score_locations().items():
        location = world.get_location(loc_name)
        set_anti_meta_rule(world, location)

        number = loc_id - 80000
        set_rule(location, lambda state, n=number: state.has(itemlist.combine_number_name(n, itemlist.numbers[n-1][1]), world.player))



def set_anti_meta_rule(world: APTombolaWorld, location: APTombolaLocation):
    if location.item_rule is Location.item_rule: # empty rule
        if world.options.prevent_other_meta_game_items:
            location.item_rule = lambda item: (not (item.game == "AP Tombola" and item.classification == ItemClassification.progression) and item.game != "APBingo")
        else:
            location.item_rule = lambda item: (not (item.game == "AP Tombola" and item.classification == ItemClassification.progression))
    else:
        if world.options.prevent_other_meta_game_items:
            location.item_rule = lambda item, old_rule=location.item_rule: (not (item.game == "AP Tombola" and item.classification == ItemClassification.progression) and item.game != "APBingo") and old_rule(item)
        else:
            location.item_rule = lambda item,old_rule=location.item_rule: (not (item.game == "AP Tombola" and item.classification == ItemClassification.progression)) and old_rule(item)

def set_completion_condition (world: APTombolaWorld) -> None:

    # Define rule for "Requirement Reached" locations
    tombola_goal_count = world.options.tombola_victory_count
    tombola_count_reached_loc = world.get_location("EVENT: Tombola Count Requirement Reached")
    set_rule(tombola_count_reached_loc, lambda state, c=tombola_goal_count: state.count("Tombola Scored", world.player) >= c)

    milestone_goal_count = world.options.milestone_victory_count
    milestone_count_reached_loc = world.get_location("EVENT: Milestone Count Requirement Reached")
    set_rule(milestone_count_reached_loc, lambda state, c=milestone_goal_count: state.count("Milestone Achieved", world.player) >= c)

    # Set Goal condition
    all_requirements = world.get_location("EVENT: All Goal Requirements Reached")
    set_rule(all_requirements, lambda state: state.count("Victory Token", world.player) >= 2 ) # TODO HARDCODED

    world.multiworld.completion_condition[world.player] = lambda state: state.has("SLOT GOALED", world.player)









