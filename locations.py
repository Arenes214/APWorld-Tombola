from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items

if TYPE_CHECKING:
    from .world import APTombolaWorld

from collections import defaultdict


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


# Later i'll maybe make the number of rewards changeable, this should save me a bit of time then
AMBO_REWARD_COUNT_MAX = 1
TERNO_REWARD_COUNT_MAX = 2
QUATERNA_REWARD_COUNT_MAX = 2
CINQUINA_REWARD_COUNT_MAX = 3
DECINA_REWARD_COUNT_MAX = 3
TOMBOLA_REWARD_COUNT_MAX = 4

# Location id - Cards will be 5 digit (Format CS00N)
# C indicates Card (e.g. 3xxxx is card 3)
# S indicates which score it is (2 Ambo, 3 Terno, ..., 6 Decina, 7 Tombola)
# N indicates for multiple score rewards which one it is
# e.g. 24003 indicates Card 2, Score Quaterna, third reward

def all_locations_to_id():
    the_list = {}

    for card in range(6):
        for i in range(AMBO_REWARD_COUNT_MAX): # Ambo locations
            the_list[f"Card {card+1} - Ambo Reward {i+1}"] = (10000*(card+1))+2000+i+1

        for i in range (TERNO_REWARD_COUNT_MAX): # Terno locations
            the_list[f"Card {card+1} - Terno Reward {i+1}"] = (10000*(card+1))+3000+i+1

        for i in range (QUATERNA_REWARD_COUNT_MAX): # Quaterna locations
            the_list[f"Card {card+1} - Quaterna Reward {i+1}"] = (10000*(card+1))+4000+i+1

        for i in range (CINQUINA_REWARD_COUNT_MAX): # Cinquina locations
            the_list[f"Card {card+1} - Cinquina Reward {i+1}"] = (10000*(card+1))+5000+i+1

        for i in range (DECINA_REWARD_COUNT_MAX): # Decina locations
            the_list[f"Card {card+1} - Decina Reward {i+1}"] = (10000*(card+1))+6000+i+1

        for i in range (TOMBOLA_REWARD_COUNT_MAX): # Tombola locations
            the_list[f"Card {card+1} - Tombola Reward {i+1}"] = (10000*(card+1))+7000+i+1

    return the_list

# Create the list with ids to mimic APQuest behaviour
LOCATION_NAME_TO_ID = all_locations_to_id()

class APTombolaLocation(Location):
    game = "AP Tombola"

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}

def create_all_locations(world: APTombolaWorld) -> None:
    create_regular_locations(world)
    create_events(world)

def create_regular_locations(world: APTombolaWorld) -> None:
    # Get the regions
    # Card 1 is index **1** since index 0 will be the starting regions
    regions = []
    regions.append(world.get_region("The Table"))
    for i in range (1,7):
        regions.append(world.get_region(f"Card {i}"))


    for key, value in LOCATION_NAME_TO_ID.items():
        # TODO When options can change the amount there will need to be some logic here
        # For now just create all of them
        if value >= 10000: # Check for the range of ids that are Card locations
            region_index = value // 10000
            # Probably wacky since i already got the id but might as well just follow APQuest for now
            loc = get_location_names_with_ids([key])
            regions[region_index].add_locations(loc, APTombolaLocation)

def create_events(world: APTombolaWorld) -> None:
    return #TODO later if needed







