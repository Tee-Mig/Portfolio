from __future__ import annotations

import re
import json
import cv2
import mss
import numpy as np
import pytesseract
import hashlib
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Literal, Any
from copy import deepcopy


_RUNTIME_KEY = "__runtime__"


# =========================================================
# SETTINGS (3 structures)
# =========================================================

RUNE_RULESETS: dict[str, dict[str, Any]] = {
    "default": {
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
            "Gardien",
            "Focus",
            "Endurance",
            "Determination",
            "Amelioration",
            "Precision",
            "Tolerance",
            "Protection",
        },
        "SETS_LITTLE_USED": {
            "Energie",
            "Vengeance",
            "Sceau",
            "Destruction",
            "Combat",
        },
        "SETS_NEMESIS": {"Nemesis"},
        "SETS_OFFENSIVE_LITTLE_USED": {"Fatale", "Vampire"},
        "SETS_OFFENSIVE_USED": {"Rage", "Lame"},
        "SETS_FAST": {"Rapide"},  # swift
        "SETS_USED": {"Desespoir"},
        "SETS_VERY_USED": {"Violent", "Volonte", "Intangible"},
        # --- Big proc thresholds (par catégorie) ---
        "BIG_PROC": {
            "never_used": {
                "SPD": 23,
                "CR": 23,
                "CD": 27,
                "ATK%": 31,
                "HP%": 31,
                "DEF%": 31,
                "ACC": 31,
                "RES": 31,
            },
            "little_used": {
                "SPD": 22,
                "CR": 22,
                "CD": 26,
                "ATK%": 30,
                "HP%": 30,
                "DEF%": 30,
                "ACC": 30,
                "RES": 30,
            },
            "nemesis": {
                "SPD": 21,
                "CR": 21,
                "CD": 26,
                "ATK%": 30,
                "HP%": 30,
                "DEF%": 30,
                "ACC": 30,
                "RES": 30,
            },
            "offensive_little_used": {
                "SPD": 22,
                "CR": 21,
                "CD": 25,
                "ATK%": 28,
                "HP%": 30,
                "DEF%": 30,
                "ACC": 30,
                "RES": 30,
            },
            "offensive_used": {
                "SPD": 21,
                "CR": 20,
                "CD": 24,
                "ATK%": 27,
                "HP%": 28,
                "DEF%": 28,
                "ACC": 30,
                "RES": 30,
            },
            "fast": {
                "SPD": 23,
                "CR": 21,
                "CD": 26,
                "ATK%": 30,
                "HP%": 30,
                "DEF%": 30,
                "ACC": 30,
                "RES": 30,
            },
            "used": {
                "SPD": 21,
                "CR": 20,
                "CD": 24,
                "ATK%": 28,
                "HP%": 28,
                "DEF%": 28,
                "ACC": 30,
                "RES": 30,
            },
            "very_used": {
                "SPD": 20,
                "CR": 20,
                "CD": 24,
                "ATK%": 26,
                "HP%": 26,
                "DEF%": 26,
                "ACC": 30,
                "RES": 30,
            },
            "other": {
                "SPD": 20,
                "CR": 20,
                "CD": 24,
                "ATK%": 26,
                "HP%": 26,
                "DEF%": 26,
                "ACC": 30,
                "RES": 30,
            },
        },
        # --- Quelles main stats/slots sont "importantes" ---
        # Valeur None = tous les slots; sinon set de slots concernés
        "MAIN_IMPORTANT": {
            "SPD": None,  # tous les slots
            "CD": None,
            "ATK%": {2, 6},
            "HP%": {4, 6},
        },
        # --- Efficiency thresholds ---
        # Structure par catégorie de set:
        #   slot_135          : runes slot 1/3/5 (main flat ATK/DEF/HP)
        #   main_important    : slots 2/4/6 avec main définie dans MAIN_IMPORTANT
        #   main_not_important: slots 2/4/6 avec les autres main stats
        #   Chaque entrée a: support (VIT,PV%,DEF%,ATK%) et dps (VIT,ATK%,CD,CR)
        # ATK%@2,6 : support plus exigeant (on veut des subs offensives sur main offensive)
        #            dps normal (main_important.dps)
        # HP%@4,6  : support normal (main_important.support)
        #            dps très exigeant (CD/CR sur rune HP% = inutile)
        "EFF_THRESHOLDS": {
            "never_used": {
                "slot_135": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.714, 3: 0.785, 4: 0.857},
                },
                "main_not_important": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.714, 3: 0.785, 4: 0.857},
                },
                "ATK%": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.696, 3: 0.767, 4: 0.838},
                },
                "HP%": {
                    "support": {2: 0.696, 3: 0.767, 4: 0.838},
                    "dps": {2: 0.714, 3: 0.785, 4: 0.857},
                },
                "CD": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.696, 3: 0.767, 4: 0.838},
                },
                "SPD": {
                    "support": {2: 0.696, 3: 0.767, 4: 0.838},
                    "dps": {2: 0.696, 3: 0.767, 4: 0.838},
                },
            },
            "little_used": {
                "slot_135": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "main_not_important": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "ATK%": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
                "HP%": {
                    "support": {2: 0.669, 3: 0.740, 4: 0.812},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "CD": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
                "SPD": {
                    "support": {2: 0.669, 3: 0.740, 4: 0.812},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
            },
            "nemesis": {
                "slot_135": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "main_not_important": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "ATK%": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
                "HP%": {
                    "support": {2: 0.669, 3: 0.740, 4: 0.812},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "CD": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
                "SPD": {
                    "support": {2: 0.669, 3: 0.740, 4: 0.812},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
            },
            "offensive_little_used": {
                "slot_135": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "main_not_important": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "ATK%": {
                    "support": {2: 0.696, 3: 0.767, 4: 0.838},
                    "dps": {2: 0.669, 3: 0.758, 4: 0.830},
                },
                "HP%": {
                    "support": {2: 0.669, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.696, 3: 0.767, 4: 0.838},
                },
                "CD": {
                    "support": {2: 0.696, 3: 0.767, 4: 0.838},
                    "dps": {2: 0.669, 3: 0.758, 4: 0.830},
                },
                "SPD": {
                    "support": {2: 0.696, 3: 0.767, 4: 0.838},
                    "dps": {2: 0.669, 3: 0.758, 4: 0.830},
                },
            },
            "offensive_used": {
                "slot_135": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.669, 3: 0.758, 4: 0.830},
                },
                "main_not_important": {
                    "support": {2: 0.714, 3: 0.785, 4: 0.857},
                    "dps": {2: 0.669, 3: 0.758, 4: 0.830},
                },
                "ATK%": {
                    "support": {2: 0.696, 3: 0.767, 4: 0.838},
                    "dps": {2: 0.651, 3: 0.722, 4: 0.794},
                },
                "HP%": {
                    "support": {2: 0.651, 3: 0.722, 4: 0.794},
                    "dps": {2: 0.696, 3: 0.767, 4: 0.838},
                },
                "CD": {
                    "support": {2: 0.696, 3: 0.767, 4: 0.838},
                    "dps": {2: 0.651, 3: 0.722, 4: 0.794},
                },
                "SPD": {
                    "support": {2: 0.696, 3: 0.767, 4: 0.838},
                    "dps": {2: 0.651, 3: 0.722, 4: 0.794},
                },
            },
            "fast": {
                "slot_135": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "main_not_important": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "ATK%": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
                "HP%": {
                    "support": {2: 0.669, 3: 0.740, 4: 0.812},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "CD": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
                "SPD": {
                    "support": {2: 0.669, 3: 0.740, 4: 0.812},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
            },
            "used": {
                "slot_135": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "main_not_important": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "ATK%": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
                "HP%": {
                    "support": {2: 0.669, 3: 0.740, 4: 0.812},
                    "dps": {2: 0.687, 3: 0.758, 4: 0.830},
                },
                "CD": {
                    "support": {2: 0.687, 3: 0.758, 4: 0.830},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
                "SPD": {
                    "support": {2: 0.669, 3: 0.740, 4: 0.812},
                    "dps": {2: 0.669, 3: 0.740, 4: 0.812},
                },
            },
            "very_used": {
                "slot_135": {
                    "support": {2: 0.661, 3: 0.732, 4: 0.803},
                    "dps": {2: 0.661, 3: 0.732, 4: 0.803},
                },
                "main_not_important": {
                    "support": {2: 0.661, 3: 0.732, 4: 0.803},
                    "dps": {2: 0.661, 3: 0.732, 4: 0.803},
                },
                "ATK%": {
                    "support": {2: 0.661, 3: 0.732, 4: 0.803},
                    "dps": {2: 0.643, 3: 0.714, 4: 0.785},
                },
                "HP%": {
                    "support": {2: 0.643, 3: 0.714, 4: 0.785},
                    "dps": {2: 0.661, 3: 0.732, 4: 0.803},
                },
                "CD": {
                    "support": {2: 0.661, 3: 0.732, 4: 0.803},
                    "dps": {2: 0.643, 3: 0.714, 4: 0.785},
                },
                "SPD": {
                    "support": {2: 0.643, 3: 0.714, 4: 0.785},
                    "dps": {2: 0.643, 3: 0.714, 4: 0.785},
                },
            },
            "other": {
                "slot_135": {
                    "support": {2: 0.661, 3: 0.732, 4: 0.803},
                    "dps": {2: 0.661, 3: 0.732, 4: 0.803},
                },
                "main_not_important": {
                    "support": {2: 0.661, 3: 0.732, 4: 0.803},
                    "dps": {2: 0.661, 3: 0.732, 4: 0.803},
                },
                "ATK%": {
                    "support": {2: 0.661, 3: 0.732, 4: 0.803},
                    "dps": {2: 0.643, 3: 0.714, 4: 0.785},
                },
                "HP%": {
                    "support": {2: 0.643, 3: 0.714, 4: 0.785},
                    "dps": {2: 0.661, 3: 0.732, 4: 0.803},
                },
                "CD": {
                    "support": {2: 0.661, 3: 0.732, 4: 0.803},
                    "dps": {2: 0.643, 3: 0.714, 4: 0.785},
                },
                "SPD": {
                    "support": {2: 0.643, 3: 0.714, 4: 0.785},
                    "dps": {2: 0.643, 3: 0.714, 4: 0.785},
                },
            },
        },
        # --- Rolls config (6★) ---
        "MAX_ROLL": {
            "HP%": 8,
            "ATK%": 8,
            "DEF%": 8,
            "SPD": 6,
            "CR": 6,
            "CD": 7,
            "ACC": 8,
            "RES": 8,
            "ATK": 20,
            "HP": 375,
            "DEF": 20,
        },
        # 1 proc max en community eff
        "PROC_EQ": 1.0 / 14.0,
    }
}

OCR_PRESETS: dict[str, dict[str, Any]] = {
    "default": {
        # --- BBOX capture ---
        "REGION_UPGRADE_TYPE_SLOT": (284, 298, 617, 62),
        "REGION_GRADE": (708, 364, 200, 54),
        "REGION_MAIN_INNATE": (425, 357, 315, 140),
        "REGION_SUBS": (267, 489, 632, 197),
        # --- Ancient detection ---
        "ANCIENT_TPL_HERO_PATH": "img/ancient_icon_heroic.png",
        "ANCIENT_TPL_LEGEND_PATH": "img/ancient_icon_legend.png",
        "ANCIENT_MATCH_THRESHOLD": 0.80,
        # --- Innate word mapping ---
        "INNATE_WORD_TO_KEY": {
            "fort": "HP",
            "rapide": "SPD",
            "mortel": "CR",
            "cruel": "CD",
            "resistant": "RES",
            "résistant": "RES",
            "precision": "ACC",
            "précision": "ACC",
        },
        # --- OCR anti-bruit (borne large) ---
        "MAX_ABS": {
            "SPD": 60,
            "CR": 80,
            "CD": 80,
            "ACC": 80,
            "RES": 80,
            "ATK%": 80,
            "HP%": 80,
            "DEF%": 80,
            "ATK": 300,
            "DEF": 300,
            "HP": 6000,
        },
    }
}

IO_PRESETS: dict[str, dict[str, Any]] = {
    "default": {
        # Si None => pas de sauvegarde de bundle (images + meta.json)
        "BUNDLE_BASE_DIR": {
            "KEEP": "runes/data/keep/img",
            "SELL": "runes/data/sell/img",
            "TEST": "runes/data/test/img",
        },
        # Si None => pas de log
        "LOG_FILE": {
            "KEEP": "runes/data/keep/keep_log.txt",
            "SELL": "runes/data/sell/sell_log.txt",
            "TEST": "runes/data/test/test_log.txt",
        },
    }
}


def get_ruleset(name: str = "default") -> dict[str, Any]:
    return RUNE_RULESETS.get(name, RUNE_RULESETS["default"])


def get_ocr_preset(name: str = "default") -> dict[str, Any]:
    return OCR_PRESETS.get(name, OCR_PRESETS["default"])


def get_io_preset(name: str = "default") -> dict[str, Any]:
    return IO_PRESETS.get(name, IO_PRESETS["default"])


# =========================================================
# TYPES / DATA STRUCTURES
# =========================================================

Rarity = Literal["legend", "hero", "unknown"]
Decision = Literal["KEEP", "SELL", "TEST"]


@dataclass(frozen=True)
class StatLine:
    key: str
    value: int
    is_percent: bool
    last_roll: int = 0
    raw: str = ""


@dataclass(frozen=True)
class RuneData:
    level: int
    slot: Optional[int]
    rarity: Rarity
    set_name: str
    main: Optional[StatLine]
    innate: Optional[StatLine]
    subs: List[StatLine]


# =========================================================
# FILESYSTEM / SERIALIZATION
# =========================================================


def json_safe(obj):
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_safe(v) for v in obj]
    if isinstance(obj, tuple):
        return [json_safe(v) for v in obj]
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    return obj


def rune_fingerprint(rune: RuneData) -> str:
    payload = {
        "set": rune.set_name,
        "slot": rune.slot,
        "level": rune.level,
        "rarity": rune.rarity,
        "main": None
        if not rune.main
        else (rune.main.key, rune.main.value, rune.main.is_percent),
        "innate": None
        if not rune.innate
        else (rune.innate.key, rune.innate.value, rune.innate.is_percent),
        "subs": [(s.key, s.value, s.is_percent) for s in rune.subs],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]


def stat_to_dict(s: Optional[StatLine]) -> Optional[dict]:
    if s is None:
        return None
    return {
        "key": s.key,
        "value": s.value,
        "is_percent": s.is_percent,
        "last_roll": s.last_roll,
        "raw": s.raw,
    }


def rune_to_dict(rune: RuneData) -> dict:
    return {
        "level": rune.level,
        "slot": rune.slot,
        "rarity": rune.rarity,
        "set_name": rune.set_name,
        "main": stat_to_dict(rune.main),
        "innate": stat_to_dict(rune.innate),
        "subs": [stat_to_dict(s) for s in rune.subs],
    }


def save_rune_bundle(
    *,
    base_dir: Optional[str],
    rune: RuneData,
    decision: str,
    reasons: list[str],
    eff_current: float,
    eff_proj: float,
    target_level: int,
    imgs: dict[str, np.ndarray],
) -> Optional[str]:
    """
    Si base_dir est None => désactivé (aucune écriture disque).
    """
    if base_dir is None:
        return None

    base = Path(base_dir)
    fp = rune_fingerprint(rune)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = base / f"{ts}_{fp}"
    folder.mkdir(parents=True, exist_ok=True)

    for name, img in imgs.items():
        cv2.imwrite(str(folder / f"{name}.png"), img)

    meta = {
        "timestamp": ts,
        "decision": decision,
        "reasons": reasons,
        "set": {
            "raw": rune.set_name,
            "normalized": normalize_set_name(rune.set_name),
            "category": set_category_v2(rune.set_name),
        },
        "efficiency": {
            "current": round(eff_current, 3),
            "projected": round(eff_proj, 3),
            "projected_target_level": target_level,
        },
        "rune": rune_to_dict(rune),
    }

    with open(folder / "meta.json", "w", encoding="utf-8") as f:
        json.dump(json_safe(meta), f, ensure_ascii=False, indent=2)

    return str(folder)


# =========================================================
# SCREEN CAPTURE
# =========================================================


def grab_region(region: Tuple[int, int, int, int]) -> np.ndarray:
    left, top, width, height = region
    with mss.mss() as sct:
        frame = np.array(
            sct.grab({"left": left, "top": top, "width": width, "height": height})
        )
    return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)


