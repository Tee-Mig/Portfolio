"""
debug_runes.py — diagnostic pour check_runes_conditions
Positionne le jeu sur l'inventaire de runes, puis lance ce script.
Il détecte les runes à l'écran, teste la détection de la coche sur chacune,
et sauvegarde les crops dans debug/.

Usage:
    python debug_runes.py          # snapshot instantané
    python debug_runes.py --watch  # boucle toutes les 2 s (Ctrl+C pour arrêter)
    python debug_runes.py --hash   # teste le changement de hash RUNE_INFO_BBOX
                                   # (clique une rune manuellement pendant la pause)
"""

import os
import sys
import time
import hashlib
import argparse

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab

# ── mêmes constantes que runes.py ──────────────────────────────────────────────
RUNE_GRID_REGION  = (963, 350, 866, 398)   # (left, top, width, height) — pyautogui
MARKS_GRID_REGION = (963, 350, 866, 520)   # même top-left, hauteur étendue
RUNE_INFO_BBOX    = (283, 305, 620, 383)   # (left, top, right, bottom) — PIL
RUNE_STATS_BBOX   = (289, 493, 576, 685)   # (left, top, right, bottom) — PIL
CHECK_OFFSET_Y    = 45
THRESHOLD         = 0.80

os.makedirs("debug", exist_ok=True)


# ── helpers ────────────────────────────────────────────────────────────────────

def _hash(bbox_ltrb):
    img = ImageGrab.grab(bbox=bbox_ltrb)
    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    arr = cv2.resize(arr, (96, 96), interpolation=cv2.INTER_AREA)
    return hashlib.md5(arr.tobytes()).hexdigest()


