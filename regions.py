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

    for i in range (6):
        reg = Region(f"Card {i}", world.player, world.multiworld)
        regions.append(reg)

    world.multiworld.regions += regions
