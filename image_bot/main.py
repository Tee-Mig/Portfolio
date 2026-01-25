from src.click import click_img, drag_and_drop_with_random_area, click_until_red_pixel
from src.arena import go_to_arena
from src.screen import (
    find_img,
    find_img_with_red_top_right,
    find_image_position,
    count_image_on_screen,
)
from time import sleep
from src.dungeons import launch_dj, farm_dj
from src.arena import arena, interserver, buy_items_in_arena_shop
from src.enums import Dungeon, DailyDungeon, Rta
from src.constants import DEFAULT_FAST_RECLICK_TIME, DEFAULT_CONFIDENCE
from src.collect_rewards import (
    collect_all_rewards,
    collect_energy_and_crystals_buildings,
    collect_rewards_on_event_page,
)
from src.rta import rta
from src.packs import CROIX_PACKS, NOT_SHOW_TODAY_PACKS, NOT_SHOW_TODAY_DUNGEON
from src.dungeons import sell_bad_runes
import pyautogui
from src.packs import remove_packs
from time import time
from src.store import store_all
from src.shop import reset_view_and_buy_shops
from random import random
from src.runes import apply_runes_from_optimizer
from src.daily_missions import daily_missions
from src.toa import toa
from src.hoh import hoh
from src.guild import do_guild_contents, check_teams


def display_ldplayer_full_window():
    click_img(
        [("img/ldplayer_icon.png", DEFAULT_CONFIDENCE - 0.1)],
        [("img/maximise_ldplayer.png",), ("img/minimise_ldplayer.png",)],
    )
    click_img([("img/maximise_ldplayer.png",)], [("img/minimise_ldplayer.png",)])


def update_info_on_screen():
    click_img(
        [
            ("img/croix_pub_ldplayer.png",),
            {"path": "img/accueil.png", "y_offset": 45},
        ],
        [
            ("img/sw_task.png",),
            ("img/sw_task2.png",),
            ("img/aucun_element_recent.png",),
        ],
        click_random=False,
    )

    if find_img([("img/aucun_element_recent.png",)]):
        click_img([("img/aucun_element_recent.png",)], [("img/sw_icon.png",)])
        click_img([("img/sw_icon.png",)], wait_until_images_to_click_gone=True)
    else:
        click_img(
            [
                ("img/sw_task.png",),
                ("img/sw_task2.png",),
            ],
            wait_until_images_to_click_gone=True,
        )


def update_game():
    click_img([("img/ok.png",)], [("img/maj.png",)])
    click_img(
        [("img/maj.png",), ("img/non_merci.png",), ("img/pas_maintenant.png",)],
        [{"path": "img/jouer.png", "precise": True}],
    )
    click_img([{"path": "img/close_tab.png", "index": -1}], [("img/sw_icon.png",)])
    click_img([("img/sw_icon.png",)], wait_until_images_to_click_gone=True)


def update_screen_and_launch_sw():
    update_info_on_screen()

    while True:
        click_img(
            [
                ("img/oui.png",),
                ("img/ne_plus_montrer_ajd.png",),
                {
                    "path": "img/touch_to_start.png",
                    "y_offset": 90,
                    "confidence": DEFAULT_CONFIDENCE - 0.1,
                },
            ],
            CROIX_PACKS
            + [
                ("img/magic_shop_building.png", (DEFAULT_CONFIDENCE - 0.35)),
                ("img/back_arrow.png",),
                ("img/retour.png",),
                ("img/ok.png",),
            ],
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
        )

        if find_img([("img/ok.png",)]) and find_img([("img/need_update.png",)]):
            update_game()
        else:
            break


# todo code later
# * launch dimension dj + collect dimension rewards
# * do guild content(rivals and guild world)
# * do raid des mondes


# todo ONGOING priorities:
# * apply ffr from rune optimizer
# * do filter runes and upgrade them


# todo sleep at the end + verify farm_dj
# todo put the volume down regularely or put never sleep

# todo if max xp regular or dimension launch regular dungeon -> need testing
# todo add continue dj if both are NONE + check again when launching daily dj if it appears after stopping dj
# todo lancer meme si runes manquantes pour arene et toa ?
# todo update launch hoh


def sw_routine(data):
    display_ldplayer_full_window()  # * perfect

    update_screen_and_launch_sw()  # * perfect

    # * perfect -> take more picture of monster pieces if needed
    reset_view_and_buy_shops(data["items_to_buy_in_shops"])

    store_all(data["store_units"])  # * perfect

    if data["collect_rewards"]["collect_energy_and_crystals_buildings"]:
        collect_energy_and_crystals_buildings()  # * perfect

    # * perfect -> upgrade collected rune after
    daily_missions(data["daily"])

    if (
        data["daily"]["dungeon"] is DailyDungeon.NONE
        and data["dungeon"]["dungeon"] is not Dungeon.NONE
    ):
        # * perfect -> upgrade runes after
        launch_dj(data["dungeon"])

    print(f"daily = {data['daily']['dungeon']}")
    print(f"dungeon run = {data['dungeon']['dungeon']}")

    # * perfect -> upgrade rune after
    collect_all_rewards(data["collect_rewards"])

    # * perfect -> verify collect reward interserver
    arena(data["arena"])

    # todo put world boss here

    # todo fix collect reward "recompenses de combat" dans gvg world(first part)
    do_guild_contents(data["guild"])

    if data["rta"] is not Rta.NONE:
        # * perfect bonus: relaunch dungeon ?
        rta(data["rta"])

    # todo always detect end hoh if fight interupt -> img/niveau_suivant_grey.png is always detected and should be only after beating last stage
    hoh(data["hoh"])

    # * perfect -> verify victory or defeated not seen on final bosses
    if data["toa"]["toa"]:
        toa(data["toa"])

    # * perfect -> put upgrade runes + add picture max xp and max xp dimension
    farm_dj(
        data["dungeon"],
        data["daily"],
    )


def test(data):
    display_ldplayer_full_window()

    do_guild_contents(data["guild"])

    # hoh(data["hoh"])

    # data["daily_summon"] = True
    # data["daily"]["dungeon"] = DailyDungeon.RIFT

    # # todo ongoin fix here
    # if (
    #     data["daily_summon"] is True
    #     or data["daily"]["dungeon"] is not DailyDungeon.NONE
    # ):
    #     # * perfect -> put upgrade runes
    #     daily_missions(
    #         data["dungeon"]["daily"],
    #         data["daily_summon"],
    #         data["dungeon"]["stop_after_current_energy"],
    #     )

    # farm_dj(
    #     data["dungeon"]["regular"],
    #     data["dungeon"]["daily"],
    #     data["dungeon"]["stop_after_current_energy"],
    # )

    # apply_runes_from_optimizer()
    # sell_bad_runes()


