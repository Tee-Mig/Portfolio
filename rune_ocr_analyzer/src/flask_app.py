import importlib
import re
import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from src.eff_equiv import calc as _eff_calc

# ─── constants ────────────────────────────────────────────────────────────────

EFF_TEMPLATES = {
    'eff_dps':     [('SPD', 6), ('ATK%', 8), ('CR%', 6), ('CD%', 7)],
    'eff_support': [('SPD', 6), ('ATK%', 8), ('HP%', 8), ('DEF%', 8)],
}
EFF_DIVISOR = 2.8

CATEGORIES = [
    "never_used", "little_used", "nemesis", "offensive_little_used",
    "offensive_used", "fast", "used", "very_used", "other",
]
RUNE_TYPES = ["slot_135", "main_not_important", "ATK%", "HP%", "DEF%", "CD", "SPD"]
RUNE_TYPE_LABELS = {
    "slot_135":           "slot 1, 3 et 5",
    "main_not_important": "main stat not important",
    "ATK%":               "important main stat ATK%",
    "HP%":                "important main stat HP%",
    "DEF%":               "important main stat DEF%",
    "CD":                 "important main stat CD",
    "SPD":                "important main stat SPD",
}
BIG_PROC_STATS = ["SPD", "CR", "CD", "ATK%", "HP%", "DEF%", "ACC", "RES"]
BUCKETS = [2, 3, 4]
CRITERIA_KEY = "KEEP_CRITERIA"
CATEGORY_SET_KEY = {
    "never_used":            "SETS_NEVER_USED",
    "little_used":           "SETS_LITTLE_USED",
    "nemesis":               "SETS_NEMESIS",
    "offensive_little_used": "SETS_OFFENSIVE_LITTLE_USED",
    "offensive_used":        "SETS_OFFENSIVE_USED",
    "fast":                  "SETS_FAST",
    "used":                  "SETS_USED",
    "very_used":             "SETS_VERY_USED",
}
ALL_SETS = sorted([
    "Amelioration", "Combat", "Desespoir", "Destruction", "Determination",
    "Endurance", "Energie", "Fatale", "Focus", "Gardien",
    "Intangible", "Lame", "Nemesis", "Precision", "Protection",
    "Rage", "Rapide", "Sceau", "Toleration", "Vampire",
    "Vengeance", "Violent", "Volonte",
])

DATAS_PATH = Path(__file__).parent / "datas.py"

app = Flask(__name__, template_folder="../templates")
app.config['TEMPLATES_AUTO_RELOAD'] = True


# ─── data helpers ─────────────────────────────────────────────────────────────

def _load_criteria() -> dict:
    import src.datas as m
    importlib.reload(m)
    sets_by_data = {}
    for ds_name, ds in [("data1", m.data1), ("data2", m.data2)]:
        s = {}
        for cat, key in CATEGORY_SET_KEY.items():
            s[cat] = sorted(ds["upgrade_rune_settings"].get(key, set()))
        sets_by_data[ds_name] = s
    return {
        "data1": m.data1["upgrade_rune_settings"][CRITERIA_KEY],
        "data2": m.data2["upgrade_rune_settings"][CRITERIA_KEY],
        "sets": sets_by_data,
    }


def _normalise(raw: dict) -> dict:
    result = {}
    for cat, cat_data in raw.items():
        c = {}
        for key, val in cat_data.items():
            if key in ("eff_support", "eff_dps"):
                c[key] = {int(k): round(float(v), 3) for k, v in val.items()}
            elif key == "big_proc":
                c[key] = {k: int(v) for k, v in val.items() if v != ""}
            elif key in RUNE_TYPES:
                ov = {}
                for ek, ev in val.items():
                    if ek in ("eff_support", "eff_dps"):
                        ov[ek] = {int(k): round(float(v), 3) for k, v in ev.items()}
                    elif ek == "big_proc":
                        ov[ek] = {k: int(v) for k, v in ev.items()}
                c[key] = ov
        result[cat] = c
    return result


# ─── file saving ──────────────────────────────────────────────────────────────

def _fmt_eff(d: dict) -> str:
    parts = ", ".join(f"{k}: {v:.3f}" for k, v in sorted(d.items()))
    return "{" + parts + "}"


def _generate_block(criteria: dict, indent="        ") -> str:
    i2 = indent + "    "
    i3 = indent + "        "
    i4 = indent + "            "
    lines = [f'{indent}"{CRITERIA_KEY}": {{']
    for cat in CATEGORIES:
        d = criteria.get(cat, {})
        lines.append(f'{i2}"{cat}": {{')
        lines.append(f'{i3}"eff_support": {_fmt_eff(d.get("eff_support", {}))},')
        lines.append(f'{i3}"eff_dps": {_fmt_eff(d.get("eff_dps", {}))},')
        bp = d.get("big_proc", {})
        lines.append(f'{i3}"big_proc": {{')
        for stat in BIG_PROC_STATS:
            if stat in bp:
                lines.append(f'{i4}"{stat}": {bp[stat]},')
        lines.append(f'{i3}}},')
        for rt in RUNE_TYPES:
            if rt in d:
                ov = d[rt]
                parts = []
                if "eff_support" in ov:
                    parts.append(f'"eff_support": {_fmt_eff(ov["eff_support"])}')
                if "eff_dps" in ov:
                    parts.append(f'"eff_dps": {_fmt_eff(ov["eff_dps"])}')
                if "big_proc" in ov:
                    bp_parts = ", ".join(f'"{k}": {v}' for k, v in ov["big_proc"].items())
                    parts.append(f'"big_proc": {{{bp_parts}}}')
                lines.append(f'{i3}"{rt}": {{{", ".join(parts)}}},')
            elif cat == "never_used":
                lines.append(f'{i3}# "{rt}": default')
        lines.append(f'{i2}}},')
    lines.append(f'{indent}}},')
    return "\n".join(lines)


