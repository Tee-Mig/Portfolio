from src.click import click_img, drag_and_drop_with_random_area
from src.screen import find_img
from src.constants import DEFAULT_CONFIDENCE
from src.packs import DEFAULT_FAST_RECLICK_TIME
from src.go_to import go_to_map
from src.dungeons import check_stop_after_current_energy, collect_energy_coffre


# todo a mettre recuperer l'energie en cas de defaite(apres click preparation) ou victoire(apres click sur go) + rejouer 2 fois max si defaite + verifier globalement + si 3 defaites quitte hoh
def hoh(hoh_data):
    if hoh_data["hoh"] is False:
        return

    go_to_map()
    drag_and_drop_with_random_area(
        start_point=(644, 548),
        start_area_radius=50,
        end_point=(1356, 554),
        end_area_radius=50,
        image_conditions=[("img/arena_island.png",)],
    )

    if find_img([("img/hoh_icon.png",)]):
        click_img(
            [("img/hoh_icon.png",)],
            [("img/demarrer_le_combat.png",), ("img/hoh_cleared.png",)],
        )
        if find_img([("img/demarrer_le_combat.png",)]):
            click_img(
                [("img/demarrer_le_combat.png",)],
                [("img/deroulement_auto.png",), ("img/go_fight.png",)],
            )
            lost_count = 0
            while True:
                click_img(
                    [("img/deroulement_auto.png",), ("img/go_fight.png",)],
                    [("img/fight_settings.png",), ("img/coffre.png",)],
                )
                if find_img([("img/coffre.png",)]):
                    if (
                        check_stop_after_current_energy(
                            hoh_data["stop_after_current_energy"]
                        )
                        or collect_energy_coffre()
                    ):
                        click_img([("img/croix2.png",)], [("img/croix1.png",)])
                        click_img(
                            [("img/croix1.png",)], wait_until_images_to_click_gone=True
                        )
                        return True
                    click_img(
                        [("img/deroulement_auto.png",)],
                        [("img/fight_settings.png",)],
                    )
                click_img(
                    [
                        ("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2),
                        ("img/victory_toa.png",),
                        ("img/defeated_toa.png",),
                    ],
                    [("img/ok.png",), ("img/ok2.png",), ("img/preparation.png",)],
                    reclick_time=DEFAULT_FAST_RECLICK_TIME,
                )

                click_img(
                    [("img/ok.png",), ("img/ok2.png",)],
                    [
                        ("img/niveau_suivant.png",),
                        ("img/preparation.png",),
                    ],
                )
                if find_img(
                    [
                        {
                            "path": "img/niveau_suivant_grey.png",
                            "precise": True,
                            "confidence": DEFAULT_CONFIDENCE + 0.05,
                        }
                    ]
                ):
                    click_img(
                        [("img/quitter.png",)], wait_until_images_to_click_gone=True
                    )
                    break
                if find_img([("img/preparation.png",)]):
                    lost_count += 1
                if lost_count >= 3:
                    click_img([("img/carte_du_monde2.png",)], [("img/croix1.png",)])
                    break
                click_img(
                    [
                        ("img/niveau_suivant.png",),
                        ("img/preparation.png",),
                    ],
                    [
                        ("img/deroulement_auto.png",),
                        ("img/go_fight.png",),
                        ("img/coffre.png",),
                    ],
                )
                if find_img([("img/coffre.png",)]):
                    if (
                        check_stop_after_current_energy(
                            hoh_data["stop_after_current_energy"]
                        )
                        or collect_energy_coffre()
                    ):
                        click_img([("img/carte_du_monde2.png",)], [("img/croix1.png",)])
                        click_img(
                            [("img/croix1.png",)], wait_until_images_to_click_gone=True
                        )
                        return True
                    click_img(
                        [
                            ("img/niveau_suivant.png",),
                            ("img/preparation.png",),
                        ],
                        [("img/deroulement_auto.png",), ("img/go_fight.png",)],
                    )
        click_img([("img/croix1.png",)], wait_until_images_to_click_gone=True)