def test_collect_rewards_event():
    display_ldplayer_full_window()

    recevoir_buttons = [
        {"path": "img/recevoir_vm.png", "precise": True},
        {"path": "img/recevoir_event1.png", "precise": True},
        {"path": "img/recevoir_event2.png", "precise": True},
        {"path": "img/recevoir_event3.png", "precise": True},
        {"path": "img/recevoir_event4.png", "precise": True},
        {"path": "img/recevoir_event5.png", "precise": True},
        {"path": "img/recevoir_event6.png", "precise": True},
        {"path": "img/recevoir_event7.png", "precise": True},
        {"path": "img/recevoir_event8.png", "precise": True},
        {"path": "img/recevoir_event9.png", "precise": True},
        {"path": "img/recevoir_event10.png", "precise": True},
        {"path": "img/recevoir_event11.png", "precise": True},
        {"path": "img/recevoir_event12.png", "precise": True},
        {"path": "img/recevoir_event13.png", "precise": True},
        {"path": "img/recevoir_event14.png", "precise": True},
        {"path": "img/recevoir_event15.png", "precise": True},
    ]

    termine_buttons = [
        {"path": "img/recevoir_vm_grey.png", "precise": True},
        {"path": "img/recevoir_event_grey1.png", "precise": True},
        {"path": "img/recevoir_event_grey2.png", "precise": True},
        {"path": "img/recevoir_event_grey3.png", "precise": True},
        {"path": "img/recevoir_event_grey4.png", "precise": True},
        {"path": "img/recevoir_event_grey5.png", "precise": True},
        {"path": "img/termine_event1.png", "precise": True},
        {"path": "img/termine_event2.png", "precise": True},
        {"path": "img/termine_event3.png", "precise": True},
        {"path": "img/termine_event4.png", "precise": True},
        {"path": "img/termine_event5.png", "precise": True},
        {"path": "img/termine_event6.png", "precise": True},
        {"path": "img/termine_event7.png", "precise": True},
        {"path": "img/termine_event8.png", "precise": True},
        {"path": "img/termine_event9.png", "precise": True},
        {"path": "img/termine_event10.png", "precise": True},
        {"path": "img/termine_event11.png", "precise": True},
        {"path": "img/termine_event12.png", "precise": True},
        {"path": "img/termine_event13.png", "precise": True},
        {"path": "img/termine_event14.png", "precise": True},
        {"path": "img/termine_event15.png", "precise": True},
        {
            "path": "img/termine_event13.png",
            "precise": True,
            "confidence": DEFAULT_CONFIDENCE + 0.05,
        },
    ]

    confirmation_button = [("img/oui_event.png",)]

    errors = [("img/veuillez_verifier.png",), ("img/selectionnez.png",)]

    click_img([("img/reward_on_event.png",)], [("img/back_event.png",)])
    while True:
        click_counter = 0
        stop = False
        while find_img(recevoir_buttons) and click_counter < 8 and stop is False:
            click_img(recevoir_buttons)
            stop = False
            while find_img(termine_buttons) is False:
                if find_img(confirmation_button):
                    click_img(confirmation_button, termine_buttons)
                if find_img(errors):
                    stop = True
                    while find_img(recevoir_buttons) is False:
                        pass
                    break
            click_counter += 1
        if drag_and_drop_with_random_area((977, 943), 50, (973, 112), 50) is False:
            break
    click_img([("img/back_event.png",)], [("img/nouvelles.png",)])


def set_all_daily_task_value(data, value_to_set):
    data["store_units"]["monsters"] = value_to_set
    data["store_units"]["arcemons"] = value_to_set

    data["daily"]["summon"] = value_to_set

    data["collect_rewards"]["collect_shop_reward"] = value_to_set
    data["collect_rewards"]["collect_social_points_and_guild_energy"] = value_to_set
    data["collect_rewards"]["collect_energy_and_crystals_dimension"] = value_to_set
    data["collect_rewards"]["make_wish"] = value_to_set
    data["collect_rewards"]["collect_events_rewards"] = value_to_set
    data["collect_rewards"]["collect_inbox_rewards"] = value_to_set
    data["collect_rewards"]["get_reap_and_buy_magic_boxes"] = value_to_set

    data["arena"]["interserver"]["interserver"] = value_to_set
    data["arena"]["interserver"]["collect_rewards"] = value_to_set
    data["arena"]["buy_arena_shop"]["transmog_pieces"] = value_to_set
    data["arena"]["buy_arena_shop"]["arcemon"] = value_to_set

    # todo data["world_boss"]["world_boss"] = value_to_set -> a mettre apres

    data["guild"]["subju"]["subju"] = value_to_set
    data["guild"]["subju"]["collect_rewards"] = value_to_set
    data["guild"]["rivals"]["rivals"] = value_to_set
    data["guild"]["world"]["world"] = value_to_set
    data["guild"]["world"]["collect_rewards"] = value_to_set

    data["hoh"]["hoh"] = value_to_set

    data["toa"]["toa"] = value_to_set