# =========================================================
# OCR
# =========================================================


def _preprocess(img_bgr: np.ndarray) -> np.ndarray:
    img = cv2.resize(img_bgr, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thr


def ocr_lines(img_bgr: np.ndarray, psm: int = 6, whitelist: str = "") -> List[str]:
    thr = _preprocess(img_bgr)
    cfg = f"--oem 3 --psm {psm}"
    if whitelist:
        cfg += f" -c tessedit_char_whitelist={whitelist}"
    text = pytesseract.image_to_string(thr, lang="fra+eng", config=cfg)

    out: List[str] = []
    seen = set()
    for raw in text.splitlines():
        line = " ".join(raw.strip().split())
        if not line:
            continue
        k = line.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(line)
    return out


# =========================================================
# NORMALISATION / SETS
# =========================================================


def _strip_accents(s: str) -> str:
    import unicodedata

    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def normalize_set_name(set_name: str) -> str:
    if not set_name:
        return "Unknown"

    s = set_name.strip().replace("’", "'")
    s = _strip_accents(s)
    s = re.sub(r"[^A-Za-z]", "", s)
    if not s:
        return "Unknown"
    s = s[0].upper() + s[1:].lower()

    fixes = {
        "Deesespoir": "Desespoir",
        "Desepoir": "Desespoir",
        "Desespojr": "Desespoir",
        "Nemesjs": "Nemesis",
        "Nemeesis": "Nemesis",
        "Neemesis": "Nemesis",
        "Ameelioration": "Amelioration",
        "Volontee": "Volonte",
        "Vlolent": "Violent",
        "Violente": "Violent",
        "Vlolente": "Violent",
        "Intanglble": "Intangible",
        "Rapide": "Rapide",
    }
    return fixes.get(s, s)


def set_category_v2(set_name: str, ruleset_name: str = "default") -> str:
    r = get_ruleset(ruleset_name)
    s = normalize_set_name(set_name)

    if s in r["SETS_NEVER_USED"]:
        return "never_used"
    if s in r["SETS_LITTLE_USED"]:
        return "little_used"
    if s in r.get("SETS_NEMESIS", set()):
        return "nemesis"
    if s in r.get("SETS_OFFENSIVE_LITTLE_USED", set()):
        return "offensive_little_used"
    if s in r.get("SETS_OFFENSIVE_USED", set()):
        return "offensive_used"
    if s in r["SETS_FAST"]:
        return "fast"
    if s in r["SETS_USED"]:
        return "used"
    if s in r["SETS_VERY_USED"]:
        return "very_used"
    return "other"


def big_proc_thresholds_for_v2(
    cat: str, ruleset_name: str = "default"
) -> Dict[str, int]:
    r = get_ruleset(ruleset_name)
    return r["BIG_PROC"].get(cat, r["BIG_PROC"]["other"])


# =========================================================
# STAT PARSING HELPERS (FIX SPD BUG HERE)
# =========================================================


def norm(s: str) -> str:
    s = s.lower().replace("’", "'")
    s = re.sub(r"[.,:;(){}\[\]<>]", " ", s)
    s = s.replace("~", " ").replace("^", " ").replace("*", " ").replace("|", " ")
    s = re.sub(r"\s+", " ", s).strip()

    # OCR variants fréquents
    s = re.sub(r"\b[8bst]tq\b", "atq", s)
    s = re.sub(r"\batore\b", "atq", s)
    s = re.sub(r"\bpy\b", "pv", s)
    s = s.replace("dats", "dgts").replace("dgtsx", "dgts")
    s = re.sub(r"r+recision", "precision", s)

    # tx critique: "t x" / "1x" / "ix" / "|x"
    s = re.sub(r"\bt\s*x\b", "tx", s)
    s = re.sub(r"\b([1il])\s*x\b", "tx", s)
    return s


def fix_triangle(n: int) -> int:
    # ex OCR "46" -> "6"
    ss = str(n)
    if ss.startswith("4") and len(ss) >= 2:
        return int(ss[1:])
    return n


def _ocr_digits_to_int(
    s: str, *, prefer: Literal["first", "last"] = "last"
) -> Optional[int]:
    """
    Extraction numérique robuste.
    prefer="last" : comportement historique (utile pour % classiques).
    prefer="first": utile pour SPD quand l'OCR colle des chiffres parasites en fin de ligne.
    """
    if not s:
        return None
    t = s
    t = t.replace("O", "0").replace("o", "0")
    t = t.replace("I", "1").replace("l", "1").replace("|", "1")
    t = t.replace("/", "")  # IMPORTANT: ne pas convertir "/" en 7

    # colle les chiffres séparés par des espaces: "1 7" -> "17"
    t = re.sub(r"(\d)\s+(\d)", r"\1\2", t)
    t = re.sub(r"(\d)\s+(\d)", r"\1\2", t)

    nums = re.findall(r"\d+", t)
    if not nums:
        return None
    return int(nums[0] if prefer == "first" else nums[-1])


def _fix_double_digit_glitch(key: str, value: int) -> int:
    # Fix OCR typique: 7 lu 77 (etc). On corrige seulement 44..99 doublés.
    if key in {"CR", "CD", "SPD", "ATK%", "HP%", "DEF%", "ACC", "RES"} and value in {
        44,
        55,
        66,
        77,
        88,
        99,
    }:
        return value // 11
    return value


def detect_key_from_label(line: str) -> Optional[str]:
    s = norm(line)

    # CD
    if "crit" in s and re.search(r"\b(dgts?|deg|d[ée]g)\b", s):
        return "CD"
    # CR
    if "crit" in s and re.search(r"\b(tx|taux)\b", s):
        return "CR"
    # SPD
    if re.search(r"\b(vit|vitesse)\b", s):
        return "SPD"
    # ATK / HP / DEF
    if re.search(r"\b(a\s*t\s*q|atq|at0|ato|atk)\b", s):
        return "ATK%"
    if re.search(r"\b(p\s*v|pv|hp)\b", s):
        return "HP%"
    if re.search(r"\bdef\b", s):
        return "DEF%"
    # ACC/RES
    if re.search(r"\b(pr[ée]cision|precision|prec)\b", s):
        return "ACC"
    if re.search(r"\b(r[ée]sistance|resistance|res)\b", s):
        return "RES"

    return None


def parse_one_stat(line: str, *, ocr_name: str = "default") -> Optional[StatLine]:
    o = get_ocr_preset(ocr_name)
    raw = line
    s = norm(line)

    key = detect_key_from_label(s)
    if not key:
        return None

    # last roll "(▲11)" etc.
    m_roll = re.search(r"\(\s*(?:[▲\^])?\s*([0-9IlO\s]+)\s*%?\s*\)", raw)
    last_roll = 0
    if m_roll:
        rr = _ocr_digits_to_int(m_roll.group(1), prefer="first")
        last_roll = fix_triangle(rr) if rr is not None else 0

    # 1) classique "+22%"
    m_val = re.search(r"[+\uFF0B]\s*([0-9IlO\s]+)\s*(%|y)?", raw)

    # 2) fallback si OCR a perdu le "+"
    if not m_val:
        if key == "CR":
            m_val = re.search(
                r"\b(?:tx|taux)\b.*?\bcrit\w*\b[^0-9]*([0-9IlO\s]+)\s*%?",
                s,
                flags=re.IGNORECASE,
            )
        elif key == "CD":
            m_val = re.search(
                r"\b(?:dgts?|deg|d[ée]g)\b.*?\bcrit\w*\b[^0-9]*([0-9IlO\s]+)\s*%?",
                s,
                flags=re.IGNORECASE,
            )
        elif key == "SPD":
            # IMPORTANT: on prend le nombre juste après VIT/VITESSE (premier nombre pertinent)
            # Exemple OCR pourri: "VIT #23 (411)8&" -> on veut 23
            m_val = re.search(
                r"\b(?:vit|vitesse)\b[^0-9]*([0-9IlO\s]{1,6})\b", s, flags=re.IGNORECASE
            )
        elif key in {"ACC", "RES"}:
            m_val = re.search(
                r"\b(?:precision|pr[ée]cision|resistance|r[ée]sistance)\b[^0-9]*([0-9IlO\s]+)\s*%?",
                s,
                flags=re.IGNORECASE,
            )

    if not m_val:
        # dernier recours
        m_val = re.search(
            r"\b(?:ATQ|PV|DEF|VIT|RES|ACC|TX)\b\s*([0-9IlO\s]+)\s*(%|y)?",
            raw,
            flags=re.IGNORECASE,
        )
        if not m_val:
            return None

    # value + % hint
    if key == "SPD":
        value = _ocr_digits_to_int(m_val.group(1), prefer="first")
        if value is None:
            return None

        value = _fix_double_digit_glitch(key, value)

        # ---------- SPD OCR FIX ----------
        # Cas typiques:
        # - "VIT +117" alors que c'est "+11" (un chiffre parasite s'ajoute)
        # - "VIT +411" alors que c'est "+11" (le ▲ est lu comme 4 et collé)
        if value >= 100:
            sv = str(value)

            # ex: 411 -> 11 ; 417 -> 17
            if sv.startswith("4") and len(sv) >= 2:
                try:
                    tail = int(sv[1:])
                    if tail <= 60:
                        value = tail
                    else:
                        # sinon fallback ci-dessous
                        pass
                except Exception:
                    pass

            # ex: 117 -> 11 (on prend les 2 premiers digits si plausible)
            if value >= 100:
                v2 = int(sv[:2])  # 11 dans 117
                vlast2 = int(sv[-2:])  # 17 dans 117 (moins bon)
                if v2 <= 60:
                    value = v2
                elif vlast2 <= 60:
                    value = vlast2
                else:
                    # dernier filet de sécurité
                    value = int(sv[0])

        pct_hint = False
    else:
        value = _ocr_digits_to_int(m_val.group(1), prefer="last")
        if value is None:
            return None
        pct_hint = ("%" in raw) or ("%" in s)

        if pct_hint:
            value = fix_triangle(value)
            if value >= 100:
                value = value % 100
            value = _fix_double_digit_glitch(key, value)

    is_percent = bool(pct_hint)

    # si ATK%/HP%/DEF% mais pas % => flat
    if key in {"ATK%", "HP%", "DEF%"} and not is_percent:
        key = {"ATK%": "ATK", "HP%": "HP", "DEF%": "DEF"}[key]

    # anti-bruit
    maxv = o["MAX_ABS"].get(key, 999999)
    if value < 0 or value > maxv:
        return None

    return StatLine(
        key=key, value=value, is_percent=is_percent, last_roll=last_roll, raw=raw
    )


# =========================================================
# PARSING BLOCS
# =========================================================


def parse_upgrade_type_slot(
    lines: List[str],
) -> Tuple[int, Optional[int], str, Optional[str]]:
    joined = " | ".join(lines)
    s = norm(joined)

    level = 0
    m_lvl = re.search(r"\+?\s*(0|3|6|9|12)\b", s)
    if m_lvl:
        level = int(m_lvl.group(1))

    slot: Optional[int] = None
    m_slot = re.search(r"\(\s*([1-6Il])\s*\)", joined)
    if not m_slot:
        m_slot = re.search(r"\b([1-6])\s*\)", joined)
    if m_slot:
        ch = m_slot.group(1)
        if ch in ("I", "l"):
            ch = "1"
        v = int(ch)
        if v in (1, 2, 3, 4, 5, 6):
            slot = v

    set_name = "unknown"
    m_set = re.search(r"rune\s+([a-zà-ÿ]+)", s)
    if m_set:
        set_name = normalize_set_name(m_set.group(1))

    innate_word = None
    m_in = re.search(r"\+?\s*(0|3|6|9|12)\s+([a-zà-ÿ]+)\s+rune\b", s)
    if m_in:
        innate_word = m_in.group(2).lower()

    return level, slot, set_name, innate_word


def parse_grade(lines: List[str]) -> Rarity:
    s = norm(" | ".join(lines))
    if re.search(r"(l[ée])?gendaire|legendaire|[eé]gendaire|l.gendaire", s):
        return "legend"
    if "gend" in s:
        return "legend"
    if re.search(r"h[ée]ro[iï]que|heroique|heroi?que|h[ée]roi|h.roi", s):
        return "hero"
    if "hero" in s or "eroi" in s:
        return "hero"
    return "unknown"


def is_main_allowed(slot: Optional[int], st: StatLine) -> bool:
    if slot is None:
        return False
    if st.last_roll > 0:
        return False

    if slot == 1:
        return st.key == "ATK" and not st.is_percent
    if slot == 3:
        return st.key == "DEF" and not st.is_percent
    if slot == 5:
        return st.key == "HP" and not st.is_percent

    if slot == 2:
        return (st.key == "SPD" and not st.is_percent) or (
            st.key in {"ATK%", "HP%", "DEF%"} and st.is_percent
        )
    if slot == 4:
        return (st.key in {"CD", "CR"} and st.is_percent) or (
            st.key in {"ATK%", "HP%", "DEF%"} and st.is_percent
        )
    if slot == 6:
        return (st.key in {"ATK%", "HP%", "DEF%"} and st.is_percent) or (
            st.key in {"ACC", "RES"} and st.is_percent
        )

    return False


def pick_main_from_main_block(
    slot: Optional[int], candidates: List[StatLine]
) -> Optional[StatLine]:
    """
    IMPORTANT: dans SW, la main stat est affichée en premier dans le bloc.
    Donc si plusieurs stats sont "main allowed", on prend la première rencontrée (ordre OCR).
    """
    if slot is None:
        return None
    allowed = [s for s in candidates if is_main_allowed(slot, s)]
    if not allowed:
        return None
    return allowed[0]


def parse_main_and_innate(
    lines: List[str],
    slot: Optional[int],
    innate_word: Optional[str],
    *,
    ocr_name: str = "default",
) -> Tuple[Optional[StatLine], Optional[StatLine], List[StatLine]]:
    o = get_ocr_preset(ocr_name)
    innate_key = o["INNATE_WORD_TO_KEY"].get((innate_word or "").lower())

    stats: List[StatLine] = []
    for line in lines:
        st = parse_one_stat(line, ocr_name=ocr_name)
        if st:
            stats.append(st)

    innate = None
    leftovers = stats[:]

    if innate_key:
        innate = next(
            (s for s in stats if s.key == innate_key and s.last_roll == 0), None
        )
        if innate:
            leftovers = [s for s in leftovers if s is not innate]

    main = pick_main_from_main_block(slot, leftovers) or pick_main_from_main_block(
        slot, stats
    )
    if main:
        leftovers = [s for s in leftovers if s is not main]

    if innate is None and main is not None:
        candidates = [s for s in leftovers if s.last_roll == 0 and s.key != main.key]
        if candidates:
            innate = candidates[0]
            leftovers = [s for s in leftovers if s is not innate]

    return main, innate, leftovers


def parse_subs(lines: List[str], *, ocr_name: str = "default") -> List[StatLine]:
    subs: List[StatLine] = []
    seen = set()
    for line in lines:
        st = parse_one_stat(line, ocr_name=ocr_name)
        if not st:
            continue
        sig = (st.key, st.value, st.is_percent, st.last_roll)
        if sig in seen:
            continue
        seen.add(sig)
        subs.append(st)
    return subs


# =========================================================
# ANCIENT DETECTION
# =========================================================


# =========================================================
# FULL PARSE
# =========================================================


def parse_rune_from_regions(
    img_upgrade_type_slot: np.ndarray,
    img_grade: np.ndarray,
    img_main_innate: np.ndarray,
    img_subs: np.ndarray,
    *,
    ocr_name: str = "default",
) -> RuneData:
    o = get_ocr_preset(ocr_name)

    lines_u = ocr_lines(img_upgrade_type_slot, psm=6)
    lines_g = ocr_lines(img_grade, psm=7)
    lines_m = ocr_lines(img_main_innate, psm=6)
    lines_s = ocr_lines(img_subs, psm=6)

    level, slot, set_name, innate_word = parse_upgrade_type_slot(lines_u)
    rarity = parse_grade(lines_g)

    main, innate, leftovers_main_block = parse_main_and_innate(
        lines_m, slot, innate_word, ocr_name=ocr_name
    )

    subs = parse_subs(lines_s, ocr_name=ocr_name)

    def sig(st: StatLine) -> tuple:
        return (st.key, st.value, st.is_percent, st.last_roll)

    # remove main from subs if duplicated
    if main is not None:
        subs = [s for s in subs if sig(s) != sig(main)]

    # push leftovers (but not duplicates)
    seen = {sig(s) for s in subs}
    for st in leftovers_main_block:
        if main is not None and sig(st) == sig(main):
            continue
        if sig(st) in seen:
            continue
        subs.append(st)
        seen.add(sig(st))

    # keep max 4 subs (non-flat first, then explicit proc, then bigger value)
    def sub_score(s: StatLine) -> tuple:
        is_flat = s.key in {"ATK", "HP", "DEF"}
        return (1 if is_flat else 0, 0 if s.last_roll > 0 else 1, -s.value)

    subs.sort(key=sub_score)
    subs = subs[:4]

    return RuneData(
        level=level,
        slot=slot,
        rarity=rarity,
        set_name=set_name,
        main=main,
        innate=innate,
        subs=subs,
    )


# =========================================================
# EFF + HELPERS (unchanged logic)
# =========================================================


def eff_comm_group(
    subs: List[StatLine],
    keys: set[str],
    ignored_subs: set[str],
    max_roll_6s: dict[str, int],
) -> float:
    s = 0.0
    for st in subs[:4]:
        if st.key in ignored_subs:
            continue
        if st.key not in keys:
            continue
        m = max_roll_6s.get(st.key)
        if not m:
            continue
        s += st.value / (m * 5.0)
    return (1.0 + s) / 2.8


def count_good_in_group(
    subs: List[StatLine], keys: set[str], ignored_subs: set[str]
) -> int:
    c = 0
    for st in subs[:4]:
        if st.key in ignored_subs:
            continue
        if st.key in keys:
            c += 1
    return c


def eff_delta_of_sub(key: str, value: int, max_roll_6s: dict[str, int]) -> float:
    m = max_roll_6s.get(key)
    if not m:
        return 0.0
    s = value / (m * 5.0)
    return s / 2.8


def start_max_for_newsub(key: str, max_roll: dict) -> Optional[int]:
    return max_roll.get(key)


def choose_best_new_sub_for_group(
    existing_subs: List[StatLine],
    group_keys: set[str],
    *,
    ignored_subs: set[str],
    max_roll: dict[str, int],
) -> tuple[Optional[str], int, float]:
    present = {s.key for s in existing_subs[:4]}
    best_key = None
    best_val = 0
    best_delta = 0.0

    for k in group_keys:
        if k in ignored_subs:
            continue
        if k in present:
            continue  # pas de doublon
        mx = start_max_for_newsub(k, max_roll)
        if mx is None:
            continue
        d = eff_delta_of_sub(k, mx, max_roll)
        if d > best_delta:
            best_delta = d
            best_key = k
            best_val = mx

    return best_key, best_val, best_delta


def clamp_bucket_for_hero_at9(n: int) -> int:
    return 2 if n <= 2 else 3


def clamp_bucket_2_3_4(n: int) -> int:
    if n <= 2:
        return 2
    if n == 3:
        return 3
    return 4


def rolls_left_until_9_for_hero(level: int) -> int:
    return {0: 3, 3: 2, 6: 1, 9: 0, 12: 0}.get(level, 0)


def rolls_until_target(level: int, rarity: Rarity) -> Tuple[int, int]:
    """
    Retourne (rolls_to_target, target_level)
    hero: target +9
    legend: target +12
    """
    try:
        level = int(level)
    except Exception:
        return 0, 9 if rarity == "hero" else 12

    if rarity == "hero":
        return {0: 3, 3: 2, 6: 1, 9: 0, 12: 0}.get(level, 0), 9
    if rarity == "legend":
        return {0: 4, 3: 3, 6: 2, 9: 1, 12: 0}.get(level, 0), 12
    return 0, 12


# =========================================================
# BIG PROC
# =========================================================


def big_proc_confirmed(rune: RuneData, thresholds: Dict[str, int]) -> Tuple[bool, str]:
    cur = {s.key: s.value for s in rune.subs[:4]}
    for k, thresh in thresholds.items():
        if k in cur and cur[k] >= thresh:
            return True, f"{k} BIG_PROC confirmed: {cur[k]} (>= {thresh})"
    return False, ""


def rolls_left_for_existing_subs(rune: RuneData) -> int:
    # HERO : rolls à +3/+6/+9 seulement (après +9 => 0)
    if rune.rarity == "hero":
        return {0: 3, 3: 2, 6: 1, 9: 0, 12: 0}.get(rune.level, 0)
    # LEGEND
    return {0: 4, 3: 3, 6: 2, 9: 1, 12: 0}.get(rune.level, 0)


def big_proc_potential(
    rune: RuneData,
    thresholds: Dict[str, int],
    max_roll: dict[str, int],
) -> Tuple[bool, str]:
    rolls_left = rolls_left_for_existing_subs(rune)
    if rolls_left <= 0:
        return False, ""

    cur = {s.key: s.value for s in rune.subs[:4]}
    for k, thresh in thresholds.items():
        if k not in cur or k not in max_roll:
            continue
        max_final = cur[k] + rolls_left * max_roll[k]
        if max_final >= thresh:
            return True, f"{k} BIG_PROC possible: {cur[k]} -> {max_final} (>= {thresh})"
    return False, ""


# =========================================================
# DECIDE (your algorithm unchanged)
# =========================================================


def _is_main_important(rune: RuneData, main_important_cfg: dict) -> bool:
    if rune.main is None or rune.slot is None:
        return False
    slots = main_important_cfg.get(rune.main.key)
    if slots is None:
        return rune.main.key in main_important_cfg
    return rune.slot in slots


def _get_rune_type(rune: RuneData, main_important_cfg: dict) -> str:
    if rune.slot in (1, 3, 5):
        return "slot_135"
    if _is_main_important(rune, main_important_cfg):
        return rune.main.key if rune.main else "main_important"
    return "main_not_important"


def _resolve_conditions(cat: str, rune_type: str, r: dict) -> dict:
    """
    Retourne {"eff_support": {2:x,3:x,4:x}, "eff_dps": {2:x,3:x,4:x}, "big_proc": {...}}

    Si KEEP_CRITERIA est défini dans le ruleset:
      - valeurs par défaut au niveau catégorie
      - overrides optionnels par rune_type (seules les clés spécifiées écrasent)
    Sinon: fallback sur EFF_THRESHOLDS + BIG_PROC.
    """
    if "KEEP_CRITERIA" in r:
        cat_cond = r["KEEP_CRITERIA"].get(cat, r["KEEP_CRITERIA"].get("other", {}))
        default_support = cat_cond.get("eff_support", {})
        default_dps = cat_cond.get("eff_dps", {})
        default_big_proc = dict(cat_cond.get("big_proc", {}))
        type_cond = cat_cond.get(rune_type, {})
        return {
            "eff_support": type_cond.get("eff_support", default_support),
            "eff_dps": type_cond.get("eff_dps", default_dps),
            "big_proc": {**default_big_proc, **type_cond.get("big_proc", {})},
        }

    # Fallback legacy
    cat_thresh = r.get("EFF_THRESHOLDS", {}).get(cat, r.get("EFF_THRESHOLDS", {}).get("other", {}))
    type_thresh = cat_thresh.get(rune_type, cat_thresh.get("slot_135", {}))
    big_proc = dict(r.get("BIG_PROC", {}).get(cat, r.get("BIG_PROC", {}).get("other", {})))
    return {
        "eff_support": type_thresh.get("support", {}),
        "eff_dps": type_thresh.get("dps", {}),
        "big_proc": big_proc,
    }


def _pick_threshold_dict(
    rune: RuneData,
    cat: str,
    best_profile: str,
    eff_thresholds: dict,
    main_important_cfg: dict,
) -> Tuple[dict, str]:
    """Retourne (bucket_dict {2:x,3:x,4:x}, label) selon slot, profil et main.

    Priorité pour les slots 2/4/6 quand la main est "importante":
      1. Clé spécifique par main stat (ex "ATK%", "HP%") si présente dans cat_t
      2. "main_important" générique
    Sinon: "main_not_important".
    label = "{cat}>{sub_key}>{profile}" pour traçabilité dans les logs.
    """
    cat_t = eff_thresholds.get(cat, eff_thresholds["other"])
    if rune.slot in (1, 3, 5):
        group_t = cat_t.get("slot_135", {})
        sub_key = "slot_135"
    elif _is_main_important(rune, main_important_cfg):
        if rune.main and rune.main.key in cat_t:
            sub_key = rune.main.key
            group_t = cat_t[sub_key]
        else:
            group_t = cat_t.get("main_important", {})
            sub_key = "main_important"
    else:
        group_t = cat_t.get("main_not_important", {})
        sub_key = "main_not_important"
    label = f"{cat}>{sub_key}>{best_profile}"
    return group_t.get(best_profile, group_t.get("support", {})), label


def decide(
    rune: RuneData, *, ruleset_name: str = "default"
) -> Tuple[Decision, List[str]]:
    r = get_ruleset(ruleset_name)

    EFF_GROUP_SUPPORT = r["EFF_GROUP_SUPPORT"]
    EFF_GROUP_DPS = r["EFF_GROUP_DPS"]
    IGNORED_SUBS = r["IGNORED_SUBS"]
    MAIN_IMPORTANT = r["MAIN_IMPORTANT"]
    MAX_ROLL = r["MAX_ROLL"]
    PROC_EQ = r["PROC_EQ"]

    # rareté unknown => SELL
    if rune.rarity == "unknown":
        return "SELL", ["SELL: rarity unknown"]

    cat = set_category_v2(rune.set_name, ruleset_name=ruleset_name)
    rune_type = _get_rune_type(rune, MAIN_IMPORTANT)
    cond = _resolve_conditions(cat, rune_type, r)
    thresholds = cond["big_proc"]

    def is_new_sub(st: StatLine) -> bool:
        return "new" in (st.raw or "").lower()

    # ============================
    # HERO
    # ============================
    if rune.rarity == "hero":
        # Rune héroïque déjà +12 => plus aucun potentiel
        if rune.level >= 12:
            confirmed, conf_msg = big_proc_confirmed(rune, thresholds)

            eff_support = eff_comm_group(
                rune.subs, EFF_GROUP_SUPPORT, IGNORED_SUBS, MAX_ROLL
            )
            eff_dps = eff_comm_group(rune.subs, EFF_GROUP_DPS, IGNORED_SUBS, MAX_ROLL)

            if eff_dps >= eff_support:
                best_profile = "dps"
                best_group = EFF_GROUP_DPS
                eff_best = eff_dps
            else:
                best_profile = "support"
                best_group = EFF_GROUP_SUPPORT
                eff_best = eff_support

            good = count_good_in_group(rune.subs, best_group, IGNORED_SUBS)
            bucket = clamp_bucket_2_3_4(good)

            eff_thresh = cond["eff_dps"] if best_profile == "dps" else cond["eff_support"]
            eff_label = f"{cat}>{rune_type}>{best_profile}"
            req = eff_thresh[bucket]

            ctx = [
                "hero +12 final evaluation",
                f"set_cat={cat}",
                f"profile={best_profile} (dps={eff_dps:.3f}, support={eff_support:.3f})",
                f"good_in_profile={good} good_group_subs={bucket}",
                f"eff_cond={eff_label} good_group_subs={bucket} req={req:.3f}",
                f"eff={eff_best:.3f} vs req={req:.3f}",
            ]

            if confirmed:
                return "KEEP", [f"KEEP: {conf_msg}"] + ctx

            if eff_best >= req:
                return "KEEP", ["KEEP: hero +12 eff ok"] + ctx

            return "SELL", ["SELL: hero +12 no big proc and no eff threshold"] + ctx

        eval_subs = [s for s in rune.subs if not is_new_sub(s)]
        eval_level = min(rune.level, 9)

        eval_rune = RuneData(
            level=eval_level,
            slot=rune.slot,
            rarity=rune.rarity,
            set_name=rune.set_name,
            main=rune.main,
            innate=rune.innate,
            subs=eval_subs,
        )

        confirmed, conf_msg = big_proc_confirmed(eval_rune, thresholds)

        # big proc potential jusqu'à +9 seulement
        rolls_left_existing = rolls_left_until_9_for_hero(eval_level)
        pot_msg = ""
        if rolls_left_existing > 0:
            cur = {s.key: s.value for s in eval_subs[:4]}
            for k, thresh in thresholds.items():
                if k not in cur or k not in MAX_ROLL:
                    continue
                max_final = cur[k] + rolls_left_existing * MAX_ROLL[k]
                if max_final >= thresh:
                    pot_msg = f"{k} BIG_PROC possible (to +9): {cur[k]} -> {max_final} (>= {thresh})"
                    break

        eff_support_now = eff_comm_group(
            eval_subs, EFF_GROUP_SUPPORT, IGNORED_SUBS, MAX_ROLL
        )
        eff_dps_now = eff_comm_group(eval_subs, EFF_GROUP_DPS, IGNORED_SUBS, MAX_ROLL)

        if eff_dps_now >= eff_support_now:
            best_profile = "dps"
            best_group = EFF_GROUP_DPS
            eff_best_now = eff_dps_now
        else:
            best_profile = "support"
            best_group = EFF_GROUP_SUPPORT
            eff_best_now = eff_support_now

        rolls_to_9 = rolls_left_until_9_for_hero(eval_level)
        eff_best_at9 = eff_best_now + rolls_to_9 * PROC_EQ

        good_in_best_now = count_good_in_group(eval_subs, best_group, IGNORED_SUBS)
        bucket9 = clamp_bucket_for_hero_at9(good_in_best_now)

        eff_thresh9 = cond["eff_dps"] if best_profile == "dps" else cond["eff_support"]
        eff_label9 = f"{cat}>{rune_type}>{best_profile}"
        req9 = eff_thresh9[bucket9]

        pass9 = eff_best_at9 >= req9
        at9 = eval_level >= 9

        ctx9 = [
            f"set_cat={cat}",
            f"profile@+9={best_profile} (dps={eff_dps_now:.3f}, support={eff_support_now:.3f})",
            f"eff_cond={eff_label9} good_group_subs={bucket9} req={req9:.3f}",
            f"good_in_profile@now={good_in_best_now} -> good_group_subs={bucket9}",
            f"proj_to+9: eff_best_now={eff_best_now:.3f} + {rolls_to_9}*{PROC_EQ:.3f} => eff_best_at9={eff_best_at9:.3f}",
            f"req9={req9:.3f}",
        ]

        if confirmed:
            if at9:
                return "KEEP", [f"KEEP: {conf_msg}"] + ctx9
            return "TEST", [f"TEST: {conf_msg}"] + ctx9

        # Si BIG PROC possible d'ici +9, on TEST (même si la gate eff ne passe pas)
        if (not at9) and pot_msg:
            return "TEST", [f"TEST: {pot_msg}"] + ctx9

        if pass9:
            if at9:
                return "KEEP", ["KEEP: PASS @+9 (hero gate)"] + ctx9
            base = ["TEST: try reach +9 (hero gate)"] + ctx9
            if pot_msg:
                base.insert(1, f"note: {pot_msg}")
            return "TEST", base

        # FAIL @+9 => best-case NEW @+12
        k1, v1, d1 = choose_best_new_sub_for_group(
            eval_subs,
            EFF_GROUP_DPS,
            ignored_subs=IGNORED_SUBS,
            max_roll=MAX_ROLL,
        )
        k2, v2, d2 = choose_best_new_sub_for_group(
            eval_subs,
            EFF_GROUP_SUPPORT,
            ignored_subs=IGNORED_SUBS,
            max_roll=MAX_ROLL,
        )

        eff_dps_at9 = eff_dps_now + rolls_to_9 * PROC_EQ
        eff_sup_at9 = eff_support_now + rolls_to_9 * PROC_EQ

        eff_dps_at12_best = eff_dps_at9 + d1
        eff_sup_at12_best = eff_sup_at9 + d2

        if eff_dps_at12_best >= eff_sup_at12_best:
            chosen = "dps"
            chosen_group = EFF_GROUP_DPS
            eff12 = eff_dps_at12_best
            new_key, new_val = k1, v1
        else:
            chosen = "support"
            chosen_group = EFF_GROUP_SUPPORT
            eff12 = eff_sup_at12_best
            new_key, new_val = k2, v2

        good_now = count_good_in_group(eval_subs, chosen_group, IGNORED_SUBS)
        good12 = good_now + (1 if new_key is not None else 0)
        bucket12 = clamp_bucket_2_3_4(good12)

        eff_thresh12 = cond["eff_dps"] if chosen == "dps" else cond["eff_support"]
        eff_label12 = f"{cat}>{rune_type}>{chosen}"
        req12 = eff_thresh12[bucket12]

        pass12 = eff12 >= req12

        ctx12 = ctx9 + [
            "FAIL@+9 => try best-case @+12 with NEW-sub",
            f"best_new_sub={new_key}+{new_val} (start-max) for profile={chosen}",
            f"eff_cond={eff_label12} good_group_subs={bucket12} req={req12:.3f}",
            f"eff_best@+12(bestcase)={eff12:.3f} vs req12={req12:.3f} | good12={good12} good_group_subs={bucket12}",
        ]

        if pass12:
            return "TEST", ["TEST: could PASS with perfect NEW-sub @+12"] + ctx12

        return "SELL", ["SELL: FAIL @+9 and even best-case NEW @+12 fails"] + ctx12

    # ============================
    # LEGEND
    # ============================
    confirmed, conf_msg = big_proc_confirmed(rune, thresholds)
    pot, pot_msg = big_proc_potential(rune, thresholds, MAX_ROLL)

    eff_support = eff_comm_group(rune.subs, EFF_GROUP_SUPPORT, IGNORED_SUBS, MAX_ROLL)
    eff_dps = eff_comm_group(rune.subs, EFF_GROUP_DPS, IGNORED_SUBS, MAX_ROLL)

    if eff_dps >= eff_support:
        best_profile = "dps"
        best_group = EFF_GROUP_DPS
        eff_best = eff_dps
    else:
        best_profile = "support"
        best_group = EFF_GROUP_SUPPORT
        eff_best = eff_support

    rolls_to_target, target_level = rolls_until_target(rune.level, rune.rarity)
    eff_proj = eff_best + rolls_to_target * PROC_EQ

    good_in_best = count_good_in_group(rune.subs, best_group, IGNORED_SUBS)
    bucket = clamp_bucket_2_3_4(good_in_best)

    eff_thresh = cond["eff_dps"] if best_profile == "dps" else cond["eff_support"]
    eff_label = f"{cat}>{rune_type}>{best_profile}"
    req = eff_thresh[bucket]

    pass_eff = eff_proj >= req
    at_target = rune.level >= target_level

    ctx = [
        f"set_cat={cat}",
        f"profile={best_profile} (dps={eff_dps:.3f}, support={eff_support:.3f})",
        f"eff_cond={eff_label} good_group_subs={bucket} req={req:.3f}",
        f"good_in_profile={good_in_best} good_group_subs={bucket}",
        f"proj+{target_level}: eff={eff_proj:.3f} (req={req:.3f}, rolls_left={rolls_to_target})",
    ]

    if confirmed:
        return ("KEEP" if at_target else "TEST"), [
            ("KEEP" if at_target else "TEST") + f": {conf_msg}"
        ] + ctx
    if (not at_target) and pot:
        return "TEST", [f"TEST: {pot_msg}"] + ctx
    if pass_eff:
        return ("KEEP" if at_target else "TEST"), [
            ("KEEP" if at_target else "TEST") + ": eff ok"
        ] + ctx
    return "SELL", ["SELL: eff insuffisante (no bigproc)"] + ctx


# =========================================================
# LOGGING
# =========================================================


def _fmt_stat_no_roll(s: Optional["StatLine"]) -> str:
    if s is None:
        return "None"
    return f"{s.key}: {s.value}"


def _parse_reasons(reasons: List[str]) -> dict:
    result = {
        "set_cat": None, "profile": None, "eff_dps": None, "eff_support": None,
        "req": None, "bucket": None, "rune_type": None,
        "reason_tag": None, "big_proc_stat": None,
    }
    for line in reasons:
        line = line.strip()
        m = re.match(r'(?:KEEP|SELL|TEST): (.+)', line)
        if m and result["reason_tag"] is None:
            text = m.group(1)
            bp = re.match(r'([\w%]+) BIG_PROC confirmed', text)
            bp_pos = re.match(r'([\w%]+) BIG_PROC possible', text)
            if bp:
                result["reason_tag"] = "big_proc"
                result["big_proc_stat"] = bp.group(1)
            elif bp_pos:
                result["reason_tag"] = "big_proc_possible"
                result["big_proc_stat"] = bp_pos.group(1)
            elif re.search(r'eff ok|PASS @\+\d+|hero \+12 eff', text):
                result["reason_tag"] = "eff"
            elif re.search(r'try reach \+9|hero gate|could PASS|PASS with', text):
                result["reason_tag"] = "test_eff"
            elif re.search(r'eff insuffisante|FAIL|no big proc', text):
                result["reason_tag"] = "eff_fail"
            elif "rarity unknown" in text:
                result["reason_tag"] = "unknown"
            else:
                result["reason_tag"] = text[:40]
            continue
        m = re.match(r'set_cat=(\S+)', line)
        if m:
            result["set_cat"] = m.group(1)
            continue
        m = re.match(r'profile(?:@\+\d+)?=(\w+) \(dps=([\d.]+), support=([\d.]+)\)', line)
        if m:
            result["profile"] = m.group(1)
            result["eff_dps"] = float(m.group(2))
            result["eff_support"] = float(m.group(3))
            continue
        m = re.match(r'eff_cond=\S+>(\S+)>\S+ good_group_subs=(\d+) req=([\d.]+)', line)
        if m:
            result["rune_type"] = m.group(1)
            result["bucket"] = int(m.group(2))
            result["req"] = float(m.group(3))
    return result


def log_rune_jsonl(
    filepath: Optional[str],
    rune: RuneData,
    decision: str,
    reasons: List[str],
    eff_current: float,
    eff_proj: float,
) -> None:
    if filepath is None:
        return
    jsonl_path = Path(filepath)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    parsed = _parse_reasons(reasons)
    req = parsed["req"]
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "decision": decision,
        "set": rune.set_name,
        "set_cat": parsed["set_cat"],
        "slot": rune.slot,
        "rarity": rune.rarity,
        "level": rune.level,
        "main": rune.main.key if rune.main else None,
        "profile": parsed["profile"],
        "eff_dps": parsed["eff_dps"],
        "eff_support": parsed["eff_support"],
        "eff_current": round(eff_current, 3),
        "eff_proj": round(eff_proj, 3),
        "req": req,
        "margin": round(eff_current - req, 3) if req is not None else None,
        "bucket": parsed["bucket"],
        "rune_type": parsed["rune_type"],
        "reason_tag": parsed["reason_tag"],
        "big_proc_stat": parsed["big_proc_stat"],
        "subs": [{"key": s.key, "value": s.value} for s in rune.subs],
    }
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(json_safe(record), ensure_ascii=False) + "\n")


def log_rune(
    filepath: Optional[str], rune: RuneData, decision: Decision, reasons: List[str]
) -> None:
    if filepath is None:
        return
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 70 + "\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Decision: {decision}\n")
        f.write(
            f"Set: {rune.set_name} | Slot: {rune.slot} | Rarity: {rune.rarity} | Level: +{rune.level}\n"
        )
        f.write(f"Main: {_fmt_stat_no_roll(rune.main)}\n")
        f.write(f"Innate: {_fmt_stat_no_roll(rune.innate)}\n")
        f.write("\nSubs:\n")
        for s in rune.subs:
            f.write(f"  {s.key}: {s.value} raw='{s.raw}'\n")
        f.write("\nReasons:\n")
        for r in reasons:
            f.write(f"  - {r}\n")


def _deep_merge(base: Any, override: Any) -> Any:
    """
    Merge récursif:
    - dict + dict => merge récursif
    - sinon => override remplace base
    Note: sets/tuples/list remplacent (pas de merge).
    """
    if isinstance(base, dict) and isinstance(override, dict):
        out = deepcopy(base)
        for k, v in override.items():
            if k in out:
                out[k] = _deep_merge(out[k], v)
            else:
                out[k] = deepcopy(v)
        return out
    return deepcopy(override)


def _resolve_preset(
    default_map: dict[str, dict[str, Any]], override: Optional[dict]
) -> dict[str, Any]:
    """
    Retourne le preset final:
    - si override None => default
    - sinon => deep merge(default, override)
    """
    base = default_map["default"]
    if override is None:
        return deepcopy(base)
    if not isinstance(override, dict):
        raise TypeError("override doit être un dict ou None")
    return _deep_merge(base, override)


