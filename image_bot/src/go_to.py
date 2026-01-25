from src.click import click_img, drag_and_drop_with_random_area
from src.packs import CROIX_PACKS, NOT_SHOW_TODAY_PACKS, GRASS
from src.constants import DEFAULT_CONFIDENCE, DEFAULT_FAST_RECLICK_TIME
from src.screen import find_img
from src.enums import Rta


def go_to_homescreen():
    click_img(
        [{"path": "img/retour.png", "precise": True}]
        + NOT_SHOW_TODAY_PACKS
        + CROIX_PACKS,
        [
            {
                "path": "img/magic_shop_building.png",
                "confidence": (DEFAULT_CONFIDENCE - 0.35),
                "precise": True,
            },
            {"path": "img/back_arrow.png", "precise": True},
        ],
        click_random=False,
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )
    click_img(
        [{"path": "img/back_arrow.png", "precise": True}]
        + NOT_SHOW_TODAY_PACKS
        + CROIX_PACKS,
        [
            {
                "path": "img/magic_shop_building.png",
                "confidence": (DEFAULT_CONFIDENCE - 0.35),
                "precise": True,
            }
        ],
        click_random=False,
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )


def go_to_arena(regular_arena=True):
    click_img(
        [{"path": "img/bataille_button.png", "precise": True}]
        + NOT_SHOW_TODAY_PACKS
        + CROIX_PACKS
        + GRASS,
        [
            {"path": "img/retour.png", "precise": True},
            {"path": "img/combat_de_classement.png", "precise": True},
            {"path": "img/back_arrow.png", "precise": True},
        ],
        click_random=False,
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )

    if find_img([("img/back_arrow.png",)]):
        drag_and_drop_with_random_area(
            start_point=(644, 548),
            start_area_radius=50,
            end_point=(1356, 554),
            end_area_radius=50,
            image_conditions=[("img/arena_island.png",)],
        )
        click_img(
            [("img/arena_island.png",)],
            [("img/arene.png",)],
            click_random=False,
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
        )
        click_img(
            [("img/arene.png",)],
            [("img/rival.png",), ("img/remove_arena_ranking.png",)],
        )
        click_img([("img/remove_arena_ranking.png",)], [("img/rival.png",)])

    if regular_arena and find_img([("img/combat_de_classement.png",)]):
        click_img(
            [("img/arena_tab.png",)],
            [("img/rival.png",), ("img/remove_arena_ranking.png",)],
        )
        click_img([("img/remove_arena_ranking.png",)], [("img/rival.png",)])


def go_to_rta(rta_type):
    if find_img([("img/combat_de_classement.png",)]) is False:
        go_to_arena(False)
        click_img(
            [("img/rta_tab.png",)], [("img/combat_de_classement.png",), ("img/ok.png",)]
        )
        click_img(
            [("img/ok.png",)],
            [
                ("img/combat_de_classement.png",),
                {"path": "img/rival.png", "precise": True},
            ],
        )
        if find_img([("img/rival.png",)]):
            return False

    if rta_type is Rta.REGULAR:
        if (
            find_img([{"path": "img/combat_de_classement.png", "precise": True}])
            is False
        ):
            return False
    else:
        if find_img([("img/special_league.png",), ("img/special_league2.png",)]):
            click_img(
                [("img/special_league.png",), ("img/special_league2.png",)],
                [("img/commencer_SL.png",)],
            )
            if (find_img([{"path": "img/commencer_SL.png", "precise": True}])) is False:
                return False
        else:
            return False

    return True


def go_to_map():
    click_img(
        [
            {"path": "img/retour.png", "precise": True},
            {"path": "img/bataille_button.png", "precise": True},
        ]
        + NOT_SHOW_TODAY_PACKS
        + CROIX_PACKS
        + GRASS,
        [{"path": "img/back_arrow.png", "precise": True}],
        click_random=False,
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )
