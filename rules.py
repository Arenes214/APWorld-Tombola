
from __future__ import annotations

import dataclasses


from typing import TYPE_CHECKING, override

from BaseClasses import CollectionState, ItemClassification, MultiWorld, Location
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import add_rule, set_rule
from rule_builder.rules import AtLeast, HasFromListUnique, Has, HasAll, And, Or, Rule
from NetUtils import JSONMessagePart

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
        world.set_rule(entrance, Has(f"Card {card} Unlock"))

    return

def set_all_regular_location_rules(world: APTombolaWorld, all_cards) -> None:

    # Set rules for all Card Score locations
    for loc_name, loc_id in locations.create_all_regular_card_score_locations().items():
        location = world.get_location(loc_name)

        # Set Item Rule for location
        set_anti_meta_rule(world, location)

        # Get the type of location it is by its ID
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
                world.set_rule(location, AtLeast(2,
                    HasFromListUnique(*actual_rows[0], count=5),
                    HasFromListUnique(*actual_rows[1], count=5),
                    HasFromListUnique(*actual_rows[2], count=5)))

                # Set rule for Decina Event
                event_location = world.get_location(f"EVENT: Card {card_id+1} - Decina Scored")
                world.set_rule(event_location, AtLeast(2,
                    HasFromListUnique(*actual_rows[0], count=5),
                    HasFromListUnique(*actual_rows[1], count=5),
                    HasFromListUnique(*actual_rows[2], count=5)))
         
            case 7:
                # Tombola Function
                single_list = []
                for row in actual_rows:
                    for n in row:
                        single_list.append(n)
                world.set_rule(location, HasAll(*single_list))

                # Set rule of Tombola Event
                event_location = world.get_location(f"EVENT: Card {card_id+1} - Tombola Scored")
                world.set_rule(event_location, HasAll(*single_list))

            case _:
                # Ambo through Cinquina can be made in the same function
                score_type_int = int(score_type)
                world.set_rule(location, AtLeast(1,
                    HasFromListUnique(*actual_rows[0], count=score_type_int),
                    HasFromListUnique(*actual_rows[1], count=score_type_int),
                    HasFromListUnique(*actual_rows[2], count=score_type_int),
                    ))

                # Set rule for Event
                all_possible_scores = ["Ambo","Terno","Quaterna","Cinquina"]
                score_name = all_possible_scores[score_type_int-2]

                event_location = world.get_location(f"EVENT: Card {card_id+1} - {score_name} Scored")

                world.set_rule(event_location, AtLeast(1,
                    HasFromListUnique(*actual_rows[0], count=score_type_int),
                    HasFromListUnique(*actual_rows[1], count=score_type_int),
                    HasFromListUnique(*actual_rows[2], count=score_type_int),
                    ))

    # Set  unlock rules
    for card in range(1,7):
        location = world.get_location(f"Card {card} Unlocked")

        # Set item rule
        set_anti_meta_rule(world, location)

        # Set location rule
        world.set_rule(location, Has(f"Card {card} Unlock"))


def set_all_rowsanity_rules(world: APTombolaWorld, all_cards) -> None:
    # Yes this is duplicated code
    for loc_name, loc_id in locations.create_all_rowsanity_score_locations().items():
        location = world.get_location(loc_name)

        # Set Item Rule for location
        set_anti_meta_rule(world, location)

        # Get the type of location it is by its ID
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

                world.set_rule(location, And(
                        HasAll(*actual_rows[score_discriminator-1]),
                        HasAll(*actual_rows[other_row-1])
                        )
                        )

            case _:
                score_type_int = int(score_type)
                world.set_rule(location, HasFromListUnique(*actual_rows[score_discriminator-1], count=score_type_int))

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
                world.set_rule(location, Has(f"{score_type} Scored", count=int(score_count)))

                # Set Rule for Event
                world.set_rule(event_location, Has(f"{score_type} Scored", count=int(score_count)))

            case 2: # Collections of Numbers
                numbers = []
                for item in milestonelist.collections:
                    if item[0] == loc_name:
                        for idx in item[2]:
                            actual_item = itemlist.combine_number_name(idx, itemlist.numbers[idx-1][1])
                            numbers.append(actual_item)

                world.set_rule(location, HasAll(*numbers))

                # Set Rule for Event
                world.set_rule(event_location, HasAll(*numbers))



            case 3: # Total Count
                target = 0
                for item in milestonelist.total_counts:
                    if item[0] == loc_name:
                        target = item[2]
                        break
                #set_rule(location, lambda state, target_l = target: state.aptombola_total_count[world.player] >= target_l)
                world.set_rule(location, TMBCountAtLeast(target,"Sum"))

                # Event
                #set_rule(event_location, lambda state, target_l = target: state.aptombola_total_count[world.player] >= target_l)
                world.set_rule(event_location, TMBCountAtLeast(target,"Sum"))

            case 4: # Even/Odd
                even_or_odd = int(loc_id_str[2]) % 2
                target = (int(loc_id_str[3])*10) + int(loc_id_str[4])

                if even_or_odd == 1: #
                    # set_rule(location, lambda state, target_l=target: state.aptombola_odd_count[world.player] >= target_l)
                    # set_rule(event_location, lambda state, target_l=target: state.aptombola_odd_count[world.player] >= target_l)
                    world.set_rule(location,TMBCountAtLeast(target,"Odd"))
                    world.set_rule(event_location,TMBCountAtLeast(target,"Odd"))


                else:
                    world.set_rule(location,TMBCountAtLeast(target,"Even"))
                    world.set_rule(event_location,TMBCountAtLeast(target,"Even"))