def _replace_block(text: str, data_name: str, criteria: dict) -> str:
    start = text.find(f"{data_name} = {{")
    next_data = "data2 = {" if data_name == "data1" else None
    end = text.find(next_data) if next_data else len(text)

    kc_offset = text.find(f'"{CRITERIA_KEY}": {{', start, end)
    brace_pos = text.index("{", kc_offset + len(f'"{CRITERIA_KEY}":'))

    depth, pos = 0, brace_pos
    while pos < len(text):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                block_end = pos + 1
                if block_end < len(text) and text[block_end] == ",":
                    block_end += 1
                break
        pos += 1

    return text[:kc_offset] + _generate_block(criteria) + text[block_end:]


def _replace_sets(text: str, data_name: str, sets_by_cat: dict) -> str:
    """Replace SETS_* set literals inside a data block."""
    start = text.find(f"{data_name} = {{")
    next_data = "data2 = {" if data_name == "data1" else None
    end = text.find(next_data) if next_data else len(text)

    for cat, set_key in CATEGORY_SET_KEY.items():
        sets_list = sorted(sets_by_cat.get(cat, []))
        pattern = f'"{set_key}": {{'
        idx = text.find(pattern, start, end)
        if idx < 0:
            continue

        brace_pos = text.index("{", idx + len(f'"{set_key}":'))
        depth, pos = 0, brace_pos
        while pos < len(text):
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
                if depth == 0:
                    set_end = pos + 1
                    if set_end < len(text) and text[set_end] == ",":
                        set_end += 1
                    break
            pos += 1

        ref = re.search(r'\n( *)"EFF_GROUP_SUPPORT"', text[start:end])
        indent = ref.group(1) if ref else "        "
        if sets_list:
            lines = [f'{indent}"{set_key}": {{']
            for s in sets_list:
                lines.append(f'{indent}    "{s}",')
            lines.append(f'{indent}}},')
            new_block = "\n".join(lines)
        else:
            new_block = f'{indent}"{set_key}": {{}},'

        diff = len(new_block) - (set_end - idx)
        text = text[:idx] + new_block + text[set_end:]
        end += diff

    return text


# ─── routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template(
        "index.html",
        categories=CATEGORIES,
        rune_types=RUNE_TYPES,
        rune_type_labels=RUNE_TYPE_LABELS,
        big_proc_stats=BIG_PROC_STATS,
        buckets=BUCKETS,
        all_sets=ALL_SETS,
        eff_templates=EFF_TEMPLATES,
        eff_divisor=EFF_DIVISOR,
    )


@app.route("/api/load")
def api_load():
    return jsonify(_load_criteria())


@app.route("/api/save", methods=["POST"])
def api_save():
    try:
        body = request.get_json()
        criteria = {
            "data1": _normalise(body["data1"]),
            "data2": _normalise(body["data2"]),
        }
        sets_changes = body.get("sets")
        text = DATAS_PATH.read_text(encoding="utf-8")
        text = _replace_block(text, "data1", criteria["data1"])
        text = _replace_block(text, "data2", criteria["data2"])
        if sets_changes:
            text = _replace_sets(text, "data1", sets_changes.get("data1", {}))
            text = _replace_sets(text, "data2", sets_changes.get("data2", {}))
        DATAS_PATH.write_text(text, encoding="utf-8")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/eff_equiv", methods=["POST"])
def api_eff_equiv():
    try:
        body     = request.get_json()
        eff_key  = body["eff_key"]
        bucket   = int(body["bucket"])
        value    = float(body["value"])
        if eff_key not in ("eff_support", "eff_dps"):
            raise ValueError(f"Unknown eff_key: {eff_key}")
        if bucket not in (2, 3, 4):
            raise ValueError(f"bucket must be 2, 3 or 4")
        result = _eff_calc.find_equiv(value, bucket, eff_key)
        return jsonify({"ok": True, "result": {str(k): v for k, v in result.items()}, "ready": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/eff_equiv_ready")
def api_eff_equiv_ready():
    return jsonify({"ready": _eff_calc.is_ready})


# ─── entry point ──────────────────────────────────────────────────────────────

def run_upgrade_settings_ui():
    def _open_browser():
        import time
        time.sleep(0.8)
        webbrowser.open("http://127.0.0.1:5000")

    threading.Thread(target=_open_browser, daemon=True).start()
    app.run(debug=False, port=5000, use_reloader=False)


if __name__ == "__main__":
    run_upgrade_settings_ui()
