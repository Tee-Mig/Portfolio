from src.enums import Dungeon, Rta, Day
from src.constants import DEFAULT_CONFIDENCE

# (1 + ((21(SPD) / (6 * 5)) + (12(ATK%) / (8 * 5)) + (0(CR%) / (6 * 5)) + (0(CD%) / (7 * 5)))) / 2.8
# (1 + ((21(SPD) / (6 * 5)) + (12(ATK%) / (8 * 5)) + (0(HP%) / (8 * 5)) + (0(DEF%) / (8 * 5)))) / 2.8

# Maxi/Veronica/Woonsa/Giana/Han/Zerath account
data1 = {
    # * upgrade rune settings
"upgrade_rune_settings": {
        # --- Profilage eff (ACC/RES ignorés) ---
        "EFF_GROUP_SUPPORT": {"SPD", "ATK%", "HP%", "DEF%"}, # 6, 8, 8, 8
        "EFF_GROUP_DPS": {"SPD", "ATK%", "CR", "CD"}, # 6, 8, 6, 7
        "IGNORED_SUBS": {
            "ACC",
            "RES",
            "ATK",
            "HP",
            "DEF",
        },  # ignorés dans eff + comptage good
        # --- Set categories ---
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_NEVER_USED": {
            "Amelioration",
            "Determination",
            "Endurance",
            "Focus",
            "Gardien",
            "Precision",
            "Protection",
            "Toleration",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_LITTLE_USED": {
            "Combat",
            "Destruction",
            "Energie",
            "Sceau",
            "Vengeance",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_NEMESIS": {
            "Nemesis",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_OFFENSIVE_LITTLE_USED": {
            "Fatale",
            "Vampire",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_OFFENSIVE_USED": {
            "Lame",
            "Rage",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_FAST": {
            "Rapide",
        },  # swift
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_USED": {
            "Desespoir",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_VERY_USED": {
            "Intangible",
            "Violent",
            "Volonte",
        },
        # --- Conditions par catégorie (eff + big_proc) ---
        # eff_support / eff_dps : {bucket: seuil} où bucket = nb de good subs (2/3/4)
        #   → valeur au niveau catégorie = défaut pour tous les types de rune de cette catégorie
        #   → entrée par type ("ATK%", "slot_135", …) écrase le défaut pour ce type uniquement
        # big_proc : {stat: seuil} seuil absolu d'un seul sub pour valider "big proc"
        #   → valeur au niveau catégorie = défaut ; entrée par type fusionne stat par stat (écrase)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    "KEEP_CRITERIA": {
            "never_used": {
                "eff_support": {2: 0.744, 3: 0.815, 4: 0.878},
                "eff_dps": {2: 0.744, 3: 0.818, 4: 0.877},
                "big_proc": {
                    "SPD": 24,
                    "CR": 24,
                    "CD": 28,
                    "ATK%": 32,
                    "HP%": 32,
                    "DEF%": 32,
                    "ACC": 32,
                    "RES": 32,
                },
                # "slot_135": default
                # "main_not_important": default
                "ATK%": {"eff_dps": {2: 0.685, 3: 0.765, 4: 0.834}, "big_proc": {"SPD": 22, "CR": 22, "CD": 26}},
                "HP%": {"eff_support": {2: 0.685, 3: 0.768, 4: 0.833}, "big_proc": {"SPD": 22, "ATK%": 30, "DEF%": 30}},
                # "DEF%": default
                "CD": {"eff_dps": {2: 0.685, 3: 0.765, 4: 0.830}, "big_proc": {"SPD": 22, "CR": 22, "ATK%": 30}},
                "SPD": {"eff_support": {2: 0.685, 3: 0.765, 4: 0.830}, "eff_dps": {2: 0.685, 3: 0.765, 4: 0.830}, "big_proc": {"CR": 22, "CD": 26, "ATK%": 30, "HP%": 30, "DEF%": 30}},
            },
            "little_used": {
                "eff_support": {2: 0.714, 3: 0.786, 4: 0.863},
                "eff_dps": {2: 0.714, 3: 0.786, 4: 0.855},
                "big_proc": {
                    "SPD": 23,
                    "CR": 23,
                    "CD": 27,
                    "ATK%": 31,
                    "HP%": 31,
                    "DEF%": 31,
                    "ACC": 32,
                    "RES": 32,
                },
                "slot_135": {"big_proc": {"SPD": 21, "CR": 20, "CD": 24, "ATK%": 27, "HP%": 27, "DEF%": 27}},
                "ATK%": {"eff_dps": {2: 0.664, 3: 0.744, 4: 0.812}, "big_proc": {"SPD": 21, "CR": 20, "CD": 24, "HP%": 27, "DEF%": 27}},
                "HP%": {"eff_support": {2: 0.664, 3: 0.747, 4: 0.813}, "big_proc": {"SPD": 21, "ATK%": 27, "DEF%": 27}},
                "CD": {"eff_dps": {2: 0.664, 3: 0.744, 4: 0.812}, "big_proc": {"SPD": 21, "CR": 20, "ATK%": 27, "HP%": 27, "DEF%": 27}},
                "SPD": {"eff_support": {2: 0.664, 3: 0.744, 4: 0.812}, "eff_dps": {2: 0.664, 3: 0.744, 4: 0.812}, "big_proc": {"CR": 20, "CD": 24, "ATK%": 27, "HP%": 27, "DEF%": 27}},
            },
            "nemesis": {
                "eff_support": {2: 0.714, 3: 0.786, 4: 0.863},
                "eff_dps": {2: 0.714, 3: 0.786, 4: 0.855},
                "big_proc": {
                    "SPD": 23,
                    "CR": 23,
                    "CD": 27,
                    "ATK%": 31,
                    "HP%": 31,
                    "DEF%": 31,
                    "ACC": 32,
                    "RES": 32,
                },
                "slot_135": {"eff_dps": {2: 0.673, 3: 0.753, 4: 0.824}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "ATK%": {"eff_dps": {2: 0.673, 3: 0.756, 4: 0.825}, "big_proc": {"CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "HP%": {"eff_support": {2: 0.673, 3: 0.756, 4: 0.825}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "SPD": 21}},
                "CD": {"eff_dps": {2: 0.673, 3: 0.756, 4: 0.825}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.673, 3: 0.756, 4: 0.824}, "eff_dps": {2: 0.673, 3: 0.753, 4: 0.824}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27}},
            },
            "offensive_little_used": {
                "eff_support": {2: 0.744, 3: 0.815, 4: 0.878},
                "eff_dps": {2: 0.744, 3: 0.818, 4: 0.874},
                "big_proc": {
                    "SPD": 23,
                    "CR": 23,
                    "CD": 27,
                    "ATK%": 31,
                    "HP%": 31,
                    "DEF%": 31,
                    "ACC": 32,
                    "RES": 32,
                },
                "slot_135": {"eff_dps": {2: 0.714, 3: 0.786, 4: 0.855}, "big_proc": {"SPD": 21, "CR": 20, "CD": 25, "ATK%": 28, "HP%": 30, "DEF%": 30}},
                "ATK%": {"eff_dps": {2: 0.711, 3: 0.786, 4: 0.855}},
                "HP%": {"eff_support": {2: 0.711, 3: 0.786, 4: 0.855}, "big_proc": {"SPD": 21, "CR": 20, "CD": 24, "ATK%": 28, "DEF%": 28}},
                "CD": {"eff_dps": {2: 0.708, 3: 0.789, 4: 0.854}, "big_proc": {"SPD": 21, "CR": 20, "ATK%": 28, "HP%": 28, "DEF%": 28}},
                "SPD": {"eff_support": {2: 0.711, 3: 0.786, 4: 0.851}, "eff_dps": {2: 0.711, 3: 0.786, 4: 0.855}, "big_proc": {"CR": 20, "CD": 24, "ATK%": 28, "HP%": 28, "DEF%": 28}},
            },
            "offensive_used": {
                "eff_support": {2: 0.685, 3: 0.768, 4: 0.836},
                "eff_dps": {2: 0.685, 3: 0.765, 4: 0.834},
                "big_proc": {
                    "SPD": 22,
                    "CR": 21,
                    "CD": 26,
                    "ATK%": 28,
                    "HP%": 30,
                    "DEF%": 30,
                    "ACC": 30,
                    "RES": 30,
                },
                "slot_135": {"big_proc": {"SPD": 21, "CR": 20, "CD": 24, "ATK%": 27}},
                "ATK%": {"eff_dps": {2: 0.631, 3: 0.717, 4: 0.791}, "big_proc": {"SPD": 21, "CR": 20, "CD": 24}},
                "CD": {"eff_dps": {2: 0.631, 3: 0.717, 4: 0.791}, "big_proc": {"SPD": 21, "CR": 20, "ATK%": 27}},
                "SPD": {"eff_dps": {2: 0.631, 3: 0.717, 4: 0.791}, "big_proc": {"CR": 20, "CD": 24, "ATK%": 27}},
            },
            "fast": {
                "eff_support": {2: 0.744, 3: 0.815, 4: 0.878},
                "eff_dps": {2: 0.744, 3: 0.818, 4: 0.877},
                "big_proc": {
                    "SPD": 23,
                    "CR": 21,
                    "CD": 27,
                    "ATK%": 30,
                    "HP%": 30,
                    "DEF%": 30,
                    "ACC": 32,
                    "RES": 32,
                },
                "ATK%": {"eff_dps": {2: 0.658, 3: 0.744, 4: 0.814}, "big_proc": {"SPD": 21, "CR": 20, "CD": 24}},
                "HP%": {"eff_support": {2: 0.655, 3: 0.747, 4: 0.813}},
                "CD": {"eff_dps": {2: 0.658, 3: 0.744, 4: 0.814}, "big_proc": {"SPD": 21, "CR": 20, "ATK%": 27}},
                "SPD": {"eff_support": {2: 0.658, 3: 0.744, 4: 0.814}, "eff_dps": {2: 0.658, 3: 0.744, 4: 0.814}},
            },
            "used": {
                "eff_support": {2: 0.676, 3: 0.756, 4: 0.824},
                "eff_dps": {2: 0.676, 3: 0.756, 4: 0.831},
                "big_proc": {
                    "SPD": 22,
                    "CR": 21,
                    "CD": 26,
                    "ATK%": 28,
                    "HP%": 28,
                    "DEF%": 28,
                    "ACC": 30,
                    "RES": 30,
                },
                "slot_135": {"big_proc": {"SPD": 21, "CR": 20, "CD": 24, "ATK%": 27, "HP%": 27, "DEF%": 27}},
                "ATK%": {"eff_dps": {2: 0.652, 3: 0.732, 4: 0.812}, "big_proc": {"SPD": 21, "CR": 20, "CD": 24, "HP%": 27, "DEF%": 27}},
                "HP%": {"eff_support": {2: 0.652, 3: 0.732, 4: 0.812}, "big_proc": {"SPD": 21, "ATK%": 27, "DEF%": 27}},
                "CD": {"eff_dps": {2: 0.652, 3: 0.732, 4: 0.812}, "big_proc": {"SPD": 21, "CR": 20, "ATK%": 27, "HP%": 27, "DEF%": 27}},
                "SPD": {"eff_support": {2: 0.652, 3: 0.735, 4: 0.813}, "eff_dps": {2: 0.652, 3: 0.732, 4: 0.812}, "big_proc": {"CR": 20, "CD": 24, "ATK%": 27, "HP%": 27, "DEF%": 27}},
            },
            "very_used": {
                "eff_support": {2: 0.655, 3: 0.738, 4: 0.804},
                "eff_dps": {2: 0.655, 3: 0.741, 4: 0.803},
                "big_proc": {
                    "SPD": 22,
                    "CR": 21,
                    "CD": 26,
                    "ATK%": 28,
                    "HP%": 28,
                    "DEF%": 28,
                    "ACC": 30,
                    "RES": 30,
                },
                "slot_135": {"big_proc": {"SPD": 21, "CR": 20, "CD": 24, "ATK%": 27, "HP%": 27, "DEF%": 27}},
                "ATK%": {"eff_dps": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"SPD": 21, "CR": 20, "CD": 24, "HP%": 27, "DEF%": 27}},
                "HP%": {"eff_support": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"SPD": 21, "ATK%": 27, "DEF%": 27}},
                "CD": {"eff_dps": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"SPD": 21, "CR": 20, "ATK%": 27, "HP%": 27, "DEF%": 27}},
                "SPD": {"eff_support": {2: 0.634, 3: 0.726, 4: 0.774}, "eff_dps": {2: 0.634, 3: 0.729, 4: 0.778}, "big_proc": {"CR": 20, "CD": 24, "ATK%": 27, "HP%": 27, "DEF%": 27}},
            },
            "other": {
                "eff_support": {2: 0.655, 3: 0.738, 4: 0.804},
                "eff_dps": {2: 0.655, 3: 0.741, 4: 0.803},
                "big_proc": {
                    "SPD": 22,
                    "CR": 21,
                    "CD": 26,
                    "ATK%": 28,
                    "HP%": 28,
                    "DEF%": 28,
                    "ACC": 30,
                    "RES": 30,
                },
                "slot_135": {"big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "ATK%": {"eff_dps": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "HP%": {"eff_support": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"ATK%": 27, "DEF%": 27, "SPD": 21}},
                "CD": {"eff_dps": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.634, 3: 0.726, 4: 0.774}, "eff_dps": {2: 0.634, 3: 0.729, 4: 0.778}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27}},
            },
        },
        # --- Quelles main stats/slots sont "importantes" ---
        # None = tous les slots; sinon set de slots concernés
        "MAIN_IMPORTANT": {
            "SPD": None,  # tous les slots
            "CD": None,
            "ATK%": {2, 6},  # slots 2 et 6
            "HP%": {4, 6},
            # "DEF%": {4, 6},
        },
        # 1 proc max en community eff
        "PROC_EQ": 1.0 / 14.0,
        # * save rune settings
    },
    "save_rune_settings": {
        "BUNDLE_BASE_DIR": {
            # "KEEP": "runes/data1/keep/img",
            # "SELL": "runes/data1/sell/img",
            # "TEST": "runes/data1/test/img",
            "KEEP": None,
            "SELL": None,
            "TEST": None,
        },
        "LOG_FILE": {
            "KEEP": "runes/data1/keep/keep_log.txt",
            "SELL": "runes/data1/sell/sell_log.txt",
            "TEST": "runes/data1/test/test_log.txt",
        },
        "JSONL_FILE": {
            "KEEP": "runes/data1/keep/keep_log.jsonl",
            "SELL": "runes/data1/sell/sell_log.jsonl",
            "TEST": "runes/data1/test/test_log.jsonl",
        },
    },
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
    # * store units in building
    "store_units": {
        "monsters": True,
        "arcemons": True,
    },
    # * perform daily summon
    "daily_summon": True,
    # * dungeon to run
    "dungeon": {
        "dungeon": Dungeon.GIANT,  # * dungeon type
        "30x10_run": True,  # * run mode x30 or x10
        "stop_after_current_energy": False,  # * stop dungeon if no current energy(no refill)
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
    # * regular arena setting
    "arena": {
        "arena": True,  # * do regular arena or not
        # * rival team images
        "img": {
            "rival_team": "img/rival_team.png",
            "rival_shortcut": "img/rival_shortcut.png",
        },
        # * interserver settings
        "interserver": {
            "interserver": True,  # * do interserver or not
            "collect_rewards": True,
            "img": {
                "team": "img/arena_team.png",
                "shortcut": "img/arena_shortcut.png",
                "spells": {
                    "unit1": {
            "s1": [("img/woonsa_s1.png",)],
            "spells": [
            ("img/woonsa_s3.png",),
            ("img/woonsa_s2.png",),
            ],
                    },
                    "unit2": {
            "s1": [("img/craig_s1.png",)],
            "spells": [
            ("img/craig_s3.png",),
            ("img/craig_s2.png",),
            ],
                    },
                    "unit3": {
            "s1": [("img/maxi_s1.png",)],
            "spells": [
            ("img/maxi_s3.png",),
            ("img/maxi_s2.png",),
            ],
                    },
                    "unit4": {
            "s1": [
            ("img/psama_s1.png",),
            ],
            "spells": [
            ("img/psama_s2.png",),
            ],
                    },
                },
            },
        },
        # * items to buy in arena shop
        "buy_arena_shop": {
            "relic": {
                "relic": True,
                "buy_until_day": Day.FRIDAY,
            },
            "relic_stones": True,
            "diablemon": True,  # * diablemon
            "ld_pieces": True,  # * ld pieces
            "ms": True,  # * mystical scroll
            "transmog_pieces": True,  # * transmog pieces in rta shop
            "arcemon": True,  # * arcemon in guild shop
        },
    },
    "world_boss": {
        "world_boss": True,
        "stop_after_current_energy": False,
    },
    "event_dungeons": {
        "mana": True,
        "diablemon": True,
        "arcemon": True,
        "stop_after_current_energy": False,
    },
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
            # * later: update images when preset will no longer be bugged
            # "img": {
            #     "teams": {
            #         "team1": "img/gvgw_team1.png",
            #         "team2": "img/gvgw_team2.png",
            #         "team3": "img/gvgw_team3.png",
            #         "team4": "img/gvgw_team4.png",
            #         "team5": "img/gvgw_team5.png",
            #     },
            #     "shortcuts": {
            #         "shortcut1": "img/gvgw_shortcut1.png",
            #         "shortcut2": "img/gvgw_shortcut2.png",
            #         "shortcut3": "img/gvgw_shortcut3.png",
            #         "shortcut4": "img/gvgw_shortcut4.png",
            #         "shortcut5": "img/gvgw_shortcut5.png",
            #     },
            # },
        },
        "collect_siege_rewards": True,
    },
    # * rta settings
    "rta": {
        "rta": Rta.REGULAR,
        "img": {
            "regular": {
                # * regular rta team (order matter in picking phase)
                "team": [
                    {"path": "img/maxi_icon.png"},
                    {"path": "img/wind_robo_icon.png"},
                    {"path": "img/dark_robo_icon.png"},
                    {"path": "img/beth_icon.png"},
                    {"path": "img/shimitae_icon.png"},
                ],
                "spells": {
                    "unit1": {
            "s1": [("img/wind_robo_s1.png",)],
            "spells": [
            ("img/wind_robo_s2.png",),
            ("img/wind_robo_s3.png",),
            ],
                    },
                    "unit2": {
            "s1": [("img/dark_robo_s1.png",)],
            "spells": [
            ("img/dark_robo_s2.png",),
            ("img/dark_robo_s3.png",),
            ],
                    },
                    "unit3": {
            "s1": [
            ("img/beth_s1.png",),
            ],
            "spells": [
            ("img/beth_s3.png",),
            ("img/beth_s2.png",),
            ],
                    },
                    "unit4": {
            "s1": [("img/maxi_s1.png",)],
            "spells": [
            ("img/maxi_s3.png",),
            ("img/maxi_s2.png",),
            ],
                    },
                    "unit5": {
            "s1": [("img/shimitae_s1.png",)],
            "spells": [
            ("img/shimitae_s2.png",),
            ("img/shimitae_s3.png",),
            ],
                    },
                },
            },
            "sl_four_stars_only": {
                # * four stars only rta team (order matter in picking phase)
                "team": [
                    {"path": "img/shimitae_icon.png"},
                    {"path": "img/draco_icon.png"},
                    {"path": "img/pralin_icon.png"},
                    {"path": "img/lushen_icon.png"},
                    {"path": "img/julie_icon.png"},
                ],
                "spells": {
                    "unit1": {
            "s1": [("img/draco_s1.png",)],
            "spells": [
            ("img/draco_s3.png",),
            ("img/draco_s2.png",),
            ],
                    },
                    "unit2": {
            "s1": [("img/pralin_s1.png",)],
            "spells": [
            ("img/pralin_s3.png",),
            ("img/pralin_s2.png",),
            ],
                    },
                    "unit3": {
            "s1": [("img/shimitae_s1.png",)],
            "spells": [
            ("img/shimitae_s2.png",),
            ("img/shimitae_s3.png",),
            ],
                    },
                    "unit4": {
            "s1": [
            ("img/julie_s1.png",),
            ],
            "spells": [
            ("img/julie_s3.png", DEFAULT_CONFIDENCE - 0.2),
            ("img/julies_s2.png",),
            ],
                    },
                    "unit5": {
            "s1": [("img/lushen_s1.png",)],
            "spells": [
            ("img/lushen_s3.png",),
            ("img/lushen_s2.png",),
            ],
                    },
                },
            },
            "sl_rgb_only": {
                # * only wind, fire and water elements only
                "team": [
                    {"path": "img/clara_icon.png"},
                    {"path": "img/wind_robo_icon.png"},
                    {"path": "img/shimitae_icon.png"},
                    {"path": "img/liesel_icon.png"},
                    {"path": "img/beth_icon.png"},
                ],
                "spells": {
                    "unit1": {
            "s1": [("img/clara_s1.png",)],
            "spells": [
            ("img/clara_s3.png", DEFAULT_CONFIDENCE - 0.2),
            ("img/clara_s2.png",),
            ],
                    },
                    "unit2": {
            "s1": [("img/wind_robo_s1.png",)],
            "spells": [
            ("img/wind_robo_s2.png",),
            ("img/wind_robo_s3.png",),
            ],
                    },
                    "unit3": {
            "s1": [
            ("img/bellenus_form1_s1.png",),
            ("img/bellenus_form2_s1.png",),
            ],
            "spells": [
            ("img/bellenus_form1_s3.png",),
            ("img/bellenus_form2_s2.png",),
            ],
                    },
                    "unit4": {
            "s1": [
            ("img/liesel_s1.png",),
            ],
            "spells": [
            ("img/liesel_s3.png",),
            ("img/liesel_s2.png",),
            ],
                    },
                    "unit5": {
            "s1": [("img/shimitae_s1.png",)],
            "spells": [
            ("img/shimitae_s2.png",),
            ("img/shimitae_s3.png",),
            ],
                    },
                },
            },
        },
    },
    "hoh": {
        "hoh": True,
        "max_losses": 3,
        "stop_after_current_energy": True,
    },
    "toa": {
        "toa": True,
        "difficulty_toa_normal": 1,  # * from 1 to 6
        "difficulty_toa_hard": 1,  # * from 1 to 6
        "img": {
            "team1": {
                "team": "img/toa_team1_1.png",
                "shortcut": "img/toa_shortcut_team1_1.png",
            },
            "team2": {
                "team": "img/toa_team2_1.png",
                "shortcut": "img/toa_shortcut_team2_1.png",
            },
            "team3": {
                "team": "img/toa_team3_1.png",
                "shortcut": "img/toa_shortcut_team3_1.png",
            },
        },
        "stop_after_current_energy": False,
    },
}