# =========================================================
# MAIN ENTRY
# =========================================================


def debug_parse_rune(
    upgrade_rune_settings: Optional[dict] = None,
    ocr_name: str = "default",
) -> None:
    r = get_ruleset(
        upgrade_rune_settings.get("ruleset") if upgrade_rune_settings else None
    )
    o = get_ocr_preset(ocr_name)

    img_u = grab_region(o["REGION_UPGRADE_TYPE_SLOT"])
    img_g = grab_region(o["REGION_GRADE"])
    img_m = grab_region(o["REGION_MAIN_INNATE"])
    img_s = grab_region(o["REGION_SUBS"])

    rune = parse_rune_from_regions(img_u, img_g, img_m, img_s, ocr_name=ocr_name)

    print("=== debug_parse_rune ===")
    print(f"Slot: {rune.slot}  Rarity: {rune.rarity}  Level: {rune.level}")
    print(f"Main:   {_fmt_stat_no_roll(rune.main)}")
    print(f"Innate: {_fmt_stat_no_roll(rune.innate)}")
    print("Subs:")
    for s in rune.subs:
        print(f"  {s.key}: {s.value}  raw='{s.raw}'")
    if upgrade_rune_settings:
        eff_s = eff_comm_group(
            rune.subs, r["EFF_GROUP_SUPPORT"], r["IGNORED_SUBS"], r["MAX_ROLL"]
        )
        eff_d = eff_comm_group(
            rune.subs, r["EFF_GROUP_DPS"], r["IGNORED_SUBS"], r["MAX_ROLL"]
        )
        print(f"Eff support: {eff_s:.3f}  Eff dps: {eff_d:.3f}")
    print("=======================")


