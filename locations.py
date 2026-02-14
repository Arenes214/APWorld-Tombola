from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items

if TYPE_CHECKING:
    from .world import APTombolaWorld

from collections import defaultdict



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







