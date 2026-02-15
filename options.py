from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle

# Options here
class TombolaVictoryCount(Range):
    """
    Sets the amount of Tombola needed to goal the game.
    """
    display_name = "Tombola Victory Count"

    range_start = 1
    range_end = 6
    default = 3

# Define Dataclass
@dataclass
class APTombolaOptions(PerGameCommonOptions):
    tombola_victory_count: TombolaVictoryCount

