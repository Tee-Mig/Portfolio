from src.click import click_img, drag_and_drop_with_random_area
from src.packs import DEFAULT_FAST_RECLICK_TIME
from src.screen import find_img
from src.constants import DEFAULT_CONFIDENCE
from src.dungeons import check_stop_after_current_energy, collect_energy_coffre
from src.go_to import go_to_map


def go_to_normal_toa():
    if find_img([("img/normal_toa.png",)]) is False:
        click_img(
            [("img/hard_toa.png",), ("img/hell_toa.png",)],
            [("img/normal_toa_tab.png",)],
        )
        click_img([("img/normal_toa_tab.png",)], [("img/normal_toa.png",)])


def go_to_hard_toa():
    if find_img([("img/hard_toa.png",)]) is False:
        click_img(
            [("img/normal_toa.png",), ("img/hell_toa.png",)],
            [("img/hard_toa_tab.png",)],
        )
        click_img([("img/hard_toa_tab.png",)], [("img/hard_toa.png",)])


def change_team(team_number):
    click_img([("img/shortcut.png",)], [(f"img/toa_shortcut_team{team_number}.png",)])
    click_img(
        [(f"img/toa_shortcut_team{team_number}.png",)],
        [(f"img/toa_team{team_number}.png",)],
    )


def check_toa_team(difficulty):
    if (difficulty == 1 or difficulty == 2) and find_img(
        [("img/toa_team1.png",)]
    ) is False:
        change_team(1)
    elif (difficulty == 3 or difficulty == 4) and find_img(
        [("img/toa_team2.png",)]
    ) is False:
        change_team(2)
    elif (difficulty == 5 or difficulty == 6) and find_img(
        [("img/toa_team3.png",)]
    ) is False:
        change_team(3)
    if difficulty > 6:
        return True
    return False


def do_toa(difficulty, stop_after_current_energy):
    click_img(
        [("img/ready.png",), ("img/ready2.png",), ("img/ready3.png",)],
        [("img/go_fight.png",)],
    )
    while True:
        if check_toa_team(difficulty):
            click_img(
                [("img/croix2.png",)],
                wait_until_images_to_click_gone=True,
            )
            return
        click_img(
            [("img/deroulement_auto.png",), ("img/go_fight.png",)],
            [
                ("img/fight_settings.png",),
                ("img/coffre.png",),
            ],
            click_random=False,
        )
        if find_img([("img/coffre.png",)]):
            if (
                check_stop_after_current_energy(stop_after_current_energy)
                or collect_energy_coffre()
            ):
                click_img(
                    [("img/croix2.png",)],
                    wait_until_images_to_click_gone=True,
                )
                return
            click_img(
                [("img/deroulement_auto.png",), ("img/go_fight.png",)],
                [("img/fight_settings.png",)],
                click_random=False,
            )
        click_img(
            [
                ("img/victory_toa.png", (DEFAULT_CONFIDENCE - 0.1)),
                ("img/defeated_toa.png", (DEFAULT_CONFIDENCE - 0.1)),
                ("img/auto_button.png", DEFAULT_CONFIDENCE - 0.15),
            ],
            [("img/ok.png",), ("img/ok2.png",), ("img/preparation.png",)],
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
        )

        click_img(
            [("img/ok.png",), ("img/ok2.png",)],
            [
                ("img/niveau_suivant.png",),
                ("img/preparation.png",),
                {"path": "img/croix1.png", "region": (0, 0, 1920, 138)},
                ("img/in_toa.png",),
            ],
        )

        if find_img(
            [
                {"path": "img/croix1.png", "region": (0, 0, 1920, 138)},
                ("img/in_toa.png",),
            ]
        ):
            click_img(
                [{"path": "img/croix1.png", "region": (0, 0, 1920, 138)}],
                [("img/in_toa.png",)],
            )
            return
        if find_img([("img/preparation.png",)]):
            difficulty += 1
        click_img(
            [("img/niveau_suivant.png",), ("img/preparation.png",)],
            [("img/deroulement_auto.png",), ("img/go_fight.png",), ("img/coffre.png",)],
        )
        if find_img([("img/coffre.png",)]):
            if (
                check_stop_after_current_energy(stop_after_current_energy)
                or collect_energy_coffre()
            ):
                click_img(
                    [("img/quitter.png",)],
                    wait_until_images_to_click_gone=True,
                )
                return
            click_img(
                [("img/niveau_suivant.png",), ("img/preparation.png",)],
                [("img/deroulement_auto.png",), ("img/go_fight.png",)],
            )


def toa(toa_data):
    go_to_map()

    drag_and_drop_with_random_area(
        start_point=(644, 548),
        start_area_radius=50,
        end_point=(1356, 554),
        end_area_radius=50,
        image_conditions=[("img/toa.png",)],
    )

    click_img([("img/toa.png",)], [("img/toa_window.png",)])
    click_img([("img/toa_window.png",)], [("img/in_toa.png",)])

    go_to_normal_toa()

    # * do normal toa
    if find_img([("img/ready.png",), ("img/ready2.png",), ("img/ready3.png",)]):
        do_toa(toa_data["difficulty_toa_normal"], toa_data["stop_after_current_energy"])

    go_to_hard_toa()

    # * do hard toa
    if find_img([("img/ready.png",), ("img/ready2.png",), ("img/ready3.png",)]):
        do_toa(toa_data["difficulty_toa_hard"], toa_data["stop_after_current_energy"])

    click_img(
        [("img/croix1.png",)],
        [{"path": "img/back_arrow.png", "precise": True}],
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )
