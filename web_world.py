from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .options import option_groups

class APTombolaWebWorld(WebWorld):

    game = "AP Tombola"

    theme = "ice"

    option_groups = option_groups
