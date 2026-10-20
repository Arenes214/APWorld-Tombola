from collections.abc import Mapping
from collections import defaultdict, Counter
from typing import Any, TextIO

from worlds.AutoWorld import World
from Options import ProgressionBalancing, OptionError

from . import items, locations, regions, rules, cards, web_world
from .options import TombolaStartHints
from . import options as aptombola_options
from .data import itemlist, milestonelist

from BaseClasses import CollectionState, Item, MultiWorld

class APTombolaWorld(World):
    """
    AP Tombola is an AP implementation of Tombola, an italian bingo game dating back to 1734
    """

    game = "AP Tombola"
    genver = 4

    # Avoid 0.1 client
    required_client_version = (0,5,1)

    web = web_world.APTombolaWebWorld()

    options_dataclass = aptombola_options.APTombolaOptions
    options: aptombola_options.APTombolaOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    item_name_groups = items.create_all_item_groups()
    location_name_groups = locations.create_all_location_groups()

    origin_region_name = "The Table"

    all_cards = []
    milestones_chosen = []

    # Easy Links
    cards_linked = []
    force_extra_unlocks = False
    special_free_mark = defaultdict(bool)
    special_free_lochints = defaultdict(bool)
    special_shieldtrap = defaultdict(bool)
    trap_rng_seed = -1

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

        if hasattr(self.multiworld, "generation_is_fake"):
            if hasattr(self.multiworld, "re_gen_passthrough"):
                slot_data = self.multiworld.re_gen_passthrough["AP Tombola"]
                self.all_cards = slot_data["Cards"]
                self.milestones_chosen = slot_data["Milestones Chosen"]
                self.options.tombola_victory_count = slot_data["tombola_victory_count"]
                self.options.milestone_victory_count = slot_data["milestone_victory_count"]
                self.options.rowsanity = slot_data["rowsanity"]
                self.options.marksanity = slot_data["marksanity"]
        else:
           self.all_cards.clear()
           self.all_cards = cards.generate_cards(self)

           # Choose Milestones
           self.milestones_chosen.clear()
           self.milestones_chosen = locations.choose_milestone_locations(self)

    @classmethod
    def stage_generate_early(cls, multiworld: MultiWorld):
        # Easy Item Links
        
        problems = ["TombolaLink",
        "TombolaUnlockA","TombolaUnlockB","TombolaUnlockC",
        "TombolaMarksA","TombolaMarksB","TombolaMarksC",
        "TombolaHintsA","TombolaHintsB","TombolaHintsC",
        "TombolaShieldsA","TombolaShieldsB","TombolaShieldsC",
        "TombolaTrapsA","TombolaTrapsB","TombolaTrapsC",
        ]

        for link in multiworld.groups.values():
            if link["name"] in problems:
                raise OptionError(f"\n\nDetected Link Name \"{link["name"]}\" manually defined by players {link["players"]}."
                "\nPlease remove this Link from item_links and use the Easy Item Links option instead.\n")
        
        for (_,world) in multiworld.worlds.items():
            if world.player_name in problems:
                raise OptionError(f"\n\nDetected Player Name \"{world.player_name}\" that would interfere with Tombola Item Links."
                "\nPlease change the player name.\n")

        def add_group_fix_state(group_name: str, game, players: set, multiworld: MultiWorld, state: CollectionState, linked_items: set, replacement_items: dict):
            pass
            group_id, group = multiworld.add_group(
                group_name,
                game,
                players,
            )

            group["item_pool"] = linked_items

            group["replacement_items"] = replacement_items
            group["link_replacement"] = True

            group["local_items"] = set()
            group["non_local_items"] = set()

            # Fix State
            state.prog_items.setdefault(group_id, Counter())
            state.reachable_regions.setdefault(group_id, set())
            state.blocked_connections.setdefault(group_id, set())
            state.stale.setdefault(group_id, True)

        state = multiworld.state

        filler_replace = set()
        for (_,name) in itemlist.fillers:
            filler_replace.add(name)

        link_request = defaultdict(list)
        link_options = ["Numbers","Unlocks","Free Marks","Free Location Hints","Traps & Shields"]

        for tombola in multiworld.get_game_worlds(cls.game):
            for option in link_options:
                if option in tombola.options.easy_item_links:
                    if option == "Unlocks" and tombola.options.cardsanity == 0:
                        continue
                    link_request[option].append(tombola)
        
        for tombola in multiworld.get_game_worlds(cls.game):
            if tombola.options.item_links:
                raise OptionError(f"\n\nPlayer {multiworld.get_player_name(tombola.player)} has both Easy Item Links and normal Links defined."
                "\nPlease remove the normal Links.")
            
        if len(link_request["Numbers"]) >= 2:
            
            numbers = set()
            for (idx, name) in itemlist.numbers:
                numbers.add(itemlist.combine_number_name(idx,name))

            players_ids = set()
            for tombola_world in link_request["Numbers"]:
                players_ids.add(tombola_world.player)

            replacements = dict()
            for player_id in players_ids:
                pick = multiworld.random.choice(list(filler_replace))
                replacements[player_id] = pick
            
            add_group_fix_state("TombolaLink", cls.game, players_ids, multiworld, state, numbers, replacements)
              
        if len(link_request["Unlocks"]) >= 2:
            
            # we need to create more than 1 group, so first prepare all of the data
            # especially since groups can have different players due to amount of cards locked per player

            # world id -> amount of cards to lock
            lock_length = defaultdict(int)
            link_players = defaultdict(list)
            force_double = False

            for tombola in link_request["Unlocks"]:
                lock_length[tombola.player] = int(tombola.options.cardsanity)
                if tombola.options.additional_card_unlocks:
                    force_double = True
            
            # Can assume at least 1 will be linked, checked for Cardsanity 0 at the start

            card_id = [1,2,3,4,5,6]
            has_linked = defaultdict(list) # player -> cards linked

            still_link = True
            while still_link:
                card_picked = multiworld.random.choice(card_id)
                card_id.remove(card_picked)

                for player_id in lock_length.keys():
                    if lock_length[player_id] > 0:
                        link_players[card_picked].append(player_id)
                        has_linked[player_id].append(card_picked)
                        lock_length[player_id] -= 1
                
                count_unlinked = 0 # Numbers of players that still have cards to lock
                for (k,player_count) in lock_length.items():
                    if player_count > 0:
                        count_unlinked += 1
                
                if count_unlinked < 2:
                    still_link = False
                
                for key in has_linked.keys():
                    multiworld.worlds[key].cards_linked = has_linked[key]
                    if force_double:
                        multiworld.worlds[key].force_extra_unlocks = True
            
            #Create link
            for (card_id,player_list) in link_players.items():

                replacements = dict()
                for player_id in player_list:
                    pick = multiworld.random.choice(list(filler_replace))
                    replacements[player_id] = pick
                
                add_group_fix_state(f"TombolaUnlock{card_id}", cls.game, set(player_list), multiworld, state, [f"Card {card_id} Unlock"], replacements)

        if len(link_request["Free Marks"]) >= 2:

            # Players can have differing amount of Free Marks
            # In order to link them all, 3 different free mark items are defined
            # Calculate the groups from biggest to lowest

            tier_players = defaultdict(list)
            special_free_mark_per_player = defaultdict(lambda: defaultdict(list))

            for tombola in link_request["Free Marks"]:
                tier = 1
                tier_players[tier].append(tombola.player)
                if tombola.options.rowsanity:
                    tier += 1
                    tier_players[tier].append(tombola.player)
                if tombola.options.marksanity:
                    tier += 1
                    tier_players[tier].append(tombola.player)
            
            item_name = [0,"Free Mark!!!","Free Mark!!","Free Mark!"]
            name_letter = [0,"A","B","C"]
            string_id = 1
             
            for tier in tier_players.keys():
                if len(tier_players[tier]) <= 1:
                    continue
                for player_id in tier_players[tier]:
                    special_free_mark_per_player[player_id][tier] = True

                replacements = dict()
                for player_id in tier_players[tier]:
                    pick = multiworld.random.choice(list(filler_replace))
                    replacements[player_id] = pick

                add_group_fix_state("TombolaMarks"+name_letter[string_id], cls.game, set(tier_players[tier]),
                    multiworld, state, [item_name[string_id]], replacements)
                string_id += 1

                for player_id in special_free_mark_per_player.keys():
                    multiworld.worlds[player_id].special_free_mark = special_free_mark_per_player[player_id]

        if len(link_request["Free Location Hints"]) >= 2:
            # Same idea as Free Marks
            # Different Tiers to account for differing counts

            tier_players = defaultdict(list)
            special_free_lochint_per_player = defaultdict(lambda: defaultdict(list))

            for tombola in link_request["Free Location Hints"]:
                tier = 1
                tier_players[tier].append(tombola.player)
                if tombola.options.rowsanity:
                    tier += 1
                    tier_players[tier].append(tombola.player)
                if tombola.options.marksanity:
                    tier += 1
                    tier_players[tier].append(tombola.player)

            item_name = [0,"Free Location Hint!!!","Free Location Hint!!","Free Location Hint!"]
            name_letter = [0,"A","B","C"]
            string_id = 1

            for tier in tier_players.keys():
                if len(tier_players[tier]) <= 1:
                    continue
                for player_id in tier_players[tier]:
                    special_free_lochint_per_player[player_id][tier] = True

                replacements = dict()
                for player_id in tier_players[tier]:
                    pick = multiworld.random.choice(list(filler_replace))
                    replacements[player_id] = pick

                add_group_fix_state("TombolaHints"+name_letter[string_id], cls.game, set(tier_players[tier]),
                    multiworld, state, [item_name[string_id]], replacements)
                string_id += 1

                for player_id in special_free_lochint_per_player.keys():
                    multiworld.worlds[player_id].special_free_lochints = special_free_lochint_per_player[player_id]

        if len(link_request["Traps & Shields"]) >= 2:

            # Same as Free Marks

            tier_players = defaultdict(list)
            special_shieldtrap_per_player = defaultdict(lambda: defaultdict(list))

            # But also we need to have seed be the same for all players
            seed = multiworld.random.randint(1,214214214214)

            for tombola in link_request["Traps & Shields"]:
                tier = 1
                tier_players[tier].append(tombola.player)
                if tombola.options.rowsanity:
                    tier += 1
                    tier_players[tier].append(tombola.player)
                if tombola.options.marksanity:
                    tier += 1
                    tier_players[tier].append(tombola.player)

            item_name_shield = [0,"Anti-Trap Shield!!!","Anti-Trap Shield!!","Anti-Trap Shield!"]
            item_name_blind  = [0,"Blindness Trap!!!","Blindness Trap!!","Blindness Trap!"]
            item_name_lock  = [0,"Lock Trap!!!","Lock Trap!!","Lock Trap!"]
            name_letter = [0,"A","B","C"]
            string_id = 1
             
            for tier in tier_players.keys():
                if len(tier_players[tier]) <= 1:
                    continue
                for player_id in tier_players[tier]:
                    special_shieldtrap_per_player[player_id][tier] = True

                replacements = dict()
                for player_id in tier_players[tier]:
                    pick = multiworld.random.choice(list(filler_replace))
                    replacements[player_id] = pick
                
                add_group_fix_state("TombolaShields"+name_letter[string_id], cls.game, set(tier_players[tier]),
                    multiworld, state, [item_name_shield[string_id]], replacements)
                add_group_fix_state("TombolaTraps"+name_letter[string_id], cls.game, set(tier_players[tier]),
                    multiworld, state, [item_name_blind[string_id],item_name_lock[string_id]], replacements)
                string_id += 1
            
                for player_id in special_shieldtrap_per_player.keys():
                    multiworld.worlds[player_id].special_shieldtrap = special_shieldtrap_per_player[player_id]
                    multiworld.worlds[player_id].trap_rng_seed = seed




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

        to_send.update(self.options.as_dict("tombola_victory_count","milestone_victory_count","rowsanity","marksanity"))

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


        # Regular
        for loc_name, loc_id in locations.create_all_regular_card_score_locations().items():
            loc_id_str = str(loc_id)
            card_id = int(loc_id_str[0]) # ID is 1-indexed
            score_type = int(loc_id_str[1])
            card = all_cards_stripped[card_id-1]
            hint_string = ""
            match score_type:
                case 6:
                    hint_string = f"Unlock Card {card_id} and obtain ALL Numbers in any two of the following rows: {card}"
                case 7:
                    hint_string = f"Unlock Card {card_id} and obtain ALL Numbers in ALL of the following rows: {card}"
                case _:
                    hint_string = f"Unlock Card {card_id} and obtain {score_type} Numbers in any one of the following rows: {card}"

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

        # Rowsanity
        if self.options.rowsanity:
            for loc_name, loc_id in locations.create_all_rowsanity_score_locations().items():
                loc_id_str = str(loc_id)
                card_id = int(loc_id_str[0]) # ID is 1-indexed
                score_type = int(loc_id_str[1])
                card = all_cards_stripped[card_id-1]
                hint_string = ""

                match score_type:
                    case 6:
                        row_1 = int(loc_id_str[3])
                        row_2 = -1
                        if row_1 == 3: # Row 3
                            row_2 = 1
                        else:
                            row_2 = row_1 + 1
                        sanity_rows = []
                        sanity_rows.append(card[row_1-1])
                        sanity_rows.append(card[row_2-1])
                        hint_string = f"Unlock Card {card_id} and obtain ALL Numbers in both of the following rows: {sanity_rows}"

                    case _:
                        sanity_row = card[int(loc_id_str[3])-1]
                        hint_string = f"Unlock Card {card_id} and obtain {score_type} Numbers in the following row: {sanity_row}"

                working_data[loc_id] = hint_string

        # Marksanity
        if self.options.marksanity:
            for loc_name, loc_id in locations.create_all_marksanity_score_locations().items():
                loc_id_str = str(loc_id)
                number = int(loc_id_str[3])*10+int(loc_id_str[4])
                hint_string = f"Obtain the Number {number}"
                working_data[loc_id] = hint_string

        # Actually apply the hint extensions
        hint_data[self.player] = working_data


    #UT Stuff
    @staticmethod
    def interpret_slot_data(slot_data: dict[str,Any]) -> dict[str,Any]:
            return slot_data
        
    ut_can_gen_without_yaml = True













