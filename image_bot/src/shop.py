from src.click import click_img
from src.screen import find_img
from src.packs import remove_packs, NOT_SHOW_TODAY_SHOP, GRASS, CROIX_PACKS
from src.constants import DEFAULT_CONFIDENCE, DEFAULT_FAST_RECLICK_TIME
from src.go_to import go_to_homescreen


def buy_items(items_to_buy):
    while find_img(items_to_buy):
        click_img(items_to_buy, [("img/acheter_shop.png",)])
        click_img(
            [("img/acheter_shop.png",)],
            NOT_SHOW_TODAY_SHOP
            + [("img/magic_shop_building2.png",), ("img/guild_shop_building2.png",)],
        )
        click_img(
            NOT_SHOW_TODAY_SHOP,
            [("img/magic_shop_building2.png",), ("img/guild_shop_building2.png",)],
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
            click_random=False,
        )


def get_all_items_to_buy(buy_items_shop):
    items_to_buy = []

    if buy_items_shop.get("ld_pieces"):
        items_to_buy += [("img/ld_pieces.png",)]

    if buy_items_shop.get("ms"):
        items_to_buy += [("img/ms.png",)]

    if buy_items_shop.get("leg_scroll_pieces"):
        items_to_buy += [("img/leg_scroll_pieces.png",)]

    if buy_items_shop.get("grave_scroll_pieces"):
        items_to_buy += [("img/grave_scroll_pieces.png",)]

    if buy_items_shop.get("unknown_scrolls"):
        items_to_buy += [("img/unknown_scrolls.png",)]

    if buy_items_shop.get("monster_pieces"):
        items_to_buy += [
            {
                "path": "img/monster_pieces.png",
                "confidence": DEFAULT_CONFIDENCE - 0.12,
                "region": (1100, 0, 820, 1080),
            },
            {
                "path": "img/monster_pieces2.png",
                "confidence": DEFAULT_CONFIDENCE - 0.12,
                "region": (1100, 0, 820, 1080),
            },
        ]
    return items_to_buy


def buy_shop(building, items_to_buy):
    remove_packs(
        [{"path": building, "confidence": (DEFAULT_CONFIDENCE - 0.35), "precise": True}]
    )

    click_img(
        CROIX_PACKS + [(building, (DEFAULT_CONFIDENCE - 0.35))],
        [("img/acheter.png", DEFAULT_CONFIDENCE - 0.1)],
        click_random=False,
    )
    if find_img(
        [
            {
                "path": "img/acheter.png",
                "confidence": DEFAULT_CONFIDENCE - 0.1,
                "precise": True,
            }
        ]
    ):
        click_img(
            [("img/acheter.png", DEFAULT_CONFIDENCE - 0.1)],
            NOT_SHOW_TODAY_SHOP + [("img/stars_shop.png",)],
        )
        click_img(
            NOT_SHOW_TODAY_SHOP,
            [("img/stars_shop.png",)],
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
            click_random=False,
        )
        buy_items(items_to_buy)
    else:
        click_img(GRASS, [{"path": "img/bataille_button.png", "precise": True}])


def reset_view_and_buy_shops(items_to_buy_in_shops):
    go_to_homescreen()

    collect_rewards_guild_status = any(items_to_buy_in_shops["guild"].values())
    collect_rewards_magic_status = any(items_to_buy_in_shops["magic"].values())

    if collect_rewards_guild_status:
        # * check guild shop
        items_to_buy_guild = get_all_items_to_buy(items_to_buy_in_shops["guild"])
        buy_shop("img/guild_shop_building.png", items_to_buy_guild)

    if collect_rewards_magic_status:
        # * check magic shop
        items_to_buy_magic = get_all_items_to_buy(items_to_buy_in_shops["magic"])
        buy_shop("img/magic_shop_building.png", items_to_buy_magic)
    else:
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
            CROIX_PACKS
            + [("img/magic_shop_building.png", (DEFAULT_CONFIDENCE - 0.35))],
            [("img/acheter.png", DEFAULT_CONFIDENCE - 0.1)],
            click_random=False,
        )
        click_img(
            [("img/acheter.png", DEFAULT_CONFIDENCE - 0.1)],
            NOT_SHOW_TODAY_SHOP + [("img/echoppe_de_magie.png",)],
        )
