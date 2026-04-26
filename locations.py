from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items

if TYPE_CHECKING:
    from .world import APTombolaWorld


# Later i'll maybe make the number of rewards changeable, this should save me a bit of time then
AMBO_REWARD_COUNT_MAX = 1
TERNO_REWARD_COUNT_MAX = 2
QUATERNA_REWARD_COUNT_MAX = 2
CINQUINA_REWARD_COUNT_MAX = 3
DECINA_REWARD_COUNT_MAX = 3
TOMBOLA_REWARD_COUNT_MAX = 4

# Location id - Cards will be 5 digit (Format CSYDN)
# C indicates Card (e.g. 3xxxx is card 3) ("Card 7" are milestones)
# S indicates which score it is (2 Ambo, 3 Terno, ..., 6 Decina, 7 Tombola) or special properties:
    # 8 indicates Card Unlock (Cardsanity)
# Y indicates the kinda of Sanity it is (0 No Sanity, 1 Rowsanity)
# D indicates the "discriminator" for sanity options (e.g. for Rowsanity 0 is row 1, 1 is row 2)
# N indicates for multiple score rewards which one it is
# e.g. 24003 indicates Card 2, Score Quaterna, third reward


def all_locations_to_id():
    complete_list = {}

    complete_list.update(create_all_regular_card_score_locations())
    complete_list.update(create_all_cardsanity_unlock_locations())
    complete_list.update(create_all_rowsanity_score_locations())
    complete_list.update(create_all_milestone_score_locations())

    return complete_list

def create_all_regular_card_score_locations():
    the_list = {}

     # Create Card Scoring Locations
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

def create_all_cardsanity_unlock_locations():
    the_list = {}
    # Create Card Unlock Location
    # Reminder that they must exist in location_name_to_id in world.py
    for card in range (6):
        the_list[f"Card {card+1} Unlocked"] = (10000*(card+1))+8000+1

    return the_list


def create_all_rowsanity_score_locations():
    # differentiators:
    # 0 - Row 1
    # 1 - Row 2
    # 2 - Row 3
    # For Decina, the differentiator indicates its row plus the one after (wrapping around for Row 3)

    the_list = {}
    for card in range(6):
        for row in range(3):
            decina_pal = 0
            if row == 2:
                decina_pal = 1
            else:
                decina_pal = row+2
            the_list[f"Card {card+1} Rowsanity - Row {row+1} Ambo Reward"] = (10000*(card+1))+2000+100+(10*(row+1))+1
            the_list[f"Card {card+1} Rowsanity - Row {row+1} Terno Reward"] = (10000*(card+1))+3000+100+(10*(row+1))+1
            the_list[f"Card {card+1} Rowsanity - Row {row+1} Quaterna Reward"] = (10000*(card+1))+4000+100+(10*(row+1))+1
            the_list[f"Card {card+1} Rowsanity - Row {row+1} Cinquina Reward"] = (10000*(card+1))+5000+100+(10*(row+1))+1
            the_list[f"Card {card+1} Rowsanity - Rows {row+1} & {decina_pal} Decina Reward"] = (10000*(card+1))+6000+100+(10*(row+1))+1
    return the_list


# For Milestones, Locations id are as following (Format MTABC)
# M Indicates:
# 7 is Milestones in general
# 8 is Total Count Milestones, since they may need more than 999 index

# T indicates Type: 1 is Score Collect, 2 is Collection of Numbers,, 3 is Even/Odd

# For Score Collect
# A indicates which score it is (2 Ambo, 3 Terno...)
# B indicates the number of them to get
# C is 1

# For Collection of Numbers
# TODO A list will exists that contains all possible Collections
# The format will just be based on the list

# For Total Count, TABC will indicate the count to reach

# For Even/Odd, A indicates Even(2) or Odd(1), BC indicates the count

