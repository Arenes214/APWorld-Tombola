from collections.abc import Mapping
from typing import Any, TextIO

from worlds.AutoWorld import World
from Options import ProgressionBalancing

from . import items, locations, regions, rules, cards, web_world
from .options import TombolaStartHints
from . import options as aptombola_options
from .data import itemlist, milestonelist

from BaseClasses import CollectionState, Item

class APTombolaWorld(World):
    """
    AP Tombola is an AP implementation of Tombola, an italian bingo game dating back to 1734
    """

    game = "AP Tombola"
    genver = 3

    web = web_world.APTombolaWebWorld()

    options_dataclass = aptombola_options.APTombolaOptions
    options: aptombola_options.APTombolaOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    item_name_groups = items.create_all_item_groups()

    origin_region_name = "The Table"

    all_cards = []
    milestones_chosen = []

    def collect(self, state: CollectionState, item: Item) -> bool:
        change = super().collect(state, item)
        if item.code is not None:
            if change and item.code >=1 and item.code <= 90:
                state.aptombola_total_count[self.player] += item.code

                if item.code % 2 == 0:
                    state.aptombola_even_count[self.player] += 1
                else:
                    state.aptombola_odd_count[self.player] += 1
        return change

    def remove(self, state: CollectionState, item: Item) -> bool:
        change = super().remove(state, item)
        if not (item.code is None):
            if change and item.code >= 1 and item.code <= 90:
                state.aptombola_total_count[self.player] -= item.code

                if item.code % 2 == 0:
                    state.aptombola_even_count[self.player] -= 1
                else:
                    state.aptombola_odd_count[self.player] -= 1
        return change


    def generate_early(self) -> None:
        # Forge ProgBal to 0
        self.options.progression_balancing = ProgressionBalancing(0)

        # Add Starting Hints if needed

        if self.options.automatic_number_hints:
            to_hint = []
            intermidiate_step = str(self.options.start_hints)
            already_prehinted = intermidiate_step[intermidiate_step.find("(")+1: -1]
            if (already_prehinted):
                for i in already_prehinted.split(","):
                    to_hint.append(i.strip())

            for item in itemlist.numbers:
                to_hint.append(itemlist.combine_number_name(item[0],item[1]))
            self.options.start_hints = TombolaStartHints(to_hint)

        # Create the Cards
        self.all_cards.clear()
        self.all_cards = cards.generate_cards(self)

        # Choose Milestones
        self.milestones_chosen.clear()
        self.milestones_chosen = locations.choose_milestone_locations(self)


    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.APTombolaItem:
        return items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def write_spoiler_header(self, spoiler_handle:TextIO):
        spoiler_handle.write(f"\nTombola Cards:\n")
        for card_id, card in enumerate(self.all_cards):
            spoiler_handle.writelines(f"Card {card_id+1}:")
            for row in card:
                elements = []
                for n in row:
                    if not n == 0:
                        elements.append(n)
                spoiler_handle.writelines(f"{elements} ")
            spoiler_handle.write("\n")


    def fill_slot_data(self) -> dict[str, Any]:
        to_send = {}
        to_send["Genver"] = self.genver
        to_send["Cards"] = self.all_cards

        to_send["All Milestones"] = locations.create_all_milestone_score_locations()

        to_send["All Collection of Numbers Milestones"] = milestonelist.collections
        to_send["All Total Count Milestones"] = milestonelist.total_counts # these 2 i have to do to also get the "targets"

        to_send["Milestones Chosen"] = self.milestones_chosen

        to_send.update(self.options.as_dict("tombola_victory_count","milestone_victory_count","cardsanity"))

        return to_send

    def extend_hint_information(self, hint_data):
        working_data = {}
        all_cards_stripped = []
        for card in self.all_cards:
            card_stripped = []
            for row in card:
                row_stripped = []
                for n in row:
                    if not n == 0:
                        row_stripped.append(n)
                card_stripped.append(row_stripped)
            all_cards_stripped.append(card_stripped)

        print(f"DEBUG stripped: {all_cards_stripped}")

        # Regular
        for loc_name, loc_id in locations.create_all_regular_card_score_locations().items():
            loc_id_str = str(loc_id)
            card_id = int(loc_id_str[0]) # ID is 1-indexed
            score_type = int(loc_id_str[1])
            card = all_cards_stripped[card_id-1]
            hint_string = ""
            match score_type:
                case 6:
                    hint_string = f"Unlock Card {card_id} and Get ALL Numbers in any two of the following rows: {card}"
                case 7:
                    hint_string = f"Unlock Card {card_id} and Get ALL Numbers in ALL of the following rows: {card}"
                case _:
                    hint_string = f"Unlock Card {card_id} and Get {score_type} Numbers in any one of the following rows: {card}"
            working_data[loc_id] = hint_string

        # Milestones
        for milestone_name, milestone_id in self.milestones_chosen:
            milestone_id_str = str(milestone_id)
            score_type = int(milestone_id_str[1])
            hint_string = ""

            match score_type:
                case 1:
                    collect_type = int(milestone_id_str[2])
                    collect_count = int(milestone_id_str[3])
                    collect_strings = ["Ambo","Terno","Quaterna","Cinquina"]

                    match collect_type:
                        case 7:
                            hint_string = f"Score a Tombola in {collect_count} Cards (Getting ALL Numbers in ALL rows of a Card)"
                        case 6:
                            hint_string = f"Score a Decina in {collect_count} Cards (Getting ALL Numbers in two out of three rows of a Card)"
                        case _:
                            hint_string = f"Score a {collect_strings[collect_type-2]} in {collect_count} Cards (Getting {collect_type} Numbers in any one row of a Card)"

                case 2:
                    numbers_list = []
                    for canditate in milestonelist.collections:
                        if canditate[1] == milestone_id:
                            numbers_list = canditate[2]
                            break
                    hint_string = f"Obtain ALL of the following numbers: {numbers_list}"

                case 3:
                    total_count = 0
                    for canditate in milestonelist.total_counts:
                        if canditate[1] == milestone_id:
                            total_count = canditate[2]
                            break
                    hint_string = f"Get the Sum of all Numbers received to {total_count} or greater"

                case 4:
                    even_or_odd = int(milestone_id_str[2])
                    if even_or_odd % 2 == 0: # Even
                        hint_string = f"Obtain {(int(milestone_id_str[3])*10+int(milestone_id_str[4]))} even Numbers"
                    else:
                        hint_string = f"Obtain {(int(milestone_id_str[3])*10+int(milestone_id_str[4]))} odd Numbers"

            working_data[milestone_id] = hint_string

        # Actually apply the hint extensions
        hint_data[self.player] = working_data
















