# TODO TEST WHEN RULES.PY IS DONE REMOVE THE COMMENTS IN WORLD.PY

from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

if TYPE_CHECKING:
    from .world import APTombolaWorld

def set_all_rules(world: APTombolaWorld) -> None:

    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: APTombolaWorld) -> None:
    # Currently all regions are just accessible, this may be used later for "cardsanity" aka locked cards
    return








