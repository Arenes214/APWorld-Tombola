from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, locations, regions, rules, cards, web_world
from .options import TombolaStartHints
from . import options as aptombola_options
from .data import itemlist

class APTombolaWorld(World):
    """
    AP Tombola is an AP implementation of Tombola, an italian bingo game dating back to 1734
    """

    game = "AP Tombola"

    web = web_world.APTombolaWebWorld()

    options_dataclass = aptombola_options.APTombolaOptions
    options: aptombola_options.APTombolaOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    item_name_groups = items.create_all_item_groups()

    origin_region_name = "The Table"

    cardsanity_to_lock = []

    def generate_early(self) -> None:
        # Extra clearing of the list so that the fuzzer does not shit itself
        self.cardsanity_to_lock.clear()

        # Choose Cardsanity Cards to lock
        if self.options.cardsanity:
            count = self.options.cardsanity
            cards = [i for i in range(1,7)]
            self.random.shuffle(cards)

            while (count > 0):
                self.cardsanity_to_lock.append(cards.pop())
                count -= 1

        # Add Starting Hints if needed
        print(f"Before the function, start_hints is: {self.options.start_hints}")

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


    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)
        print(f"At create_regions cardsanity_to_lock is {self.cardsanity_to_lock}")

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)
        print(f"At create_items cardsanity_to_lock is {self.cardsanity_to_lock}")

    def create_item(self, name: str) -> items.APTombolaItem:
        return items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    # There may be data that the game client will need to modify the behavior of the game.
    # This is what slot_data exists for. Upon every client connection, the slot's slot_data is sent to the client.
    # slot_data is just a dictionary using basic types, that will be converted to json when sent to the client.
    #def fill_slot_data(self) -> Mapping[str, Any]:
        # If you need access to the player's chosen options on the client side, there is a helper for that.
        #return self.options.as_dict(
        #    "hard_mode", "hammer", "extra_starting_chest", "confetti_explosiveness", "player_sprite"
        #)