def check_rune_conditions(
    upgrade_rune_settings: Optional[dict] = None,
    save_rune_settings: Optional[dict] = None,
    ocr_presets: Optional[dict] = None,
) -> bool:
    """
    Wrapper runtime.

    - Param 1 (upgrade_rune_settings) écrase RUNE_RULESETS["default"]
    - Param 2 (save_rune_settings) écrase IO_PRESETS["default"]
    - Param 3 (ocr_presets) écrase OCR_PRESETS["default"] (tu le laisses par défaut)

    Appel attendu:
        keep = up_runes(data1["upgrade_rune_settings"], data1["save_rune_settings"])
    """
    # 1) resolve presets (merge avec default)
    runtime_rules = _resolve_preset(RUNE_RULESETS, upgrade_rune_settings)
    runtime_io = _resolve_preset(IO_PRESETS, save_rune_settings)
    runtime_ocr = _resolve_preset(OCR_PRESETS, ocr_presets)

    # 2) inject runtime presets (sans toucher le code existant)
    RUNE_RULESETS[_RUNTIME_KEY] = runtime_rules
    IO_PRESETS[_RUNTIME_KEY] = runtime_io
    OCR_PRESETS[_RUNTIME_KEY] = runtime_ocr

    # 3) run
    return _run_check_rune_conditions(
        ruleset_name=_RUNTIME_KEY,
        io_name=_RUNTIME_KEY,
        ocr_name=_RUNTIME_KEY,
    )


def _run_check_rune_conditions(
    *,
    ruleset_name: str = "default",
    ocr_name: str = "default",
    io_name: str = "default",
) -> bool:
    o = get_ocr_preset(ocr_name)
    io = get_io_preset(io_name)

    img_u = grab_region(o["REGION_UPGRADE_TYPE_SLOT"])
    img_g = grab_region(o["REGION_GRADE"])
    img_m = grab_region(o["REGION_MAIN_INNATE"])
    img_s = grab_region(o["REGION_SUBS"])

    rune = parse_rune_from_regions(img_u, img_g, img_m, img_s, ocr_name=ocr_name)

    decision, reasons = decide(rune, ruleset_name=ruleset_name)
    log_cfg = io.get("LOG_FILE")
    log_path = log_cfg.get(decision) if isinstance(log_cfg, dict) else log_cfg
    log_rune(log_path, rune, decision, reasons)

    # Pour la sauvegarde bundle, on met une "eff_current/proj" cohérente minimalement :
    # - current = best profile now (sans projection)
    # - projected = best profile + rolls to target (hero->+9, legend->+12)
    r = get_ruleset(ruleset_name)
    eff_s = eff_comm_group(
        rune.subs, r["EFF_GROUP_SUPPORT"], r["IGNORED_SUBS"], r["MAX_ROLL"]
    )
    eff_d = eff_comm_group(
        rune.subs, r["EFF_GROUP_DPS"], r["IGNORED_SUBS"], r["MAX_ROLL"]
    )
    eff_current = max(eff_s, eff_d)
    rolls_to_target, target_level = rolls_until_target(rune.level, rune.rarity)
    eff_proj = eff_current + rolls_to_target * r["PROC_EQ"]

    jsonl_cfg = io.get("JSONL_FILE")
    jsonl_path = jsonl_cfg.get(decision) if isinstance(jsonl_cfg, dict) else jsonl_cfg
    log_rune_jsonl(jsonl_path, rune, decision, reasons, eff_current, eff_proj)

    bundle_cfg = io.get("BUNDLE_BASE_DIR")
    if isinstance(bundle_cfg, dict):
        bundle_dir = bundle_cfg.get(decision)
    else:
        bundle_dir = f"{bundle_cfg}/{decision}" if bundle_cfg else None
    save_rune_bundle(
        base_dir=bundle_dir,
        rune=rune,
        decision=decision,
        reasons=reasons,
        eff_current=eff_current,
        eff_proj=eff_proj,
        target_level=target_level,
        imgs={
            "upgrade_type_slot": img_u,
            "grade": img_g,
            "main_innate": img_m,
            "subs": img_s,
        },
    )

    return decision != "SELL"


