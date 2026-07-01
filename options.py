from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle, StartHints

# Options here
class TombolaVictoryCount(Range):
    """
    Sets the amount of Tombola needed to goal the game.
    (Default is 3)
    """
    display_name = "Tombola Victory Count"
    range_start = 1
    range_end = 6

    default = 3

class MilestoneVictoryCount(Range):
    """
    Sets the amount of Milestones needed to goal the game.
    (Default is 9)
    """
    display_name = "Milestone Victory Count"
    range_start = 1
    range_end = 18

    default = 9

class PreventOtherMetaGameItems(DefaultOnToggle):
    """
    When enabled, prevents locations in the game from having items from other Meta-Games, such as APBingo.

    Note: Progression Items from AP Tombola slots will never be placed in an AP Tombola slot, even if this option is disabled.
    (Default: Enabled)
    """
    display_name = "Prevent Other Meta-Game Items"

class AutomaticNumberHints(DefaultOnToggle):
    """
    When enabled, all Numbers will be automatically hinted. Highly recommended.
    (Default: Enabled)
    """
    display_name = "Automatic Number Hints"

class Cardsanity(Range):
    """
    If Cardsanity is set to a value other than zero, than that many Cards' Unlocks will be sent to the Multiworld,
    instead of being automatically given at the start of the game.
    (Default is 0)
    """
    display_name = "Cardsanity"

    range_start = 0
    range_end = 6

    default = 0

class Rowsanity(Toggle):
    """
    If Rowsanity is enabled, for each row of a Card and for each score type other than Tombola,
    a location will be created that will require that specific row's numbers to be checked.
    In the case of a Decina, each combination of 2 rows will be a location.
    Note: Despite being classified as a Sanity Option, this option enhances the Tombola Experience and is thus recommended.
    (Default: Disabled)
    """
    display_name = "Rowsanity"

class Marksanity(Toggle):
    """
    If Marksanity is enabled a location is created for each number.
    Marking a number will check the corresponding location.
    (Default: Disabled)
    """
    display_name = "Marksanity"

class TombolaStartHints(StartHints):
    """
    Start with these item's locations prefilled into the ``!hint`` command.
    """
    default = []

# Define Dataclass
@dataclass
class APTombolaOptions(PerGameCommonOptions):
    tombola_victory_count: TombolaVictoryCount
    milestone_victory_count: MilestoneVictoryCount
    prevent_other_meta_game_items: PreventOtherMetaGameItems
    automatic_number_hints: AutomaticNumberHints
    cardsanity: Cardsanity
    rowsanity: Rowsanity
    marksanity: Marksanity
    start_hints: TombolaStartHints



option_groups = [
    OptionGroup("Goal Options", [TombolaVictoryCount, MilestoneVictoryCount],),

    OptionGroup("Misc Options", [PreventOtherMetaGameItems, AutomaticNumberHints],),

    OptionGroup("Sanity Options", [Cardsanity, Rowsanity, Marksanity],),

    OptionGroup("Item & Location Options", [TombolaStartHints],)
]

