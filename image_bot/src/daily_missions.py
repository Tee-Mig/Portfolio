from src.click import click_img, drag_and_drop_with_random_area
from src.packs import remove_packs
from src.screen import find_img
from src.enums import DailyDungeon
from src.dungeons import (
    stop_dj,
    check_number_of_runs_dj,
    collect_energy_coffre,
    check_stop_after_current_energy,
)
from src.packs import CROIX_PACKS, GRASS
from src.constants import DEFAULT_CONFIDENCE
from src.store import store_monster


def reset_view():
    remove_packs(
        [
            {
                "path": "img/magic_shop_building.png",
                "confidence": (DEFAULT_CONFIDENCE - 0.35),
                "precise": True,
            }
        ]
    )

    click_img(
        [("img/magic_shop_building.png", DEFAULT_CONFIDENCE - 0.35)],
        [("img/acheter.png", DEFAULT_CONFIDENCE - 0.1)],
    )
    click_img(
        [("img/acheter.png", DEFAULT_CONFIDENCE - 0.1)],
        [{"path": "img/echoppe_de_magie.png", "precise": True}],
    )


def do_daily_summon():
    remove_packs(
        [{"path": "img/missions.png", "precise": True}],
        close_packs=(CROIX_PACKS + GRASS),
    )

    click_img([("img/missions.png",)], [("img/croix2.png",)])

    drag_and_drop_with_random_area(
        start_point=(920, 881),
        start_area_radius=50,
        end_point=(917, 601),
        end_area_radius=50,
        image_conditions=[
            {"path": "img/missions_summon.png", "precise": True},
            {"path": "img/missions_summon_done.png", "precise": True},
        ],
    )

    if find_img(
        [
            {
                "path": "img/missions_summon.png",
                "precise": True,
                "confidence": DEFAULT_CONFIDENCE + 0.05,
            }
        ]
    ):
        click_img(
            [{"path": "img/missions_summon.png", "x_offset": 700}],
            [("img/go_missions.png",)],
        )
        click_img(
            [("img/go_missions.png",)],
            [{"path": "img/croix1.png", "region": (1700, 0, 220, 1080)}],
        )

        while True:
            drag_and_drop_with_random_area(
                start_point=(1435, 743),
                start_area_radius=50,
                end_point=(1434, 326),
                end_area_radius=50,
                image_conditions=[("img/velin_inconnu.png",)],
            )
            if find_img([("img/trans_scroll.png",)]) is False:
                break

        if find_img([("img/velin_inconnu.png",)]):
            click_img([("img/velin_inconnu.png",)], [("img/invoquer.png",)])
            for _ in range(3):
                click_img([("img/invoquer.png",)], [("img/skip.png",), ("img/ok.png",)])
                click_img([("img/skip.png",)], [("img/ok.png",)])
                click_img([("img/ok.png",)], [("img/invoquer.png",)])

        reset_view()

        store_monster()
        return True
    return False


def exit_dungeon():
    click_img(
        [("img/croix1.png",)],
        [{"path": "img/croix_dj.png", "precise": True}],
    )
    click_img([("img/croix_dj.png",)], wait_until_images_to_click_gone=True)


