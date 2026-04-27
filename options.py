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

    Note: progression items from AP Tombola games will never be placed in an AP Tombola slot, even if this option is disabled.
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
    If Cardsanity is set to a value other than zero, than that many Cards will be locked.
    A locked Card may be unlocked by receiving its corresponding "Card Unlock" item.
    Unlocking a Card sends an item to the multiworld.
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
    In the case of a Decina, each combination of 2 rows will have its check
    (Default: Disabled)
    """
    display_name = "Rowsanity"

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
    start_hints: TombolaStartHints



option_groups = [
    OptionGroup("Goal Options", [TombolaVictoryCount, MilestoneVictoryCount],),

    OptionGroup("Misc Options", [PreventOtherMetaGameItems, AutomaticNumberHints],),

    OptionGroup("Sanity Options", [Cardsanity, Rowsanity],),

    OptionGroup("Item & Location Options", [TombolaStartHints],)
]

