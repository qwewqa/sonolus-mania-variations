from __future__ import annotations

from sonolus.script.archetype import (
    EntityRef,
    PlayArchetype,
    entity_data,
    entity_memory,
    exported,
    imported,
    shared_memory,
)
from sonolus.script.bucket import Bucket, Judgment, JudgmentWindow
from sonolus.script.interval import Interval, lerp, unlerp
from sonolus.script.particle import Particle
from sonolus.script.runtime import input_offset, time, touches
from sonolus.script.sprite import Sprite
from sonolus.script.timing import beat_to_time

from mania.common.layout import (
    note_y,
)
from mania.common.note import (
    HoldHandle,
    NoteVariant,
    draw_note_body,
    draw_note_connector,
    note_body_sprite,
    note_bucket,
    note_connector_sprite,
    note_head_sprite,
    note_hold_particle,
    note_particle,
    note_window,
    play_hit_effects,
    schedule_auto_hit_sfx,
)
from mania.common.options import Options
from mania.play.input_manager import mark_touch_used, taps_in_hitbox
from mania.play.lane import Lane
from mania.play.timescale import TimescaleGroup


class Note(PlayArchetype):
    is_scored = True

    variant: NoteVariant = imported()
    beat: float = imported()
    lane_ref: EntityRef[Lane] = imported()
    timescale_group_ref: EntityRef[TimescaleGroup] = imported()
    prev_note_ref: EntityRef[Note] = imported()

    touch_id: int = shared_memory()
    y: float = shared_memory()

    target_time: float = entity_data()
    input_target_time: float = entity_data()
    input_time: Interval = entity_data()
    window: JudgmentWindow = entity_data()
    bucket: Bucket = entity_data()
    body_sprite: Sprite = entity_data()
    head_sprite: Sprite = entity_data()
    connector_sprite: Sprite = entity_data()
    particle: Particle = entity_data()
    hold_particle: Particle = entity_data()
    has_prev: bool = entity_data()
    start_time: float = entity_data()
    target_scaled_time: float = entity_data()

    started: bool = entity_memory()
    hold_handle: HoldHandle = entity_memory()

    finish_time: float = exported()

    def preprocess(self):
        self.target_time = beat_to_time(self.beat)
        self.input_target_time = self.target_time + input_offset()
        self.input_time = note_window(self.variant).good + self.input_target_time
        self.window @= note_window(self.variant)
        self.bucket @= note_bucket(self.variant)
        self.body_sprite @= note_body_sprite(self.variant)
        self.head_sprite @= note_head_sprite(self.variant)
        self.connector_sprite @= note_connector_sprite(self.variant)
        self.particle @= note_particle(self.variant)
        self.hold_particle @= note_hold_particle(self.variant)
        self.has_prev = self.prev_note_ref.index > 0

        self.start_time, self.target_scaled_time = self.timescale_group.get_note_times(self.target_time)

        schedule_auto_hit_sfx(Judgment.PERFECT, self.target_time)

    def spawn_time(self) -> float:
        return min(self.start_time, self.prev_start_time)

    def spawn_order(self) -> float:
        return self.spawn_time()

    def should_spawn(self) -> bool:
        return time() >= self.spawn_time()

    def update_sequential(self):
        self.y = note_y(self.timescale_group.scaled_time, self.target_scaled_time)

    def update_parallel(self):
        if self.despawn:
            return
        if self.missed_timing() or self.prev_missed():
            self.despawn = True
            return
        self.draw_body()
        self.draw_connector()

    def missed_timing(self) -> bool:
        return time() > self.input_time.end

    def prev_missed(self) -> bool:
        if not self.has_prev:
            return False
        prev = self.prev
        return prev.is_despawned and prev.touch_id == 0

    def draw_body(self):
        draw_note_body(
            sprite=self.body_sprite,
            pos=self.lane.pos,
            y=self.y,
        )

    def draw_connector(self):
        if not self.has_prev:
            return
        prev = self.prev
        if not prev.is_despawned:
            draw_note_connector(
                sprite=self.connector_sprite,
                pos=self.lane.pos,
                y=self.y,
                prev_pos=prev.lane.pos,
                prev_y=prev.y,
            )
        elif time() < self.target_time:
            prev_target_time = prev.target_time
            target_time = self.target_time
            progress = unlerp(prev_target_time, target_time, time())
            prev_pos = lerp(prev.lane.pos, self.lane.pos, progress)
            draw_note_connector(
                sprite=self.connector_sprite,
                pos=self.lane.pos,
                y=self.y,
                prev_pos=prev_pos,
                prev_y=0,
            )
            draw_note_body(
                sprite=self.head_sprite,
                pos=prev_pos,
                y=0,
            )
            self.hold_handle.update(
                particle=self.hold_particle,
                pos=prev_pos,
            )

    def touch(self):
        if self.has_prev and not self.prev.is_despawned:
            return
        match self.variant:
            case NoteVariant.SINGLE | NoteVariant.HOLD_START:
                self.handle_tap_input()
            case NoteVariant.HOLD_END:
                if Options.auto_release_holds:
                    self.handle_hold_input()
                else:
                    self.handle_release_input()
            case NoteVariant.HOLD_TICK:
                self.handle_hold_input()

    def handle_tap_input(self):
        if time() not in self.input_time:
            return
        for touch in taps_in_hitbox(self.hitbox):
            mark_touch_used(touch)
            self.touch_id = touch.id
            self.complete(touch.start_time)
            return

    def handle_release_input(self):
        touch_id = self.prev.touch_id
        if touch_id == 0:
            return
        for touch in touches():
            if touch.id != touch_id:
                continue
            if not touch.ended:
                return
            if time() >= self.input_time.start and self.hitbox.contains_point(touch.position):
                self.complete(touch.time)
            else:
                self.fail(touch.time)
            return
        if time() >= self.input_time.start:
            self.complete(time() - input_offset())
        else:
            self.fail(time() - input_offset())

    def handle_hold_input(self):
        touch_id = self.prev_note_ref.get().touch_id
        if touch_id == 0:
            return
        self.touch_id = touch_id
        for touch in touches():
            if touch.id != touch_id:
                continue
            if self.hitbox.contains_point(touch.position):
                if touch.ended:
                    # The touch has ended in the hitbox.
                    if time() >= self.input_time.start:
                        self.complete(touch.time)
                    else:
                        self.fail(touch.time)
                elif time() >= self.input_target_time:
                    # The touch is in the hitbox and we've reached the target time.
                    if self.started:
                        # And it's been in the hitbox continuously.
                        self.complete(self.target_time)
                    else:
                        # But it just entered the hitbox.
                        self.complete(time() - input_offset())
                elif time() >= self.input_time.start:
                    # The touch is in the hitbox, but we haven't reached the target time yet.
                    self.started = True
                else:
                    # The touch is ongoing and in the hitbox, but it's not yet in the input time.
                    pass
            elif self.started:
                # The touch was in the hitbox, but moved out, so it counts as a release.
                # self.started will only be true if the input start time has been reached.
                self.complete(time() - input_offset())
            elif touch.ended:
                # The touch ended without ever being in the hitbox within the input time.
                self.fail(touch.time)
            else:
                # The touch is ongoing, but it's never been in the hitbox.
                pass
            return
        if time() >= self.input_time.start:
            self.complete(time() - input_offset())
        else:
            self.fail(time() - input_offset())

    def complete(self, actual_time: float):
        self.result.judgment = self.window.judge(actual=actual_time, target=self.target_time)
        self.result.accuracy = actual_time - self.target_time
        self.result.bucket @= self.bucket
        self.result.bucket_value = self.result.accuracy * 1000
        play_hit_effects(
            note_particle=self.particle,
            pos=self.lane.pos,
            judgment=self.result.judgment,
        )
        self.despawn = True

    def fail(self, actual_time: float):
        self.result.judgment = Judgment.MISS
        self.result.accuracy = actual_time - self.target_time
        self.result.bucket @= self.bucket
        self.result.bucket_value = self.result.accuracy * 1000
        self.despawn = True

    def terminate(self):
        self.hold_handle.destroy()
        self.finish_time = time()

    @property
    def lane(self) -> Lane:
        return self.lane_ref.get()

    @property
    def timescale_group(self) -> TimescaleGroup:
        return self.timescale_group_ref.get()

    @property
    def prev(self) -> Note:
        return self.prev_note_ref.get()

    @property
    def prev_start_time(self) -> float:
        if not self.has_prev:
            return 1e8
        return self.prev_note_ref.get().start_time

    @property
    def hitbox(self):
        return self.lane.hitbox


class UnscoredNote(Note):
    is_scored = False