def launch_daily_dungeon(daily_data):
    remove_packs(
        [{"path": "img/missions.png", "precise": True}],
        close_packs=(CROIX_PACKS + GRASS),
    )

    click_img([("img/missions.png",)], [("img/croix2.png",)])

    daily_dungeon_to_launch = [
        {
            "path": f"img/{daily_data['dungeon'].name.lower()}_dungeon_missions.png",
            "precise": True,
        }
    ]
    if daily_data["dungeon"] == DailyDungeon.ESSENCE:
        daily_dungeon_to_launch += [
            {
                "path": "img/magic_essence_dungeon_missions.png",
                "precise": True,
            }
        ]
    drag_and_drop_with_random_area(
        start_point=(920, 881),
        start_area_radius=50,
        end_point=(917, 601),
        end_area_radius=50,
        image_conditions=daily_dungeon_to_launch,
    )

    if find_img(
        daily_dungeon_to_launch,
    ):
        click_img(
            [
                {"path": daily_dungeon["path"], "x_offset": 1200}
                for daily_dungeon in daily_dungeon_to_launch
            ],
            [("img/go_missions.png",)],
        )
        click_img(
            [("img/go_missions.png",)],
            [
                {"path": "img/go_launch_dj.png", "region": (0, 800, 1920, 280)},
                ("img/combat.png",),
                ("img/combat_raid.png",),
                ("img/vente_selective.png",),
            ],
        )
        if find_img([("img/vente_selective.png",)]):
            stop_dj()

            remove_packs(
                [{"path": "img/missions.png", "precise": True}],
                close_packs=(CROIX_PACKS + [("img/croix_dj.png",)]),
            )
            click_img([("img/missions.png",)], [("img/croix2.png",)])
            drag_and_drop_with_random_area(
                start_point=(920, 881),
                start_area_radius=50,
                end_point=(917, 601),
                end_area_radius=50,
                image_conditions=daily_dungeon_to_launch,
            )
            click_img(
                [
                    {"path": daily_dungeon["path"], "x_offset": 1100}
                    for daily_dungeon in daily_dungeon_to_launch
                ],
                [("img/go_missions.png",)],
            )
            click_img(
                [("img/go_missions.png",)],
                [
                    {"path": "img/go_launch_dj.png", "region": (0, 800, 1920, 280)},
                    ("img/combat.png",),
                    ("img/combat_raid.png",),
                ],
            )
        if daily_data["dungeon"] == DailyDungeon.ESSENCE:
            for essence_type, value in daily_data["essence_dungeon_to_run"].items():
                if value is False and find_img(
                    [(f"img/{essence_type}_essence_dj.png",)]
                ):
                    daily_data["dungeon"] = DailyDungeon.NONE
                    exit_dungeon()
                    return True

        click_img(
            [
                {"path": "img/go_launch_dj.png", "region": (0, 800, 1920, 280)},
                ("img/combat.png",),
                ("img/combat_raid.png",),
            ],
            [
                ("img/combats_a_repetition_button.png",),
                ("img/combats_a_repetition_button_raid.png",),
                ("img/coffre.png",),
            ],
        )
        if find_img([("img/coffre.png",)]):
            if (
                check_stop_after_current_energy(daily_data["stop_after_current_energy"])
                or collect_energy_coffre()
            ):
                daily_data["dungeon"] = DailyDungeon.NONE
                exit_dungeon()
                return True
            click_img(
                [
                    {"path": "img/go_launch_dj.png", "region": (0, 800, 1920, 280)},
                    ("img/combat.png",),
                    ("img/combat_raid.png",),
                ],
                [
                    ("img/combats_a_repetition_button.png",),
                    ("img/combats_a_repetition_button_raid.png",),
                ],
            )

        check_number_of_runs_dj(daily_data["30x10_run"])
        click_img(
            [
                ("img/combats_a_repetition_button.png",),
                ("img/combats_a_repetition_button_raid.png",),
            ],
            [("img/reduce_combat_repet.png",), ("img/coffre.png",)],
        )
        if find_img([("img/coffre.png",)]):
            if (
                check_stop_after_current_energy(daily_data["stop_after_current_energy"])
                or collect_energy_coffre()
            ):
                daily_data["dungeon"] = DailyDungeon.NONE
                click_img([("img/croix2.png",)], [("img/croix1.png",)])
                exit_dungeon()
                return True
            click_img(
                [
                    ("img/combats_a_repetition_button.png",),
                    ("img/combats_a_repetition_button_raid.png",),
                ],
                [("img/reduce_combat_repet.png",)],
            )
        click_img(
            [("img/reduce_combat_repet.png",)],
            wait_until_images_to_click_gone=True,
        )
        return True
    else:
        daily_data["dungeon"] = DailyDungeon.NONE
        return False


def daily_missions(daily_data):
    daily_summon = daily_data["summon"]
    daily_dungeon_status = None
    daily_summon_status = None

    if daily_data["dungeon"] is not DailyDungeon.NONE:
        daily_dungeon_status = launch_daily_dungeon(daily_data)
        if daily_dungeon_status is False and daily_summon:
            while drag_and_drop_with_random_area(
                start_point=(917, 586),
                start_area_radius=50,
                end_point=(920, 896),
                end_area_radius=50,
            ):
                pass
    if daily_summon:
        daily_summon_status = do_daily_summon()

    if daily_dungeon_status and not daily_summon_status:
        reset_view()
