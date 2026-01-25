from src.click import click_img, drag_and_drop_with_random_area, click_until_red_pixel
from src.screen import find_img, find_img_with_red_top_right
from src.constants import DEFAULT_FAST_RECLICK_TIME
from src.constants import (
    DEFAULT_REGION,
    DEFAULT_CONFIDENCE,
    CHECK_BEFORE_AUTO_INTERSERVER,
)
from src.go_to import go_to_arena
from src.rta import click_on_target


def check_arena_team(team: str, team_shortcut: str):
    if not find_img([(team,)]):
        click_img([("img/shortcut.png",)], [(team_shortcut,)])
        click_img([(team_shortcut,)], [(team,)])


def fight_rival():
    while (find_img([("img/victory.png",), ("img/defeated.png",)])) is False:
        click_img([("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2)])


def fight_arena():
    cmp_auto = 0
    while (find_img([("img/victory.png",), ("img/defeated.png",)])) is False:
        if find_img([("img/woonsa_s1.png",)]):
            cmp_auto += 1
            click_img(
                [("img/woonsa_s3.png",), ("img/woonsa_s2.png",)],
                click_random=False,
            )
            click_on_target()
        if find_img([("img/jeogun_s1.png",)]):
            cmp_auto += 1
            click_img(
                [("img/jeogun_s3.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/maxi_s1.png",)]):
            cmp_auto += 1
            click_img(
                [("img/maxi_s3.png",), ("img/maxi_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/psama_s1.png",)]):
            cmp_auto += 1
            click_img(
                [("img/psama_s2.png",)],
                click_random=False,
            )
            click_on_target()
        if cmp_auto >= CHECK_BEFORE_AUTO_INTERSERVER:
            click_img([("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2)])


def arena_fight_cycle(
    region: tuple[int, int, int, int] = DEFAULT_REGION,
):
    while find_img([{"path": "img/arena_wing.png", "region": region}]):
        click_img(
            [{"path": "img/arena_wing.png", "region": region}],
            [
                ("img/go.png",),
                {"path": "img/croix1.png", "region": (0, 0, 1500, 1080)},
            ],
        )
        if find_img([{"path": "img/croix1.png", "region": (0, 0, 1500, 1080)}]):
            return
        check_arena_team("img/rival_team.png", "img/rival_shortcut.png")
        click_img(
            [("img/oui.png",), ("img/go.png",)],
            wait_until_images_to_click_gone=True,
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
            click_random=False,
        )
        fight_rival()
        click_img(
            [("img/victory.png",), ("img/defeated.png",)],
            [("img/arene_list.png",), ("img/ok2.png",)],
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
        )
        click_img([("img/ok2.png",)], [("img/arene_list.png",)])  # * for collab


def buy_item():
    click_img([("img/acheter_shop.png",)], [("img/oui3.png",)])
    click_img([("img/oui3.png",)], [("img/ok3.png",)])
    click_img([("img/ok3.png",)], wait_until_images_to_click_gone=True)


def buy_max_item():
    is_red_pixel = click_until_red_pixel(
        images_to_click=[("img/plus3.png",)],
        red_pixel_region=(1026, 609, 88, 59),
        waiting_images=[
            ("img/end_cursor_shop.png",),
            ("img/full_item_to_buy.png", DEFAULT_CONFIDENCE + 0.05),
        ],
    )
    if is_red_pixel:
        click_img([("img/moins.png",)])
    if is_red_pixel is None:
        click_img([("img/croix_fenetre.png",)], wait_until_images_to_click_gone=True)
    else:
        buy_item()


def buy_items_in_arena_shop(buy_arena_shop):
    click_img([("img/shop_arena_button.png",)], [("img/rta_shop_tab.png",)])

    if find_img([("img/devilmon.png",)]) and buy_arena_shop["diablemon"]:
        click_img([("img/devilmon.png",)], [("img/acheter_shop.png",)])
        buy_item()

    if (
        find_img([("img/devilmon.png",)]) is False
        or buy_arena_shop["diablemon"] is False
    ):
        if (
            find_img([("img/ld_pieces_arena_shop.png",)])
            and (buy_arena_shop["ld_pieces"])
        ):
            click_img([("img/ld_pieces_arena_shop.png",)], [("img/acheter_shop.png",)])
            buy_max_item()

        if (
            find_img([("img/ld_pieces_arena_shop.png",)]) is False
            or buy_arena_shop["ld_pieces"] is False
        ) and (find_img([("img/ms_arena_shop.png",)]) and buy_arena_shop["ms"]):
            click_img([("img/ms_arena_shop.png",)], [("img/acheter_shop.png",)])
            buy_max_item()

    if buy_arena_shop["transmog_pieces"]:
        click_img([("img/rta_shop_tab.png",)], [("img/rta_shop_tab_selected.png",)])
        drag_and_drop_with_random_area(
            start_point=(1233, 569),
            start_area_radius=50,
            end_point=(416, 556),
            end_area_radius=50,
            image_conditions=[
                ("img/shift_stones.png",),
                ("img/no_shift_stones.png",),
            ],
        )
        if find_img([("img/shift_stones.png",)]):
            click_img([("img/shift_stones.png",)], [("img/acheter_shop.png",)])
            buy_item()

    if buy_arena_shop["arcemon"]:
        click_img(
            [("img/guild_arena_tab.png",)], [("img/guild_arena_tab_selected.png",)]
        )
        if find_img([("img/arcemon_shop.png",)]):
            click_img([("img/arcemon_shop.png",)], [("img/acheter_shop.png",)])
            buy_item()

    click_img([("img/croix1.png",)], [{"path": "img/retour.png", "precise": True}])


def do_arena():
    click_img([("img/rival.png",)], [("img/arena_wing.png",)])

    if find_img([("img/maitre_x.png",)]):
        arena_fight_cycle((0, 0, 1920, 380))

    while True:
        region = DEFAULT_REGION
        if find_img_with_red_top_right(("img/rival_tab.png",)):
            if find_img([("img/top_rivals.png",)]) and find_img(
                [("img/maitre_x.png",)]
            ):
                region = (0, 500, 1920, 580)
            elif find_img([("img/top_rivals.png",)]):
                region = (0, 380, 1920, 700)

        arena_fight_cycle(region)
        if find_img([{"path": "img/croix1.png", "region": (0, 0, 1500, 1080)}]):
            break

        if find_img_with_red_top_right(("img/rival_tab.png",)):
            if find_img_with_red_top_right(("img/rival_tab.png",)):
                drag_and_drop_with_random_area(
                    start_point=(933, 813),
                    start_area_radius=50,
                    end_point=(901, 320),
                    end_area_radius=50,
                )
        else:
            drag_and_drop_with_random_area(
                start_point=(901, 320),
                start_area_radius=50,
                end_point=(933, 813),
                end_area_radius=50,
            )
    click_img(
        [{"path": "img/croix1.png", "region": (0, 0, 1500, 1080)}],
        [{"path": "img/croix1.png", "region": (1500, 0, 420, 1080)}],
    )
    click_img(
        [{"path": "img/croix1.png", "index": -1}],
        [{"path": "img/retour.png", "precise": True}],
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )


def interserver(interserver_data):
    if find_img([("img/server_battle.png",)]):
        click_img([("img/server_battle.png",)], [("img/combat_interserver.png",)])
        if interserver_data["interserver"] and find_img(
            [{"path": "img/combat_interserver.png", "precise": True}]
        ):
            click_img(
                [("img/combat_interserver.png",)],
                [("img/in_interserver_list.png",)],
            )
            while True:
                while find_img([("img/interserver_wing.png",)]):
                    click_img(
                        [("img/interserver_wing.png",)],
                        [("img/go.png",)],
                    )
                    check_arena_team("img/arena_team.png", "img/arena_shortcut.png")
                    click_img([("img/go.png",)], wait_until_images_to_click_gone=True)
                    fight_arena()
                    click_img(
                        [("img/victory.png",), ("img/defeated.png",)],
                        [("img/in_interserver_list.png",)],
                        reclick_time=DEFAULT_FAST_RECLICK_TIME,
                    )
                if (
                    drag_and_drop_with_random_area(
                        start_point=(933, 813),
                        start_area_radius=50,
                        end_point=(901, 320),
                        end_area_radius=50,
                    )
                    is False
                ):
                    break
            click_img(
                [{"path": "img/croix1.png", "region": (0, 0, 1565, 1080)}],
                [("img/recompense_interserver.png",)],
            )

        if interserver_data["collect_rewards"] and find_img_with_red_top_right(
            ("img/recompense_interserver.png",), number_of_red_pixel=900
        ):
            click_img(
                [("img/recompense_interserver.png",)],
                [("img/recompenses_de_gloire.png",)],
            )
            click_img(
                [("img/recompenses_de_gloire.png",)], [("img/interserver_point.png",)]
            )
            click_img(
                [
                    ("img/ne_plus_montrer_ajd2.png",),
                    ("img/ok.png",),
                    {"path": "img/recuperer2.png", "index": 0},
                ],
                [{"path": "img/next_reward.png", "region": (0, 0, 670, 1080)}],
                reclick_time=DEFAULT_FAST_RECLICK_TIME,
                click_random=False,
            )
            click_img([("img/croix1.png",)], [("img/recompense_interserver.png",)])

        click_img([("img/croix1.png",)], [{"path": "img/retour.png", "precise": True}])


def arena(arena_data):
    interserver_status = any(arena_data["interserver"].values())
    buy_arena_shop_status = any(arena_data["buy_arena_shop"].values())

    if arena_data["arena"] or interserver_status or buy_arena_shop_status:
        go_to_arena()
    else:
        return

    if arena_data["arena"]:
        do_arena()

    if interserver_status:
        interserver(arena_data["interserver"])

    if buy_arena_shop_status:
        buy_items_in_arena_shop(arena_data["buy_arena_shop"])