def _locate(hay_bgr, needle_bgr, threshold=0.80, use_gray=False):
    hay = cv2.cvtColor(hay_bgr, cv2.COLOR_BGR2GRAY) if use_gray else hay_bgr
    nee = cv2.cvtColor(needle_bgr, cv2.COLOR_BGR2GRAY) if use_gray else needle_bgr
    if hay.shape[0] < nee.shape[0] or hay.shape[1] < nee.shape[1]:
        return []
    res = cv2.matchTemplate(hay, nee, cv2.TM_CCOEFF_NORMED)
    ys, xs = np.where(res >= threshold)
    return [(int(x + nee.shape[1] // 2), int(y + nee.shape[0] // 2))
            for x, y in zip(xs, ys)]


def _check_score(cx, cy, check_tpl, roi_half_w=75, roi_half_h=60):
    """Retourne (score, roi_bgr, max_loc) pour la position (cx, cy)."""
    center_x = cx
    center_y = cy + CHECK_OFFSET_Y
    left   = max(0, MARKS_GRID_REGION[0] + center_x - roi_half_w)
    top    = max(0, MARKS_GRID_REGION[1] + center_y - roi_half_h)
    w      = roi_half_w * 2
    h      = roi_half_h * 2

    roi     = pyautogui.screenshot(region=(left, top, w, h))
    roi_bgr = cv2.cvtColor(np.array(roi), cv2.COLOR_RGB2BGR)

    hay = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    nee = cv2.cvtColor(check_tpl, cv2.COLOR_BGR2GRAY)

    if hay.shape[0] < nee.shape[0] or hay.shape[1] < nee.shape[1]:
        return None, roi_bgr, None

    res = cv2.matchTemplate(hay, nee, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return float(max_val), roi_bgr, max_loc


def _annotate_roi(roi_bgr, check_tpl, score, max_loc):
    canvas = roi_bgr.copy()
    if max_loc is not None:
        nh, nw = check_tpl.shape[:2]
        x, y = max_loc
        color = (0, 200, 0) if score >= THRESHOLD else (0, 0, 220)
        cv2.rectangle(canvas, (x, y), (x + nw, y + nh), color, 2)
        label = f"{score:.3f} {'OK' if score >= THRESHOLD else 'FAIL'}"
        cv2.putText(canvas, label, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
    return canvas


# ── snapshot ───────────────────────────────────────────────────────────────────

def snapshot(check_tpl, rune_tpl_1, rune_tpl_2, ts_str):
    print(f"\n─── snapshot {ts_str} ───")

    # 1) Capture marks + info regions
    marks_img = pyautogui.screenshot(region=MARKS_GRID_REGION)
    marks_bgr = cv2.cvtColor(np.array(marks_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(f"debug/marks_{ts_str}.png", marks_bgr)

    info_img  = ImageGrab.grab(bbox=RUNE_INFO_BBOX)
    info_bgr  = cv2.cvtColor(np.array(info_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(f"debug/info_{ts_str}.png", info_bgr)
    info_hash = _hash(RUNE_INFO_BBOX)

    stats_img = ImageGrab.grab(bbox=RUNE_STATS_BBOX)
    stats_bgr = cv2.cvtColor(np.array(stats_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(f"debug/stats_{ts_str}.png", stats_bgr)
    stats_hash = _hash(RUNE_STATS_BBOX)

    print(f"  info  hash : {info_hash}")
    print(f"  stats hash : {stats_hash}")
    print(f"  Saved: debug/marks_{ts_str}.png  debug/info_{ts_str}.png  debug/stats_{ts_str}.png")

    # 2) Detect rune positions
    rune_img = pyautogui.screenshot(region=RUNE_GRID_REGION)
    rune_bgr = cv2.cvtColor(np.array(rune_img), cv2.COLOR_RGB2BGR)
    locs = []
    if rune_tpl_1 is not None:
        locs += _locate(rune_bgr, rune_tpl_1, 0.80)
    if rune_tpl_2 is not None:
        locs += _locate(rune_bgr, rune_tpl_2, 0.80)

    print(f"  Runes détectées : {len(locs)}  positions={locs}")

    # 3) Check score for each rune
    rois = []
    for i, (cx, cy) in enumerate(locs):
        score, roi_bgr, max_loc = _check_score(cx, cy, check_tpl)
        if score is None:
            print(f"  rune {i} ({cx:4d},{cy:4d}): ROI trop petite")
            continue
        ok = score >= THRESHOLD
        flag = "✓ DETECTE" if ok else "✗ non detecte"
        print(f"  rune {i} ({cx:4d},{cy:4d}): score={score:.4f}  {flag}")

        ann = _annotate_roi(roi_bgr, check_tpl, score, max_loc)
        roi_path = f"debug/roi_{i}_{cx}_{cy}_{ts_str}.png"
        cv2.imwrite(roi_path, ann)
        rois.append(ann)

    # composite
    if rois:
        max_h = max(r.shape[0] for r in rois)
        max_w = max(r.shape[1] for r in rois)
        tiles = []
        for r in rois:
            pad = np.zeros((max_h, max_w, 3), dtype=np.uint8)
            pad[:r.shape[0], :r.shape[1]] = r
            tiles.append(pad)
        cv2.imwrite(f"debug/composite_{ts_str}.png", np.hstack(tiles))
        print(f"  Composite ROIs → debug/composite_{ts_str}.png")

    return info_hash, stats_hash


# ── hash change test ───────────────────────────────────────────────────────────

def test_hash_change():
    print("\n=== Test changement de hash ===")
    print("Capture initiale en cours...")
    h_info_before  = _hash(RUNE_INFO_BBOX)
    h_stats_before = _hash(RUNE_STATS_BBOX)
    print(f"  info  avant  : {h_info_before}")
    print(f"  stats avant  : {h_stats_before}")

    print("\nClique maintenant sur une rune (tu as 5 secondes)...")
    time.sleep(5)

    h_info_after  = _hash(RUNE_INFO_BBOX)
    h_stats_after = _hash(RUNE_STATS_BBOX)
    print(f"\n  info  apres  : {h_info_after}")
    print(f"  stats apres  : {h_stats_after}")

    info_changed  = h_info_before  != h_info_after
    stats_changed = h_stats_before != h_stats_after
    print(f"\n  RUNE_INFO_BBOX  change : {'OUI ✓' if info_changed  else 'NON ✗'}")
    print(f"  RUNE_STATS_BBOX change : {'OUI ✓' if stats_changed else 'NON ✗'}")

    if not info_changed and not stats_changed:
        print("\n  → Ni info ni stats ne changent : les bboxes sont peut-etre mal positionnees.")
        print("    Verifie RUNE_INFO_BBOX et RUNE_STATS_BBOX dans debug_runes.py.")
    elif stats_changed and not info_changed:
        print("\n  → stats change mais pas info : utiliser RUNE_STATS_BBOX comme signal de fallback.")

    ts_str = time.strftime("%Y%m%d_%H%M%S")
    for name, bbox in [("info_after", RUNE_INFO_BBOX), ("stats_after", RUNE_STATS_BBOX)]:
        img = cv2.cvtColor(np.array(ImageGrab.grab(bbox=bbox)), cv2.COLOR_RGB2BGR)
        cv2.imwrite(f"debug/{name}_{ts_str}.png", img)
    print(f"\n  Captures après → debug/info_after_{ts_str}.png  debug/stats_after_{ts_str}.png")


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="boucle snapshot toutes les 2 s")
    parser.add_argument("--hash",  action="store_true", help="teste changement de hash des bboxes")
    args = parser.parse_args()

    check_tpl  = cv2.imread("img/check2.png")
    rune_tpl_1 = cv2.imread("img/rune_inventory.png")
    rune_tpl_2 = cv2.imread("img/rune2.png")

    if check_tpl is None:
        print("ERREUR: img/check2.png introuvable")
        sys.exit(1)

    if args.hash:
        test_hash_change()
        return

    if args.watch:
        print("Mode watch — Ctrl+C pour arrêter\n")
        try:
            while True:
                ts_str = time.strftime("%Y%m%d_%H%M%S")
                snapshot(check_tpl, rune_tpl_1, rune_tpl_2, ts_str)
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nArrete.")
    else:
        ts_str = time.strftime("%Y%m%d_%H%M%S")
        snapshot(check_tpl, rune_tpl_1, rune_tpl_2, ts_str)
        print("\nTermine. Verifie le dossier debug/")


if __name__ == "__main__":
    main()
