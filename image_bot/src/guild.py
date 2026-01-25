from src.go_to import go_to_map
from src.click import drag_and_drop_with_random_area, click_img
from src.screen import find_img, find_img_with_red_top_right, count_image_on_screen
from src.dungeons import collect_energy_coffre, check_stop_after_current_energy
from src.constants import (
    DEFAULT_CONFIDENCE,
    DEFAULT_FAST_RECLICK_TIME,
    DEFAULT_REGION,
    CHECK_BEFORE_AUTO_GVG_WORLD,
)
from src.packs import NOT_SHOW_TODAY_DUNGEON
from typing import Tuple
from src.rta import click_on_target


def go_to_guild_content(img):
    go_to_map()

    drag_and_drop_with_random_area(
        start_point=(1356, 554),
        start_area_radius=50,
        end_point=(644, 548),
        end_area_radius=50,
        image_conditions=img,
    )


def subju_fight(fight_img: str, stop_after_current_energy) -> bool:
    click_img([(fight_img,)], [("img/combat.png",)])
    click_img([("img/combat.png",)], [("img/go.png",)])
    click_img(
        [("img/oui.png",), {"path": "img/go.png", "precise": True}],
        [
            ("img/coffre.png",),
            ("img/skip.png",),
            ("img/fight_settings.png", DEFAULT_CONFIDENCE - 0.1),
        ],
        click_random=False,
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )
    if find_img([("img/coffre.png",)]):
        if (
            check_stop_after_current_energy(stop_after_current_energy)
            or collect_energy_coffre()
        ):
            click_img([("img/croix2.png",)], [("img/croix1.png",)])
            click_img(
                [("img/croix1.png",)],
                [{"path": "img/retour.png", "precise": True}],
            )
            return True
        click_img(
            [("img/oui.png",), {"path": "img/go.png", "precise": True}],
            [("img/skip.png",), ("img/fight_settings.png", DEFAULT_CONFIDENCE - 0.1)],
            click_random=False,
            reclick_time=DEFAULT_FAST_RECLICK_TIME,
        )
    click_img(
        [("img/skip.png",)], [("img/fight_settings.png", DEFAULT_CONFIDENCE - 0.1)]
    )
    click_img(
        [
            ("img/result.png", (DEFAULT_CONFIDENCE - 0.1)),
            ("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2),
        ],
        [("img/preparation_icon.png",)],
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )
    click_img(
        [("img/preparation_icon.png",)], [("img/croix2.png",), ("img/coffre.png",)]
    )
    if find_img([("img/coffre.png",)]):
        if (
            check_stop_after_current_energy(stop_after_current_energy)
            or collect_energy_coffre()
        ):
            click_img(
                [("img/carte_du_monde2.png",)], wait_until_images_to_click_gone=True
            )
            return True
        click_img([("img/preparation_icon.png",)], [("img/croix2.png",)])
    click_img([("img/croix2.png",)], [("img/croix1.png",)])
    click_img(
        [("img/croix1.png",)],
        [{"path": "img/retour.png", "precise": True}],
    )
    return False


def subju(subju_data):
    go_to_guild_content(
        [
            ("img/subju_on.png", (DEFAULT_CONFIDENCE + 0.03)),
            ("img/subju_off.png", (DEFAULT_CONFIDENCE + 0.03)),
        ]
    )
    if find_img(
        [
            ("img/subju_on.png", (DEFAULT_CONFIDENCE + 0.03)),
            ("img/subju_off.png", (DEFAULT_CONFIDENCE + 0.03)),
        ]
    ):
        click_img(
            [
                ("img/subju_on.png", (DEFAULT_CONFIDENCE + 0.03)),
                ("img/subju_off.png", (DEFAULT_CONFIDENCE + 0.03)),
            ],
            [("img/oui.png",)],
        )
        if find_img([("img/no_guild.png",)]) is False:
            click_img([("img/oui.png",)], [("img/coffre_a_trophees.png",)])
            if subju_data["subju"] and find_img([("img/boss_subju.png",)]):
                subju_fight(
                    "img/boss_subju.png", subju_data["stop_after_current_energy"]
                )
            elif (
                subju_data["subju"]
                and find_img([("img/fire_subju.png",)])
                and find_img([("img/boss_subju.png",)]) is False
            ):
                for i in range(3):
                    if i == 0:
                        subju_dj = "img/fire_subju.png"
                    elif i == 1:
                        subju_dj = "img/wind_subju.png"
                    else:
                        subju_dj = "img/water_subju.png"

                    if subju_fight(subju_dj, subju_data["stop_after_current_energy"]):
                        break

            if subju_data["collect_rewards"] and find_img_with_red_top_right(
                ("img/coffre_a_trophees.png",), number_of_red_pixel=3300
            ):
                click_img(
                    [("img/coffre_a_trophees.png",)], [("img/subju_rewards.png",)]
                )
                click_img([("img/subju_rewards.png",)], [("img/oui.png",)])
                click_img([("img/oui.png",)], [("img/vente_selective4.png",)])
                click_img(
                    [("img/vente_selective4.png",)],
                    [("img/vente_selective3.png",)],
                )
                click_img(
                    [("img/vente_selective3.png",)],
                    NOT_SHOW_TODAY_DUNGEON + [("img/ok.png",)],
                )
                click_img(
                    NOT_SHOW_TODAY_DUNGEON + [("img/ok.png",)],
                    [{"path": "img/croix1.png", "precise": True}],
                    click_random=False,
                    reclick_time=DEFAULT_FAST_RECLICK_TIME,
                )
                click_img(
                    [("img/croix1.png",)],
                    [{"path": "img/retour.png", "precise": True}],
                )
            click_img([("img/retour.png",)], wait_until_images_to_click_gone=True)
        else:
            click_img([("img/non.png",)], wait_until_images_to_click_gone=True)


def do_attack_guild_rivals(tower_color: str, stop_after_current_energy):
    click_img([(tower_color,)], [("img/attaque.png",)])
    click_img([("img/attaque.png",)], [("img/go.png",)])
    click_img(
        [("img/go.png",)],
        [("img/fight_settings.png", DEFAULT_CONFIDENCE - 0.1), ("img/coffre.png",)],
    )
    if find_img([("img/coffre.png",)]):
        if (
            check_stop_after_current_energy(stop_after_current_energy)
            or collect_energy_coffre()
        ):
            click_img([("img/croix2.png",)], [("img/retour.png",)])
            click_img([("img/retour.png",)], wait_until_images_to_click_gone=True)
            return True
        click_img(
            [("img/go.png",)], [("img/fight_settings.png", DEFAULT_CONFIDENCE - 0.1)]
        )
    click_img(
        [
            ("img/victory.png", (DEFAULT_CONFIDENCE - 0.1)),
            ("img/defeated.png", (DEFAULT_CONFIDENCE - 0.1)),
            ("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2),
        ],
        [("img/retour.png",)],
        reclick_time=DEFAULT_FAST_RECLICK_TIME,
    )
    return False


def guild_rivals(guild_rivals_data):
    go_to_guild_content([("img/ile_de_combat.png", DEFAULT_CONFIDENCE + 0.03)])
    click_img(
        [("img/ile_de_combat.png", DEFAULT_CONFIDENCE + 0.03)],
        [("img/non.png",), ("img/rivaux_de_guilde.png",)],
    )
    if find_img([("img/rivaux_de_guilde.png",)]):
        if find_img_with_red_top_right(("img/rivaux_de_guilde.png",)):
            click_img([("img/rivaux_de_guilde.png",)], [("img/retour.png",)])

            fight = count_image_on_screen("img/guild_sword.png")
            while fight > 0:
                while fight > 0:
                    drag_and_drop_with_random_area(
                        start_point=(1356, 554),
                        start_area_radius=50,
                        end_point=(644, 548),
                        end_area_radius=50,
                        image_conditions=[("img/green_tower_guild.png",)],
                    )
                    if find_img([("img/green_tower_guild.png",)]) is False:
                        break
                    if do_attack_guild_rivals(
                        "img/green_tower_guild.png",
                        guild_rivals_data["stop_after_current_energy"],
                    ):
                        return
                    else:
                        fight -= 1

                if fight <= 0:
                    break

                while fight > 0:
                    drag_and_drop_with_random_area(
                        start_point=(644, 548),
                        start_area_radius=50,
                        end_point=(1356, 554),
                        end_area_radius=50,
                        image_conditions=[("img/yellow_tower_guild.png",)],
                    )
                    if find_img([("img/yellow_tower_guild.png",)]) is False:
                        break
                    if do_attack_guild_rivals(
                        "img/yellow_tower_guild.png",
                        guild_rivals_data["stop_after_current_energy"],
                    ):
                        return
                    else:
                        fight -= 1

                if fight <= 0:
                    break
                # todo need screenshot of red tower
                # while fight > 0:
                #     drag_and_drop_with_random_area(
                #         start_point=(1356, 554),
                #         start_area_radius=50,
                #         end_point=(644, 548),
                #         end_area_radius=50,
                #         image_conditions=[("img/red_tower_guild.png",)],
                #     )
                #     if find_img([("img/red_tower_guild.png",)]) is False:
                #         break
                #     if do_attack_guild_rivals("img/red_tower_guild.png", guild_rivals_data["stop_after_current_energy"]):
                #         return
                #     else:
                #         fight -= 1

            click_img([("img/retour.png",)], wait_until_images_to_click_gone=True)
        else:
            click_img(
                [{"path": "img/back_arrow_grey.png", "precise": True}],
                wait_until_images_to_click_gone=True,
            )

    else:
        click_img([("img/non.png",)], wait_until_images_to_click_gone=True)


def check_gvgw_team(
    team: str,
    team_shortcut: str,
    team_region: Tuple[int, int, int, int],
    shortcut_region: Tuple[int, int, int, int] = DEFAULT_REGION,
):
    if not find_img([{"path": team, "region": team_region}]):
        click_img(
            [
                {"path": "img/shortcut.png", "region": team_region},
                {"path": "img/shortcut2.png", "region": team_region},
            ],
            [{"path": team_shortcut, "region": shortcut_region}],
        )
        click_img(
            [{"path": team_shortcut, "region": shortcut_region}],
            [
                {
                    "path": team,
                    "region": team_region,
                }
            ],
        )


def check_teams():
    check_gvgw_team("img/gvgw_team1.png", "img/gvgw_shortcut1.png", (0, 0, 1920, 350))
    check_gvgw_team("img/gvgw_team2.png", "img/gvgw_shortcut2.png", (0, 350, 1920, 730))

    while drag_and_drop_with_random_area(
        start_point=(941, 499),
        start_area_radius=50,
        end_point=(940, 239),
        end_area_radius=50,
    ):
        pass

    check_gvgw_team("img/gvgw_team3.png", "img/gvgw_shortcut3.png", (0, 0, 1920, 210))
    check_gvgw_team("img/gvgw_team4.png", "img/gvgw_shortcut4.png", (0, 210, 1920, 220))
    check_gvgw_team(
        "img/gvgw_team5.png",
        "img/gvgw_shortcut5.png",
        (0, 430, 1920, 650),
        (0, 855, 1920, 230),
    )


def gvg_world_fight():
    auto_cmp = 0
    while (find_img([("img/gvgw_round_2.png", (DEFAULT_CONFIDENCE + 0.07))])) is False:
        print("fight 1")
        # * fight 1
        if find_img([("img/lionel_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/lionel_s3.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/CP_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/CP_s3.png",), ("img/CP_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/maxi_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/maxi_s3.png",), ("img/maxi_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if auto_cmp >= CHECK_BEFORE_AUTO_GVG_WORLD:
            click_img([("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2)])

    auto_cmp = 0
    while (find_img([("img/gvgw_round_3.png", (DEFAULT_CONFIDENCE + 0.07))])) is False:
        print("fight 2")
        # * fight 2
        if find_img([("img/tiana_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/tiana_s3.png",), ("img/tiana_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/galion_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/galion_s3.png",), ("img/galion_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/zaiross_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/zaiross_s3.png",), ("img/zaiross_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if auto_cmp >= CHECK_BEFORE_AUTO_GVG_WORLD:
            click_img([("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2)])

    auto_cmp = 0
    while (find_img([("img/gvgw_round_4.png", (DEFAULT_CONFIDENCE + 0.07))])) is False:
        print("fight 3")
        # * fight 3
        if find_img([("img/light_robo_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/light_robo_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/lamiella_s1.png",)]):
            auto_cmp += 1
            click_img(
                [
                    ("img/lamiella_s2.png", (DEFAULT_CONFIDENCE - 0.2)),
                    ("img/lamiella_s3.png",),
                ],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/dorothy_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/dorothy_s3.png",), ("img/dorothy_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if auto_cmp >= CHECK_BEFORE_AUTO_GVG_WORLD:
            click_img([("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2)])

    auto_cmp = 0
    while (find_img([("img/gvgw_round_5.png", (DEFAULT_CONFIDENCE + 0.07))])) is False:
        print("fight 4")
        # * fight 4
        if find_img([("img/bastet_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/bastet_s3.png",), ("img/bastet_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/gemini_s1.png",)]):
            auto_cmp += 1
            click_img(
                [
                    ("img/gemini_s2.png",),
                ],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/alicia_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/alicia_s3.png",), ("img/alicia_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if auto_cmp >= CHECK_BEFORE_AUTO_GVG_WORLD:
            click_img([("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2)])

    auto_cmp = 0
    while (find_img([("img/result.png", (DEFAULT_CONFIDENCE - 0.1))])) is False:
        print("fight 5")
        # * fight 5
        if find_img([("img/jeogun_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/jeogun_s3.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/bellenus_form1_s1.png",), ("img/bellenus_form2_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/bellenus_form1_s3.png",), ("img/bellenus_form2_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if find_img([("img/akha_s1.png",)]):
            auto_cmp += 1
            click_img(
                [("img/akha_s3.png",), ("img/akha_s2.png",)],
                click_random=False,
            )
            click_on_target()

        if auto_cmp >= CHECK_BEFORE_AUTO_GVG_WORLD:
            click_img([("img/auto_button.png", DEFAULT_CONFIDENCE - 0.2)])


def do_attack_guild_world(tower_color: str, stop_after_current_energy):
    click_img([(tower_color,)], [("img/attaque2.png",)])
    click_img([("img/attaque2.png",)], [("img/go.png",)])
    check_teams()
    click_img([("img/go.png",)], [("img/depart.png",), ("img/coffre.png",)])
    if find_img([("img/coffre.png",)]):
        if (
            check_stop_after_current_energy(stop_after_current_energy)
            or collect_energy_coffre()
        ):
            click_img([("img/croix2.png",)], [("img/croix1.png",)])
            click_img(
                [("img/croix1.png",)], [{"path": "img/retour.png", "precise": True}]
            )
            click_img([("img/retour.png",)], wait_until_images_to_click_gone=True)
            return True
        click_img([("img/go.png",)], [("img/depart.png",)])
    click_img(
        [("img/depart.png",)], [("img/gvgw_round_1.png", (DEFAULT_CONFIDENCE + 0.03))]
    )
    gvg_world_fight()
    click_img(
        [("img/result.png", (DEFAULT_CONFIDENCE - 0.1))],
        [("img/recompenses_gvg_world.png",)],
    )
    return False


def guild_world(gvg_world_data):
    go_to_guild_content([("img/ile_de_combat.png", DEFAULT_CONFIDENCE + 0.03)])
    click_img(
        [("img/ile_de_combat.png", DEFAULT_CONFIDENCE + 0.03)],
        [("img/non.png",), ("img/combat_de_guilde_world.png",)],
    )
    if find_img([("img/combat_de_guilde_world.png",)]):
        click_img(
            [("img/combat_de_guilde_world.png",)], [("img/recompenses_gvg_world.png",)]
        )
        if gvg_world_data["world"]:
            fight = count_image_on_screen("img/guild_sword.png")
            while fight > 0:
                while fight > 0:
                    drag_and_drop_with_random_area(
                        start_point=(1356, 554),
                        start_area_radius=50,
                        end_point=(644, 548),
                        end_area_radius=50,
                        image_conditions=[("img/green_tower_guild.png",)],
                    )
                    if find_img([("img/green_tower_guild.png",)]) is False:
                        break
                    if do_attack_guild_world(
                        "img/green_tower_guild.png",
                        gvg_world_data["stop_after_current_energy"],
                    ):
                        return
                    else:
                        fight -= 1

                if fight <= 0:
                    break

                while fight > 0:
                    drag_and_drop_with_random_area(
                        start_point=(644, 548),
                        start_area_radius=50,
                        end_point=(1356, 554),
                        end_area_radius=50,
                        image_conditions=[("img/yellow_tower_guild.png",)],
                    )
                    if find_img([("img/yellow_tower_guild.png",)]) is False:
                        break
                    if do_attack_guild_world(
                        "img/yellow_tower_guild.png",
                        gvg_world_data["stop_after_current_energy"],
                    ):
                        return
                    else:
                        fight -= 1

                if fight <= 0:
                    break
                # todo need screenshot of red tower
                # while fight > 0:
                #     drag_and_drop_with_random_area(
                #         start_point=(1356, 554),
                #         start_area_radius=50,
                #         end_point=(644, 548),
                #         end_area_radius=50,
                #         image_conditions=[("img/red_tower_guild.png",)],
                #     )
                #     if find_img([("img/red_tower_guild.png",)]) is False:
                #         break
                #     if do_attack_guild_world("img/red_tower_guild.png", gvg_world_data["stop_after_current_energy"]):
                #         return
                #     else:
                #         fight -= 1
        if gvg_world_data["collect_rewards"] and find_img_with_red_top_right(
            ("img/recompenses_gvg_world.png",), number_of_red_pixel=3000
        ):
            click_img([("img/recompenses_gvg_world.png",)], [("img/vs.png",)])
            while find_img_with_red_top_right(
                ("img/recompenses_de_combat.png",), number_of_red_pixel=900
            ):
                print("test 1")
                while find_img([("img/recolter.png",)]):
                    print("test 2.01")
                    click_img([("img/recolter.png",)], [("img/obtenus.png",)])
                    click_img(
                        [("img/obtenus.png",)],
                        [
                            {
                                "path": "img/croix1.png",
                                "precise": True,
                                "region": (1500, 0, 420, 1080),
                            }
                        ],
                    )
                    print("test 2")  # todo block here
                print("test 3")
                if find_img_with_red_top_right(
                    ("img/recompenses_de_combat.png",), number_of_red_pixel=900
                ):
                    print("test 4")
                    drag_and_drop_with_random_area(
                        start_point=(933, 713),
                        start_area_radius=50,
                        end_point=(901, 420),
                        end_area_radius=50,
                    )
                else:
                    print("test 5")
                print("test 6")

            if find_img_with_red_top_right(
                ("img/recompenses_de_xp.png",), number_of_red_pixel=600
            ):
                click_img([("img/recompenses_de_xp.png",)], [("img/guild_point.png",)])
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
            click_img(
                [("img/croix1.png",)], [{"path": "img/retour.png", "precise": True}]
            )

        click_img([("img/retour.png",)], wait_until_images_to_click_gone=True)

    else:
        click_img([("img/non.png",)], wait_until_images_to_click_gone=True)


def go_most_left_map():
    go_to_map()
    drag_and_drop_with_random_area(
        start_point=(644, 548),
        start_area_radius=50,
        end_point=(1356, 554),
        end_area_radius=50,
        image_conditions=[("img/arena_island.png",)],
    )


def check_do_guild_content(guild_data):
    for _, sub_data in guild_data.items():
        for sub_key, value in sub_data.items():
            if sub_key != "stop_after_current_energy" and value:
                return True
    return False


def do_guild_contents(guild_data):
    if check_do_guild_content(guild_data):
        go_most_left_map()
    else:
        return

    if guild_data["subju"]["subju"] or guild_data["subju"]["collect_rewards"]:
        subju(guild_data["subju"])

    if guild_data["rivals"]["rivals"]:
        guild_rivals(guild_data["rivals"])

    if guild_data["world"]["world"] or guild_data["world"]["collect_rewards"]:
        guild_world(guild_data["world"])
