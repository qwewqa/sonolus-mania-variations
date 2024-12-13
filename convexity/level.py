from pathlib import Path

from sonolus.script.level import BpmChange, Level, LevelData

from convexity.convert.osu import convert_osz
from convexity.play.init import Init
from convexity.play.lane import Lane
from convexity.play.note import Note, NoteVariant
from convexity.play.timescale import TimescaleChange, TimescaleGroup

level = Level(
    name="convexity-level",
    title="Convexity Level",
    bgm=None,
    data=LevelData(
        bgm_offset=0,
        entities=[
            BpmChange(beat=0, bpm=60),
            Init(),
            Lane(lane=-1.5),
            Lane(lane=-0.5),
            Lane(lane=0.5),
            Lane(lane=1.5),
            ts1 := TimescaleGroup(),
            TimescaleChange(beat=0, scale=1),
            TimescaleChange(beat=0.001, scale=1),
            TimescaleChange(beat=0.002, scale=1),
            # *[
            #     [
            #         head := Note(
            #             variant=NoteVariant.HOLD_START,
            #             beat=i,
            #             lane=-1.5,
            #             leniency=2,
            #             timescale_group_ref=ts1.ref(),
            #         ),
            #         seg := Note(
            #             variant=NoteVariant.HOLD_TICK,
            #             beat=i + (1 - 1 / 2) * 0.25,
            #             lane=0.5,
            #             leniency=2,
            #             timescale_group_ref=ts1.ref(),
            #             prev_note_ref=head.ref(),
            #         ),
            #         seg := UnscoredNote(
            #             variant=NoteVariant.HOLD_ANCHOR,
            #             beat=i + (1 - 1 / 2) * 0.5,
            #             lane=2.5,
            #             leniency=0,
            #             timescale_group_ref=ts1.ref(),
            #             prev_note_ref=seg.ref(),
            #         ),
            #         seg := Note(
            #             variant=NoteVariant.HOLD_TICK,
            #             beat=i + (1 - 1 / 2) * 0.75,
            #             lane=0.5,
            #             leniency=2,
            #             timescale_group_ref=ts1.ref(),
            #             prev_note_ref=seg.ref(),
            #         ),
            #         seg := Note(
            #             variant=NoteVariant.HOLD_END,
            #             beat=i + 1 - 1 / 2,
            #             lane=0.5,
            #             leniency=2,
            #             timescale_group_ref=ts1.ref(),
            #             prev_note_ref=seg.ref(),
            #         ),
            #     ]
            #     for i in range(2, 30)
            # ],
            # # ts2 := TimescaleGroup(),
            # # TimescaleChange(beat=0, scale=1),
            # # TimescaleChange(beat=2, scale=1.5),
            # # *[
            # #     [
            # #         head := Note(
            # #             variant=NoteVariant.HOLD_START,
            # #             beat=i,
            # #             lane=-0.5,
            # #             leniency=2,
            # #             timescale_group_ref=ts2.ref(),
            # #         ),
            # #         Note(
            # #             variant=NoteVariant.HOLD_END,
            # #             beat=i + 1 - 1 / 2,
            # #             lane=-0.5,
            # #             leniency=2,
            # #             timescale_group_ref=ts2.ref(),
            # #             prev_note_ref=head.ref(),
            # #         ),
            # #     ]
            # #     for i in range(2, 30)
            # # ],
            # ts4 := TimescaleGroup(),
            # TimescaleChange(beat=0, scale=1),
            # *[
            #     tsc
            #     for i in range(1, 100)
            #     for tsc in [
            #         TimescaleChange(beat=i / 4, scale=1),
            #         TimescaleChange(beat=i / 4 + 1 / 8, scale=1),
            #     ]
            # ],
            # TimescaleChange(beat=100 / 4, scale=1),
            # *[
            #     Note(
            #         variant=NoteVariant.FLICK,
            #         beat=i / 4,
            #         lane=1.5,
            #         leniency=1,
            #         timescale_group_ref=ts4.ref(),
            #     )
            #     for i in range(8, 100)
            # ],
            # *[
            #     Note(
            #         variant=NoteVariant.DIRECTIONAL_FLICK,
            #         beat=i / 4,
            #         lane=-2.5,
            #         leniency=1,
            #         direction=-1,
            #         timescale_group_ref=ts4.ref(),
            #     )
            #     for i in range(8, 100)
            # ],
            *[
                Note(
                    variant=NoteVariant.DIRECTIONAL_FLICK,
                    beat=i / 4,
                    lane=-2.5,
                    leniency=3,
                    direction=3,
                    timescale_group_ref=ts1.ref(),
                )
                for i in range(8, 100)
            ],
            *[
                Note(
                    variant=NoteVariant.DIRECTIONAL_FLICK,
                    beat=i / 4,
                    lane=1.5,
                    leniency=3,
                    direction=3,
                    timescale_group_ref=ts1.ref(),
                )
                for i in range(8, 100)
            ],
        ],
    ),
)

levels = [level]

for osz_file in Path("resources").glob("*.osz"):
    levels.extend(convert_osz(osz_file.read_bytes()))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-1557"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-738"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-700"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-20008"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-20004"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-1482"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-20007"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-2001"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-1187"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-2028"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-2030"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-719"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-1095"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-1018"))
# levels.append(convert_sonolus_llsif_level("milkbun-llsif-1345"))
# levels.extend(get_bestdori_official(307))
# levels.extend(get_bestdori_official(306))
# levels.extend(get_bestdori_official(292))
# levels.extend(get_bestdori_official(247))
# levels.extend(get_bestdori_official(187))
# levels.extend(get_bestdori_official(185))
# levels.extend(get_bestdori_official(484))
# levels.extend(get_bestdori_official(253))
# levels.extend(get_bestdori_official(598))
# levels.extend(get_bestdori_official(597))
# levels.extend(get_bestdori_official(596))
# levels.extend(get_bestdori_official(470))
# levels.extend(get_bestdori_official(406))
# levels.extend(get_bestdori_official(4))