# light Werner/Lora account
data2 = {
    # * upgrade rune settings
    "upgrade_rune_settings": {
        # --- Profilage eff (ACC/RES ignorés) ---
        "EFF_GROUP_SUPPORT": {"SPD", "HP%", "DEF%", "ATK%"},
        "EFF_GROUP_DPS": {"SPD", "ATK%", "CR", "CD"},
        "IGNORED_SUBS": {
            "ACC",
            "RES",
            "ATK",
            "HP",
            "DEF",
        },  # ignorés dans eff + comptage good
        # --- Set categories ---
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_NEVER_USED": {
            "Amelioration",
            "Determination",
            "Endurance",
            "Focus",
            "Gardien",
            "Precision",
            "Protection",
            "Toleration",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_LITTLE_USED": {
            "Combat",
            "Destruction",
            "Energie",
            "Sceau",
            "Vengeance",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_NEMESIS": {
            "Nemesis",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_OFFENSIVE_LITTLE_USED": {
            "Fatale",
            "Vampire",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_OFFENSIVE_USED": {
            "Lame",
            "Rage",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_FAST": {
            "Rapide",
        },  # swift
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_USED": {
            "Desespoir",
        },
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "SETS_VERY_USED": {
            "Intangible",
            "Violent",
            "Volonte",
        },
        # --- Conditions par catégorie (eff + big_proc) ---
        # eff_support / eff_dps : {bucket: seuil} où bucket = nb de good subs (2/3/4)
        #   → valeur au niveau catégorie = défaut pour tous les types de rune de cette catégorie
        #   → entrée par type ("ATK%", "slot_135", …) écrase le défaut pour ce type uniquement
        # big_proc : {stat: seuil} seuil absolu d'un seul sub pour valider "big proc"
        #   → valeur au niveau catégorie = défaut ; entrée par type fusionne stat par stat (écrase)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    "KEEP_CRITERIA": {
            "never_used": {
                "eff_support": {2: 0.744, 3: 0.815, 4: 0.878},
                "eff_dps": {2: 0.744, 3: 0.818, 4: 0.874},
                "big_proc": {
                    "SPD": 24,
                    "CR": 24,
                    "CD": 28,
                    "ATK%": 32,
                    "HP%": 32,
                    "DEF%": 32,
                    "ACC": 32,
                    "RES": 32,
                },
                # "slot_135": default
                # "main_not_important": default
                "ATK%": {"eff_dps": {2: 0.685, 3: 0.765, 4: 0.834}, "big_proc": {"CD": 26, "CR": 22, "SPD": 22}},
                "HP%": {"eff_support": {2: 0.685, 3: 0.768, 4: 0.833}, "big_proc": {"ATK%": 30, "DEF%": 30, "SPD": 22}},
                # "DEF%": default
                "CD": {"eff_dps": {2: 0.685, 3: 0.765, 4: 0.830}, "big_proc": {"ATK%": 30, "CR": 22, "SPD": 22}},
                "SPD": {"eff_support": {2: 0.685, 3: 0.765, 4: 0.830}, "eff_dps": {2: 0.685, 3: 0.765, 4: 0.830}, "big_proc": {"ATK%": 30, "CD": 26, "CR": 22, "DEF%": 30, "HP%": 30}},
            },
            "little_used": {
                "eff_support": {2: 0.714, 3: 0.786, 4: 0.863},
                "eff_dps": {2: 0.714, 3: 0.786, 4: 0.855},
                "big_proc": {
                    "SPD": 23,
                    "CR": 23,
                    "CD": 27,
                    "ATK%": 31,
                    "HP%": 31,
                    "DEF%": 31,
                    "ACC": 32,
                    "RES": 32,
                },
                "slot_135": {"big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "ATK%": {"eff_dps": {2: 0.664, 3: 0.744, 4: 0.812}, "big_proc": {"CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "HP%": {"eff_support": {2: 0.664, 3: 0.747, 4: 0.813}, "big_proc": {"ATK%": 27, "DEF%": 27, "SPD": 21}},
                "CD": {"eff_dps": {2: 0.664, 3: 0.744, 4: 0.812}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.664, 3: 0.744, 4: 0.812}, "eff_dps": {2: 0.664, 3: 0.744, 4: 0.812}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27}},
            },
            "nemesis": {
                "eff_support": {2: 0.714, 3: 0.786, 4: 0.863},
                "eff_dps": {2: 0.714, 3: 0.786, 4: 0.855},
                "big_proc": {
                    "SPD": 23,
                    "CR": 23,
                    "CD": 27,
                    "ATK%": 31,
                    "HP%": 31,
                    "DEF%": 31,
                    "ACC": 32,
                    "RES": 32,
                },
                "slot_135": {"eff_dps": {2: 0.673, 3: 0.753, 4: 0.824}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "ATK%": {"eff_dps": {2: 0.673, 3: 0.756, 4: 0.825}, "big_proc": {"CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "HP%": {"eff_support": {2: 0.673, 3: 0.756, 4: 0.825}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "SPD": 21}},
                "CD": {"eff_dps": {2: 0.673, 3: 0.756, 4: 0.825}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.673, 3: 0.756, 4: 0.824}, "eff_dps": {2: 0.673, 3: 0.753, 4: 0.824}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27}},
            },
            "offensive_little_used": {
                "eff_support": {2: 0.744, 3: 0.815, 4: 0.878},
                "eff_dps": {2: 0.744, 3: 0.818, 4: 0.874},
                "big_proc": {
                    "SPD": 23,
                    "CR": 23,
                    "CD": 27,
                    "ATK%": 31,
                    "HP%": 31,
                    "DEF%": 31,
                    "ACC": 32,
                    "RES": 32,
                },
                "slot_135": {"eff_dps": {2: 0.708, 3: 0.789, 4: 0.854}, "big_proc": {"ATK%": 28, "CD": 25, "CR": 20, "DEF%": 30, "HP%": 30, "SPD": 21}},
                "ATK%": {"eff_dps": {2: 0.711, 3: 0.786, 4: 0.855}},
                "HP%": {"eff_support": {2: 0.711, 3: 0.786, 4: 0.855}, "big_proc": {"ATK%": 28, "CD": 24, "CR": 20, "DEF%": 28, "SPD": 21}},
                "CD": {"eff_dps": {2: 0.708, 3: 0.789, 4: 0.854}, "big_proc": {"ATK%": 28, "CR": 20, "DEF%": 28, "HP%": 28, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.711, 3: 0.786, 4: 0.851}, "eff_dps": {2: 0.711, 3: 0.786, 4: 0.855}, "big_proc": {"ATK%": 28, "CD": 24, "CR": 20, "DEF%": 28, "HP%": 28}},
            },
            "offensive_used": {
                "eff_support": {2: 0.685, 3: 0.768, 4: 0.836},
                "eff_dps": {2: 0.685, 3: 0.765, 4: 0.834},
                "big_proc": {
                    "SPD": 22,
                    "CR": 21,
                    "CD": 26,
                    "ATK%": 28,
                    "HP%": 30,
                    "DEF%": 30,
                    "ACC": 30,
                    "RES": 30,
                },
                "slot_135": {"big_proc": {"SPD": 21, "CR": 20, "CD": 24, "ATK%": 27}},
                "ATK%": {"eff_dps": {2: 0.631, 3: 0.717, 4: 0.791}, "big_proc": {"SPD": 21, "CR": 20, "CD": 24}},
                "CD": {"eff_dps": {2: 0.631, 3: 0.717, 4: 0.791}, "big_proc": {"SPD": 21, "CR": 20, "ATK%": 27}},
                "SPD": {"eff_dps": {2: 0.631, 3: 0.717, 4: 0.791}, "big_proc": {"CR": 20, "CD": 24, "ATK%": 27}},
            },
            "fast": {
                "eff_support": {2: 0.741, 3: 0.815, 4: 0.881},
                "eff_dps": {2: 0.741, 3: 0.815, 4: 0.881},
                "big_proc": {
                    "SPD": 23,
                    "CR": 21,
                    "CD": 27,
                    "ATK%": 30,
                    "HP%": 30,
                    "DEF%": 30,
                    "ACC": 32,
                    "RES": 32,
                },
                "ATK%": {"eff_dps": {2: 0.658, 3: 0.744, 4: 0.814}, "big_proc": {"CD": 24, "CR": 20, "SPD": 21}},
                "HP%": {"eff_support": {2: 0.655, 3: 0.747, 4: 0.813}},
                "CD": {"eff_dps": {2: 0.658, 3: 0.744, 4: 0.814}, "big_proc": {"ATK%": 27, "CR": 20, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.658, 3: 0.744, 4: 0.814}, "eff_dps": {2: 0.658, 3: 0.744, 4: 0.814}},
            },
            "used": {
                "eff_support": {2: 0.676, 3: 0.756, 4: 0.824},
                "eff_dps": {2: 0.676, 3: 0.756, 4: 0.831},
                "big_proc": {
                    "SPD": 22,
                    "CR": 21,
                    "CD": 26,
                    "ATK%": 28,
                    "HP%": 28,
                    "DEF%": 28,
                    "ACC": 30,
                    "RES": 30,
                },
                "slot_135": {"big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "ATK%": {"eff_dps": {2: 0.652, 3: 0.732, 4: 0.812}, "big_proc": {"CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "HP%": {"eff_support": {2: 0.652, 3: 0.732, 4: 0.812}, "big_proc": {"ATK%": 27, "DEF%": 27, "SPD": 21}},
                "CD": {"eff_dps": {2: 0.652, 3: 0.732, 4: 0.812}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.652, 3: 0.732, 4: 0.812}, "eff_dps": {2: 0.652, 3: 0.732, 4: 0.812}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27}},
            },
            "very_used": {
                "eff_support": {2: 0.655, 3: 0.738, 4: 0.804},
                "eff_dps": {2: 0.655, 3: 0.741, 4: 0.803},
                "big_proc": {
                    "SPD": 22,
                    "CR": 21,
                    "CD": 26,
                    "ATK%": 28,
                    "HP%": 28,
                    "DEF%": 28,
                    "ACC": 30,
                    "RES": 30,
                },
                "slot_135": {"big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "ATK%": {"eff_dps": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "HP%": {"eff_support": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"ATK%": 27, "DEF%": 27, "SPD": 21}},
                "CD": {"eff_dps": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.634, 3: 0.726, 4: 0.774}, "eff_dps": {2: 0.634, 3: 0.729, 4: 0.778}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27}},
            },
            "other": {
                "eff_support": {2: 0.655, 3: 0.738, 4: 0.804},
                "eff_dps": {2: 0.655, 3: 0.741, 4: 0.803},
                "big_proc": {
                    "SPD": 22,
                    "CR": 21,
                    "CD": 26,
                    "ATK%": 28,
                    "HP%": 28,
                    "DEF%": 28,
                    "ACC": 30,
                    "RES": 30,
                },
                "slot_135": {"big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "ATK%": {"eff_dps": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"CD": 24, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "HP%": {"eff_support": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"ATK%": 27, "DEF%": 27, "SPD": 21}},
                "CD": {"eff_dps": {2: 0.631, 3: 0.726, 4: 0.774}, "big_proc": {"ATK%": 27, "CR": 20, "DEF%": 27, "HP%": 27, "SPD": 21}},
                "SPD": {"eff_support": {2: 0.634, 3: 0.726, 4: 0.774}, "eff_dps": {2: 0.634, 3: 0.729, 4: 0.778}, "big_proc": {"ATK%": 27, "CD": 24, "CR": 20, "DEF%": 27, "HP%": 27}},
            },
        },
        # --- Quelles main stats/slots sont "importantes" ---
        # None = tous les slots; sinon set de slots concernés
        "MAIN_IMPORTANT": {
            "SPD": None,  # tous les slots
            "CD": None,
            "ATK%": {2, 6},  # slots 2 et 6
            "HP%": {4, 6},
            # "DEF%": {4, 6},
        },
        # 1 proc max en community eff
        "PROC_EQ": 1.0 / 14.0,
        # * save rune settings
    },
    "save_rune_settings": {
        "BUNDLE_BASE_DIR": {
            # "KEEP": "runes/data2/keep/img",
            # "SELL": "runes/data2/sell/img",
            # "TEST": "runes/data2/test/img",
            "KEEP": None,
            "SELL": None,
            "TEST": None,
        },
        "LOG_FILE": {
            "KEEP": "runes/data2/keep/keep_log.txt",
            "SELL": "runes/data2/sell/sell_log.txt",
            "TEST": "runes/data2/test/test_log.txt",
        },
        "JSONL_FILE": {
            "KEEP": "runes/data2/keep/keep_log.jsonl",
            "SELL": "runes/data2/sell/sell_log.jsonl",
            "TEST": "runes/data2/test/test_log.jsonl",
        },
    },
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
    # * store units in building
    "store_units": {
        "monsters": True,
        "arcemons": True,
    },
    # * perform daily summon
    "daily_summon": True,
    # * which dungeon to run
    "dungeon": {
        "dungeon": Dungeon.RAID,  # * dungeon type
        "30x10_run": True,  # * run mode x30 or x10
        "stop_after_current_energy": False,  # * stop dungeon if no current energy(no refill)
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
    # * regular arena setting
    "arena": {
        "arena": True,  # * do regular arena or not
        # * rival team images
        "img": {
            "rival_team": "img/rival_team.png",
            "rival_shortcut": "img/rival_shortcut.png",
        },
        # * interserver settings
        "interserver": {
            "interserver": True,  # * do interserver or not
            "collect_rewards": True,
            "img": {
                "team": "img/arena_team_2.png",
                "shortcut": "img/arena_shortcut_2.png",
                "spells": {
                    "unit1": {
            "s1": [("img/dark_robo_s1.png",)],
            "spells": [
            ("img/dark_robo_s2.png",),
            ("img/dark_robo_s3.png",),
            ],
                    },
                    "unit2": {
            "s1": [("img/liesel_s1.png",)],
            "spells": [
            ("img/liesel_s3.png",),
            ("img/liesel_s2.png",),
            ],
                    },
                    "unit3": {
            "s1": [("img/kaki_s1.png",)],
            "spells": [
            ("img/kaki_s2.png",),
            ],
                    },
                    "unit4": {
            "s1": [
            ("img/shimitae_s1.png",),
            ],
            "spells": [
            ("img/shimitae_s2.png",),
            ("img/shimitae_s3.png",),
            ],
                    },
                },
            },
        },
        # * items to buy in arena shop
        "buy_arena_shop": {
            "relic": {
                "relic": True,
                "buy_until_day": Day.FRIDAY,
            },
            "relic_stones": True,
            "diablemon": True,  # * diablemon
            "ld_pieces": True,  # * ld pieces
            "ms": True,  # * mystical scroll
            "transmog_pieces": True,  # * transmog pieces in rta shop
            "arcemon": True,  # * arcemon in guild shop
        },
    },
    "world_boss": {
        "world_boss": True,
        "stop_after_current_energy": False,
    },
    "event_dungeons": {
        "mana": True,
        "diablemon": True,
        "arcemon": True,
        "stop_after_current_energy": False,
    },
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
            # * later: update images when preset will no longer be bugged
            # "img": {
            #     "teams": {
            #         "team1": "img/gvgw_team1_2.png",
            #         "team2": "img/gvgw_team2_2.png",
            #         "team3": "img/gvgw_team3_2.png",
            #         "team4": "img/gvgw_team4_2.png",
            #         "team5": "img/gvgw_team5_2.png",
            #     },
            #     "shortcuts": {
            #         "shortcut1": "img/gvgw_shortcut1_2.png",
            #         "shortcut2": "img/gvgw_shortcut2_2.png",
            #         "shortcut3": "img/gvgw_shortcut3_2.png",
            #         "shortcut4": "img/gvgw_shortcut4_2.png",
            #         "shortcut5": "img/gvgw_shortcut5_2.png",
            #     },
            # },
            "collect_siege_rewards": True,
        },
    },
    "rta": {
        "rta": Rta.REGULAR,
        "img": {
            "regular": {
                # * regular rta team (order matter in picking phase)
                "team": [
                    {"path": "img/light_werner_icon.png"},
                    {"path": "img/dark_robo_icon.png"},
                    {"path": "img/liesel_icon.png"},
                    {"path": "img/prom_icon.png"},
                    {"path": "img/shimitae_icon.png"},
                ],
                "spells": {
                    "unit1": {
            "s1": [("img/light_werner_s1.png",)],
            "spells": [
            ("img/light_werner_s2.png",),
            ("img/light_werner_s3.png",),
            ],
                    },
                    "unit2": {
            "s1": [("img/dark_robo_s1.png",)],
            "spells": [
            ("img/dark_robo_s2.png",),
            ("img/dark_robo_s3.png",),
            ],
                    },
                    "unit3": {
            "s1": [("img/prom_s1.png",)],
            "spells": [
            ("img/prom_s3.png",),
            ("img/prom_s2.png",),
            ],
                    },
                    "unit4": {
            "s1": [("img/liesel_s1.png",)],
            "spells": [
            ("img/liesel_s3.png",),
            ("img/liesel_s2.png",),
            ],
                    },
                    "unit5": {
            "s1": [("img/shimitae_s1.png",)],
            "spells": [
            ("img/shimitae_s2.png",),
            ("img/shimitae_s3.png",),
            ],
                    },
                },
            },
            "sl_rgb_only": {
                # * four stars only rta team (order matter in picking phase)
                "team": [
                    {"path": "img/clara_icon.png"},
                    {"path": "img/wind_robo_icon.png"},
                    {"path": "img/shimitae_icon.png"},
                    {"path": "img/liesel_icon.png"},
                    {"path": "img/jun_icon.png"},
                ],
                "spells": {
                    "unit1": {
            "s1": [("img/clara_s1.png",)],
            "spells": [
            ("img/clara_s3.png", DEFAULT_CONFIDENCE - 0.2),
            ("img/clara_s2.png",),
            ],
                    },
                    "unit2": {
            "s1": [("img/wind_robo_s1.png",)],
            "spells": [
            ("img/wind_robo_s2.png",),
            ("img/wind_robo_s3.png",),
            ],
                    },
                    "unit3": {
            "s1": [
            ("img/jun_s1.png",),
            ],
            "spells": [
            ("img/jun_s3.png",),
            ("img/jun_s4.png", DEFAULT_CONFIDENCE - 0.2),
            ("img/jun_s2.png",),
            ],
                    },
                    "unit4": {
            "s1": [
            ("img/liesel_s1.png",),
            ],
            "spells": [
            ("img/liesel_s3.png",),
            ("img/liesel_s2.png",),
            ],
                    },
                    "unit5": {
            "s1": [("img/shimitae_s1.png",)],
            "spells": [
            ("img/shimitae_s2.png",),
            ("img/shimitae_s3.png",),
            ],
                    },
                },
            },
        },
    },
    "hoh": {
        "hoh": True,
        "max_losses": 3,
        "stop_after_current_energy": True,
    },
    "toa": {
        "toa": True,
        "difficulty_toa_normal": 1,  # * from 1 to 6
        "difficulty_toa_hard": 1,  # * from 1 to 6
        "img": {
            "team1": {
                "team": "img/toa_team1_2.png",
                "shortcut": "img/toa_shortcut_team1_2.png",
            },
            "team2": {
                "team": "img/toa_team2_2.png",
                "shortcut": "img/toa_shortcut_team2_2.png",
            },
            "team3": {
                "team": "img/toa_team3_2.png",
                "shortcut": "img/toa_shortcut_team3_2.png",
            },
        },
        "stop_after_current_energy": False,
    },
}