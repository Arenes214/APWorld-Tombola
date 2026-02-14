from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, locations, options, regions, rules

class APTombolaWorld(World):
    """
    AP Tombola is an AP implementation of Tombola, an italian bingo game dating back to 1734
    """

    game = "AP Tombola"


    options_dataclass = options.APTombolaOptions
    options: options.APTombolaOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = "The Table"

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)
# TODO UNDO THE COMMENT, THIS IS FOR TEST ONLY
    #def set_rules(self) -> None:
        #rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

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


    # Card Generation
    def generate_cards():
        # Create and shuffle numbers
        sheet_columns = {
            0: list(range(1,10)),
            1: list(range(10,20)),
            2: list(range(20,30)),
            3: list(range(30, 40)),
            4: list(range(40, 50)),
            5: list(range(50, 60)),
            6: list(range(60, 70)),
            7: list(range(70, 80)),
            8: list(range(80, 91)), # Last columns includes 90
        }

        for i in sheet_columns:
            world.random.shuffle(sheet_columns[i])

        # Get the numbers for each card
        all_card_numbers = []

        # For each card get the first 9 numbers from each column to follow the "at least one per column" rule
        for card in range(6):
            card_numbers = []

            for col in range(9):
                n = sheet_columns[col].pop()
                card_numbers.append((col, n))
                # Column count is not needed here since it will be 1 for each column
            all_card_numbers.append(card_numbers)

        # Now we can take the remaining numbers to have 15 per Card

        #BUG: There is a possibility that later loops won't have enough columns to take from and will infinite loop
        #TODO FIX this
        for card_numbers in all_card_numbers:
            col_count = defaultdict(lambda:1) # Create the column count at 1 since there is guaranteed exact 1 per column

            while (len(card_numbers) < 15):
                col = world.random.randint(0,8)

                if col_count[col] >=3: # Don't take if we already have 3 in column
                    continue
                if not sheet_columns[col]: # And seriously don't try to take from an empty column
                    continue

                n = sheet_columns[col].pop()
                card_numbers.append((col, n))
                col_count[col] += 1

        # Now that i have all of the cards' numbers, create the cards
        cards = []

        # And populate them
        for card_numbers in all_card_numbers:
            card = [[0] * 9 for _ in range (3)]
            row_count = [0,0,0] # Create the row count for the "5 per row"" rule

            for (col, n) in card_numbers:
                possible_rows = [r for r in range(3) if row_count[r] < 5]
                row = world.random.choice(possible_rows)
                card[row][col] = n
                row_count[row] += 1

            # After poplulating them, order the columns
            for col in range (9):
                col_sorted = [card[row][col] for row in range(3) if card[row][col] != 0]
                col_sorted.sort()

                i = 0 # index of col_sorted basically
                for row in range(3):
                    if card[row][col] != 0:
                        card[row][col] = col_sorted[i]
                        i += 1
            # After doing everything add the card to cards
            cards.append(card)

        return cards

    cards = generate_cards()