def set_all_marksanity_rules(world: APTombolaWorld):
    for loc_name, loc_id in locations.create_all_marksanity_score_locations().items():
        location = world.get_location(loc_name)
        set_anti_meta_rule(world, location)

        number = loc_id - 80000
        #set_rule(location, lambda state, n=number: state.has(itemlist.combine_number_name(n, itemlist.numbers[n-1][1]), world.player))
        world.set_rule(location,Has(itemlist.combine_number_name(number,itemlist.numbers[number-1][1])))


def set_anti_meta_rule(world: APTombolaWorld, location: APTombolaLocation):
    if location.item_rule is Location.item_rule: # empty rule
        if world.options.prevent_other_meta_game_items:
            location.item_rule = lambda item: (not (item.game == "AP Tombola" and item.advancement) and item.game != "APBingo")
        else:
            location.item_rule = lambda item: (not (item.game == "AP Tombola" and item.advancement == ItemClassification.progression))
    else:
        if world.options.prevent_other_meta_game_items:
            location.item_rule = lambda item, old_rule=location.item_rule: (not (item.game == "AP Tombola" and item.advancement == ItemClassification.progression) and item.game != "APBingo") and old_rule(item)
        else:
            location.item_rule = lambda item,old_rule=location.item_rule: (not (item.game == "AP Tombola" and item.advancement == ItemClassification.progression)) and old_rule(item)

def set_completion_condition (world: APTombolaWorld) -> None:

    # Define rule for "Requirement Reached" locations
    tombola_goal_count = int(world.options.tombola_victory_count)
    tombola_count_reached_loc = world.get_location("EVENT: Tombola Count Requirement Reached")
    #set_rule(tombola_count_reached_loc, lambda state, c=tombola_goal_count: state.count("Tombola Scored", world.player) >= c)
    world.set_rule(tombola_count_reached_loc,Has("Tombola Scored",count=tombola_goal_count))

    milestone_goal_count = int(world.options.milestone_victory_count)
    milestone_count_reached_loc = world.get_location("EVENT: Milestone Count Requirement Reached")
    #set_rule(milestone_count_reached_loc, lambda state, c=milestone_goal_count: state.count("Milestone Achieved", world.player) >= c)
    world.set_rule(milestone_count_reached_loc, Has("Milestone Achieved",count=milestone_goal_count))

    # Set Goal condition
    all_requirements = world.get_location("EVENT: All Goal Requirements Reached")
    #set_rule(all_requirements, lambda state: state.count("Victory Token", world.player) >= 2 )
    world.set_rule(all_requirements, Has("Victory Token", count=2))

    #world.multiworld.completion_condition[world.player] = lambda state: state.has("SLOT GOALED", world.player)
    world.set_completion_rule(Has("SLOT GOALED"))


# Rule Builder Stuff

@dataclasses.dataclass
class TMBCountAtLeast(Rule["APTombolaWorld"], game="AP Tombola"):
    target: int
    count_type: str

    @override
    def _instantiate(self, world: "APTombolaWorld") -> Rule.Resolved:
        return self.Resolved(self.target, self.count_type, player=world.player)

    class Resolved(Rule.Resolved):
        target: int
        count_type: str

        @override
        def _evaluate(self, state:CollectionState) -> bool:
            match self.count_type:
                case "Odd":
                    return state.aptombola_odd_count[self.player] >= self.target
                case "Even":
                    return state.aptombola_even_count[self.player] >= self.target
                case "Sum":
                    return state.aptombola_total_count[self.player] >= self.target
        
        @override
        def explain_json(self, state:CollectionState | None = None) -> list[JSONMessagePart]:

            start: str
            color: str
            greater_string: str

            if self.count_type == "Odd" or self.count_type == "Even":
                start = f"Amount of {self.count_type} Numbers "
            elif self.count_type == "Sum":
                start = "Sum of all Numbers "
            
            if state is None:
                color = "Yellow"
                greater_string = "needs to be Equal or Greater "
            else:
                greater: bool
                
                match self.count_type:
                    case "Odd":
                        greater = state.aptombola_odd_count[self.player] >= self.target
                        start = start + "(" + str(state.aptombola_odd_count[self.player]) + ") is "
                    case "Even":
                        greater = state.aptombola_even_count[self.player] >= self.target
                        start = start + "(" + str(state.aptombola_even_count[self.player]) + ") is "
                        
                    case "Sum":
                        greater = state.aptombola_total_count[self.player] >= self.target
                        start = start + "(" + str(state.aptombola_total_count[self.player]) + ") is "
                
                if greater:
                    color = "green"
                    greater_string = "Equal or Greater "
                else:
                    color = "salmon"
                    greater_string = "Not Equal or Greater "
            
            return [
                {"type":"text", "text":start},
                {"type":"color","color":color,"text":greater_string},
                {"type":"text","text":f"than {self.target}"}
            ]

