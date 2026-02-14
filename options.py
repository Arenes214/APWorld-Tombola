from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle

# Options here
class Quick(Toggle):
    """
    This only exists so that AP does not complain
    """
    display_name = "Quick"

@dataclass
class APTombolaOptions(PerGameCommonOptions):
    quick: Quick

