from sonolus.script.archetype import PlayArchetype, callback, imported

from mania.common.effect import play_empty_sfx
from mania.common.layout import (
    LanePosition,
    Layer,
    lane_hitbox,
    lane_layout,
    note_layout,
)
from mania.common.particle import Particles
from mania.common.skin import Skin
from mania.play.input_manager import unused_touches


class Lane(PlayArchetype):
    pos: LanePosition = imported()

    def update_parallel(self):
        Skin.lane.draw(self.layout, z=Layer.LANE)
        Skin.slot.draw(self.slot_layout, z=Layer.SLOT)

    @callback(order=1)
    def touch(self):
        for touch in unused_touches():
            if not touch.started:
                continue
            if self.hitbox.contains_point(touch.position):
                play_empty_sfx()
                Particles.lane.spawn(self.layout, duration=0.2)

    @property
    def hitbox(self):
        return lane_hitbox(self.pos)

    @property
    def layout(self):
        return lane_layout(self.pos)

    @property
    def slot_layout(self):
        return note_layout(self.pos, 0)
