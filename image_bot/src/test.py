from src.click import click_img, drag_and_drop_with_random_area
from src.constants import (
    DEFAULT_FAST_RECLICK_TIME,
    DEFAULT_CONFIDENCE,
)
from src.screen import find_img
from src.packs import remove_packs
from src.enums import Dungeon
from src.dungeons import stop_dj, check_number_of_runs_dj, collect_energy_coffre


def handle_standard_dungeon(dj_tab, dj, dungeon_data):
    click_img([("img/donjon_de_cairos.png",)], [("img/giant_tab.png",)])
    drag_and_drop_with_random_area(
        start_point=(494, 807),
        start_area_radius=50,
        end_point=(498, 455),
        end_area_radius=50,
        image_conditions=dj_tab,
    )
    if find_img(dj_tab):
        run_dungeon_sequence(
            dj_tab,
            dj,
            dungeon_data,
            go_btn={"path": "img/go_launch_dj.png", "region": (0, 800, 1920, 280)},
            combat_buttons=[
                ("img/combats_a_repetition_button.png",),
                ("img/coffre.png",),
            ],
        )
    else:
        click_img([("img/croix_dj.png",)], wait_until_images_to_click_gone=True)


def handle_rift_dungeon(dj_tab, dj, dungeon_data):
    click_img([("img/donjon_du_rift.png",)], [("img/combat.png",)])
    run_dungeon_sequence(
        dj_tab,
        dj,
        dungeon_data,
        go_btn=("img/combat.png",),
        combat_buttons=[("img/combats_a_repetition_button.png",), ("img/coffre.png",)],
    )


def handle_raid_dungeon(dj_tab, dj, dungeon_data):
    click_img([("img/raid_des_mondes.png",)], [("img/combat_raid.png",)])
    click_img(dj_tab, dj)
    click_img(
        [("img/combat_raid.png",)], [("img/combats_a_repetition_button_raid.png",)]
    )
    check_number_of_runs_dj(dungeon_data["30x10_run"])
    click_img(
        [("img/combats_a_repetition_button_raid.png",)],
        [("img/reduce_combat_repet.png",), ("img/coffre.png",)],
    )
    if collect_energy_coffre():
        close_raid_ui()
        dungeon_data["dungeon"] = Dungeon.NONE
    else:
        click_img(
            [("img/reduce_combat_repet.png",)], wait_until_images_to_click_gone=True
        )


def run_dungeon_sequence(dj_tab, dj, dungeon_data, go_btn, combat_buttons):
    click_img(dj_tab, dj)
    click_img([go_btn], combat_buttons)
    if collect_energy_coffre():
        dungeon_data["dungeon"] = Dungeon.NONE
        close_dungeon_ui()
    else:
        check_number_of_runs_dj(dungeon_data["30x10_run"])
        click_img(
            [("img/combats_a_repetition_button.png",)],
            [("img/reduce_combat_repet.png",)],
        )
        click_img(
            [("img/reduce_combat_repet.png",)], wait_until_images_to_click_gone=True
        )


def close_dungeon_ui():
    click_img([("img/croix1.png",)], wait_until_images_to_click_gone=True)
    click_img([("img/croix_dj.png",)], wait_until_images_to_click_gone=True)


def close_raid_ui():
    click_img([("img/croix1.png",)], wait_until_images_to_click_gone=True)
    click_img([("img/croix_interface.png",)], wait_until_images_to_click_gone=True)


def launch_dj(dungeon_data):
    remove_packs([("img/repet_building.png", DEFAULT_CONFIDENCE - 0.3)])
    click_img(
        [("img/repet_building.png", DEFAULT_CONFIDENCE - 0.3)],
        [("img/combats_a_repetition_icon.png",)],
    )
    click_img(
        [("img/combats_a_repetition_icon.png",)],
        [("img/combats_a_repetition.png",)],
    )

    if find_img([("img/vente_selective.png",)]):
        stop_dj()
        click_img(
            [("img/selection_du_donjon.png",)],
            [("img/donjon_de_cairos.png",)],
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
        )

    dungeon = dungeon_data["dungeon"]
    dj_tab = [(f"img/{dungeon.name.lower()}_tab.png",)]
    dj = [(f"img/{dungeon.name.lower()}_dj.png",)]

    if Dungeon.GIANT.value <= dungeon.value <= Dungeon.DARK_ESSENCE.value:
        handle_standard_dungeon(dj_tab, dj, dungeon_data)
    elif Dungeon.FIRE_RIFT.value <= dungeon.value <= Dungeon.DARK_RIFT.value:
        handle_rift_dungeon(dj_tab, dj, dungeon_data)
    elif Dungeon.RAID.value <= dungeon.value <= Dungeon.WIND_RAID.value:
        handle_raid_dungeon(dj_tab, dj, dungeon_data)
