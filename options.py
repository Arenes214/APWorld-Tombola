from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle

# Options here
class TombolaVictoryCount(Range):
    """
    Sets the amount of Tombola needed to goal the game. (Default is 3)
    """
    display_name = "Tombola Victory Count"
    range_start = 1
    range_end = 6

    default = 3

class PreventOtherMetaGameItems(DefaultOnToggle):
    """
    When enabled, prevents locations in the game from having items from other Meta-Games, such as APBingo.
    Note: items from AP Tombola games will never be placed in an AP Tombola slot, even if this option is disabled.
    (Default: Enabled)
    """
    display_name = "Prevent Other Meta-Game Items"

class Cardsanity(Range):
    """
    If Cardsanity is set to a value other than zero, than that many Cards will be locked.
    A locked Card may be unlocked by receiving its corresponding "Card Unlock" item.
    Unlocking a Card sends an item to the multiworld.
    (Default is 0)
    """
    display_name = "Cardsanity"

    range_start = 0
    range_end = 6

    default = 0

# TODO STARTING HINTS

# Define Dataclass
@dataclass
class APTombolaOptions(PerGameCommonOptions):
    tombola_victory_count: TombolaVictoryCount
    prevent_other_meta_game_items: PreventOtherMetaGameItems
    cardsanity: Cardsanity


option_groups = [
    OptionGroup("Goal Options", [TombolaVictoryCount]),

    OptionGroup("Sanity Options", [Cardsanity])


]