def create_all_milestone_score_locations():
    the_list = {}
    # Create all Score Collect locations
    for score_id, score in enumerate(["Ambo","Terno","Quaterna","Cinquina","Decina","Tombola"]):
        for count_id, count in enumerate(["Double","Triple","Quadruple","Quintuple","All of the"]):
            the_list[f"Milestone - {count} {score}"] = 70000 + 1000 + (score_id+2)*100 + (count_id+1)*10 + 1

    # Create all Collection of Numbers
    # TODO for now only Developer Permutations exists
    the_list["Milestone - Developer Permutations"] = 70000 + 2000 + 1
    the_list["Milestone - Nice."] = 70000 + 2000 + 2
    the_list["Milestone -  The Meaning of Life"] = 70000 + 2000 + 3

    # Create all Total Count locations
    # TODO for now only a select hardcoded amount of Total Counts exists
    the_list["Milestone - Developer Count"] = 80000 + 214
    the_list["Milestone - Developer Count x10"] = 80000 + 2140
    the_list["Milestone - Erbs told me this number"] = 80000 + 690


    # Create all Even/Odd locations
    for i in range (20): # 20 is arbitrary, may be increased in future
        the_list[f"Milestone - {i} Even Numbers"] = 70000 + 3000 + 200 + i
        the_list[f"Milestone - {i} Odd Numbers"] = 70000 + 3000 + 100 + i


# Create the list with ids to mimic APQuest behaviour
LOCATION_NAME_TO_ID = all_locations_to_id()

class APTombolaLocation(Location):
    game = "AP Tombola"

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}

def create_all_locations(world: APTombolaWorld) -> None:
    create_regular_locations(world)
    create_events(world)

    if world.options.rowsanity:
        create_rowsanity_locations(world)

def create_regular_locations(world: APTombolaWorld) -> None: # ALSO CREATES CARDSANITY LOCKS
    # Get the regions
    # Card 1 is index **1** since index 0 will be the starting regions
    regions = []
    regions.append(world.get_region("The Table"))

    for i in range (1,7):
        regions.append(world.get_region(f"Card {i}"))

    # Create the REGULAR score locations and associate to the region
    score_locations = create_all_regular_card_score_locations()

    for key, value in score_locations.items():
        region_index = value // 10000
        # Probably wacky since i already got the id but might as well just follow APQuest for now
        loc = get_location_names_with_ids([key])
        regions[region_index].add_locations(loc, APTombolaLocation)

    # Create Cardsanity Unlock locations if they need to, in the starting region
    if world.options.cardsanity:
        for card in world.cardsanity_to_lock:
            loc = get_location_names_with_ids([f"Card {card} Unlocked"])
            regions[0].add_locations(loc, APTombolaLocation)

def create_rowsanity_locations(world: APTombolaWorld) -> None:
    # Yes the first part is duplicated code from the regular locations
    # Get the regions
    # Card 1 is index **1** since index 0 will be the starting regions
    regions = []
    regions.append(world.get_region("The Table"))

    for i in range (1,7):
        regions.append(world.get_region(f"Card {i}"))

    score_locations = create_all_rowsanity_score_locations()

    for key, value in score_locations.items():
        region_index = value // 10000
        loc = get_location_names_with_ids([key])
        regions[region_index].add_locations(loc, APTombolaLocation)

def create_milestone_locations(world: APTombolaWorld) -> None:







def create_events(world: APTombolaWorld) -> None:
    # Get Regions
    starting_region = world.get_region("The Table")

    # Create Event Items
    victory_item_tombola = items.APTombolaItem("Tombola Scored", ItemClassification.progression, None, world.player)

    # Create Tombola Events for goal tracking
    for i in range(6):
        # Get the region
        region = world.get_region(f"Card {i+1}")

        # Create Location and set item to it
        event_location = APTombolaLocation(world.player, f"EVENT: Card {i+1} - Tombola Scored", None, region)
        event_location.place_locked_item(victory_item_tombola)
        region.locations.append(event_location)

    # Create "Goal requirement fullfilled" location
    starting_region.add_event("EVENT: Tombola Count Requirement Reached", "Victory Token", location_type=APTombolaLocation, item_type=items.APTombolaItem)