# * mig 2
def main():
    data = {
        # * items to buy in magic and guild shop
        "items_to_buy_in_shops": {
            # * guild shop
            "guild": {
                "ld_pieces": True,  # * light and dark pieces
                "ms": True,  # * mystical scroll
                "leg_scroll_pieces": True,  # * legendary scroll pieces
                "grave_scroll_pieces": True,  # * grave scroll pieces
                "unknown_scrolls": True,  # * unknown scrolls
                "monster_pieces": True,  # * monster pieces
            },
            # * magic shop
            "magic": {
                "ld_pieces": True,  # * light and dark pieces
                "ms": True,  # * mystical scroll
                "leg_scroll_pieces": True,  # * legendary scroll pieces
                "grave_scroll_pieces": True,  # * grave scroll pieces
                "unknown_scrolls": True,  # * unknown scrolls
            },
        },
        "store_units": {
            "monsters": True,
            "arcemons": True,
        },
        "daily": {
            "dungeon": DailyDungeon.ESSENCE,
            "stop_after_current_energy": False,
            "30x10_run": False,
            "continue_dungeon": False,
            "essence_dungeon_to_run": {
                "fire": True,
                "water": True,
                "wind": True,
                "light": False,
                "dark": False,
            },
            "summon": True,
        },
        "dungeon": {
            "dungeon": Dungeon.RAID,
            "30x10_run": True,
            "stop_after_current_energy": False,
        },
        "collect_rewards": {
            "collect_energy_and_crystals_buildings": True,
            "collect_shop_reward": True,
            "collect_social_points_and_guild_energy": True,
            "collect_missions_rewards": True,
            "collect_energy_and_crystals_dimension": True,
            "make_wish": True,
            "collect_events_rewards": True,
            "collect_inbox_rewards": True,
            "get_reap_and_buy_magic_boxes": True,
        },
        "arena": {
            "arena": True,
            "interserver": {
                "interserver": True,
                "collect_rewards": True,
            },
            "buy_arena_shop": {
                "diablemon": True,  # * diablemon
                "ld_pieces": True,  # * ld pieces
                "ms": True,  # * mystical scroll
                "transmog_pieces": True,  # * transmog pieces in rta shop
                "arcemon": True,  # * arcemon in guilde shop
            },
        },
        "world_boss": True,
        "guild": {
            "subju": {
                "subju": False,
                "collect_rewards": False,
                "stop_after_current_energy": False,
            },
            "rivals": {
                "rivals": False,
                "stop_after_current_energy": False,
            },
            "world": {
                "world": False,
                "collect_rewards": False,
                "stop_after_current_energy": False,
            },
        },
        "rta": Rta.REGULAR,
        "hoh": {
            "hoh": True,
            "stop_after_current_energy": True,
        },
        "toa": {
            "toa": False,
            "difficulty_toa_normal": 1,  # * from 1 to 6
            "difficulty_toa_hard": 3,  # * from 1 to 6
            "stop_after_current_energy": False,
        },
    }

    data["rta"] = Rta.REGULAR
    data["dungeon"]["stop_after_current_energy"] = False
    data["dungeon"]["dungeon"] = Dungeon.RAID  # * dungeon to run
    data["daily"]["dungeon"] = DailyDungeon.NONE
    set_all_daily_task_value(data, True)

    data["guild"]["world"]["collect_rewards"] = False  # todo need fixing
    data["guild"]["subju"]["collect_rewards"] = False  # todo need fixing
    # todo bug collect rewards subju + gvg world
    # todo regler afficher score arene apres
    # todo pour subju -> si fini et plus d'energy -> probleme pour revenir sur map principale
    # todo augmenter confidence pour trouver ile de guilde
    # todo appuyer sur oui si un allie est deja en train d'attaquer en gvg et gvg world + integrer img/guild_sword2.png

    sw_routine(data)
    # display_ldplayer_full_window()
    # farm_dj(
    #     data["dungeon"],
    #     data["daily"],
    # )

    # test(data)
    # test_collect_rewards_event()

    return 0


if __name__ == "__main__":
    main()