"""
LOGIC derriere le trie des runes:

- on calcule 2 types d'efficience et on prend le meilleur -> 2 groupes: (VIT, PV%, DEF%, ATK%) et (VIT, ATK%, CD, CR)
- pour les good subs on prend en compte combien de subs font partie d'un groupe.
    Par exemple si j'ai les subs PV%, DEF%, CD et CD, j'ai 2 fois 2 good subs et non pas 4 car ces 4 subs ne font pas partie du meme groupe.
    Les 2 premiers good subs sont PV% et DEF% car ces 2 subs font partie du groupe (VIT, PV%, DEF%, ATK%).
    Les 2 suivants good subs sont CD% et CR car ces 2 subs font partie du groupe (VIT, ATK%, CD, CR).
- pour les seuils d'efficience et pour les runes heroiques, on regarde si les condition 2 ou 3 good subs a +9. Si le seuil d'efficience n'est pas
    atteint on tente le +12 pour voir si la nouvelle sub peut sauver subs a +9. Si les conditions sont remplies a +9 on garde dans tous les cas

tous les types de sets:
    - sets jamais utilisés: guardien, focus, endurance, determination, amelioration, precision, tolération, protection:
        - BIG_PROC_NEVER_USED = { "SPD": 23, "CR": 23, "CD": 27, "ATK%": 31, "HP%": 31, "DEF%": 31, "ACC": 31, "RES": 31 }
        - efficiency minimum en fonction du nombre de bonnes subs(non flat) pour tous les slots 1, 3 et 5:
            Pour les runes a +12:
                - 2 good subs = 0.714 ((1 + ((16 / (8 * 5)) + (24 / (8 * 5)) + (0 / (8 * 5)) + (0 / (6 * 5)))) / 2.8)
                - 3 good subs = 0.785 ((1 + ((16 / (8 * 5)) + (16 / (8 * 5)) + (0 / (8 * 5)) + (12 / (6 * 5)))) / 2.8)
                - 4 good subs = 0.857 ((1 + ((16 / (8 * 5)) + (16 / (8 * 5)) + (8 / (8 * 5)) + (12 / (6 * 5)))) / 2.8)

    - set très peu utilisés: energy, vengeance, sceau, nemesis, destruction, vampire, fatale, combat:
        - BIG_PROC_LITTLE_USED = { "SPD": 22, "CR": 22, "CD": 26, "ATK%": 30, "HP%": 30, "DEF%": 30, "ACC": 30, "RES": 30 }
        - efficiency minimum en fonction du nombre de bonnes subs(non flat) pour tous les slots 1, 3 et 5(il a un proc max entre les lignes):
            Pour les runes a +12:
                - 2 good subs = 0.687
                - 3 good subs = 0.758
                - 4 good subs = 0.830
    
    - sets rapides: swift:
        - BIG_PROC_FAST = { "SPD": 23, "CR": 21, "CD": 24, "ATK%": 30, "HP%": 30, "DEF%": 30, "ACC": 30, "RES": 30 }
        - efficiency minimum en fonction du nombre de bonnes subs(non flat) pour tous les slots 1, 3 et 5(il a un proc max entre les lignes):
            Pour les runes a +12:
                - 2 good subs = 0.687
                - 3 good subs = 0.758
                - 4 good subs = 0.830

    - sets utilisés: desespoir, rage, lame:
        - BIG_PROC_USED = { "SPD": 21, "CR": 21, "CD": 24, "ATK%": 28, "HP%": 28, "DEF%": 28, "ACC": 30, "RES": 30 }
        - efficiency minimum en fonction du nombre de bonnes subs(non flat) pour tous les slots 1, 3 et 5(il a un proc max entre les lignes):
            Pour les runes a +12:
                - 2 good subs = 0.675
                - 3 good subs = 0.747
                - 4 good subs = 0.818

    - sets très utilisés: violent, volonte, intangible:
        - BIG_PROC_VERY_USED = { "SPD": 20, "CR": 20, "CD": 24, "ATK%": 26, "HP%": 26, "DEF%": 26, "ACC": 30, "RES": 30 }
        - efficiency minimum en fonction du nombre de bonnes subs(non flat) pour tous les slots 1, 3 et 5(il a un proc max entre les lignes):
            Pour les runes a +12:
                - 2 good subs a +12 = 0.661
                - 3 good subs a +12 = 0.732
                - 4 good subs a +12 = 0.803

    - L'efficiency pour les main stat ATK%(slot 2 et 6), PV%(slot 4 et 6), CD et SPD: pareil que juste avant mais on enleve 0.0147
    - le reste des main stats on prendre la meme condition que les slots 1, 3 et 5
    - On verifie l'efficience max pour les runes heroiques a +9 et les runes legendaires a +12
    - on ne prend pas en compte l'ACC et la RES pour le calcule de l'efficience

"""
