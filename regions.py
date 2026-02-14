from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region

if TYPE_CHECKING:
    from .world import APTombolaWorld

def create_and_connect_regions(world: APTombolaWorld) -> None:
    create_all_regions(world)
    connect_regions(world)

def create_all_regions(world: APTombolaWorld) -> None:
    regions = []

    start_region = Region("The Table", world.player, world.multiworld)
    regions.append(start_region)

    for i in range (6):
        reg = Region(f"Card {i+1}", world.player, world.multiworld)
        regions.append(reg)

    world.multiworld.regions += regions


def connect_regions(world: APTombolaWorld) -> None:
    start_region = world.get_region("The Table")

    for i in range (6):
        card = world.get_region(f"Card {i+1}")
        start_region.connect(card, f"Look at Card {i+1}")
