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



# Define Dataclass
@dataclass
class APTombolaOptions(PerGameCommonOptions):
    tombola_victory_count: TombolaVictoryCount
    prevent_other_meta_game_items: PreventOtherMetaGameItems


option_groups = [
    OptionGroup("Goal Options", [TombolaVictoryCount]),

    OptionGroup("Sanity Options", [])


]

