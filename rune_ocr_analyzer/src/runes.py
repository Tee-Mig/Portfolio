from src.click import click_img, drag_and_drop_with_random_area
import pytesseract
from random import uniform
from time import time, sleep
import cv2
import numpy as np
import pyautogui
import random
import hashlib
from PIL import ImageGrab
from src.up_runes import check_rune_conditions
from src.packs import NOT_SHOW_TODAY_DUNGEON
from src.screen import find_img
import os

# ----------------------------
# Tesseract
# ----------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ----------------------------
# Regions
# ----------------------------
RUNE_GRID_REGION = (963, 350, 866, 398)  # (left, top, width, height)

RUNE_INFO_BBOX = (283, 305, 620, 383)
RUNE_STATS_BBOX = (289, 493, 287, 192)

MATCH_THRESHOLD = 0.80

SOLD_TEMPLATE_PATH = "img/sold2.png"  # adapte le nom si besoin
CHECK_TEMPLATE_PATH = "img/check2.png"  # adapte le nom si besoin

OVERLAY_CONFIDENCE = 0.84  # ajuste si besoin (0.80-0.90)
OVERLAY_BOX_SIZE = 70  # taille du petit carré sous la rune (px)
OVERLAY_Y_OFFSET = 58  # décalage vertical sous le centre de la rune (px)
MIN_DISTANCE = 20


# ============================================================
#  UTILS
# ============================================================
def _cluster_1d(values, tol=35):
    """
    Regroupe des coords 1D (x ou y) en 'centres' de colonnes/lignes.
    tol ~ distance max entre points d'une même colonne/ligne.
    """
    vals = sorted(values)
    clusters = []
    for v in vals:
        if not clusters or abs(v - clusters[-1][-1]) > tol:
            clusters.append([v])
        else:
            clusters[-1].append(v)
    centers = [int(sum(c) / len(c)) for c in clusters]
    return centers


def _nearest_index(centers, v):
    return min(range(len(centers)), key=lambda i: abs(centers[i] - v))


def filter_close_points(points, min_distance=20):
    """
    Garde un seul point par zone.
    Accepte uniquement des points (x, y).
    """
    filtered = []

    for pt in points:
        # ✅ sécurité absolue
        if (
            not isinstance(pt, (tuple, list))
            or len(pt) != 2
            or not isinstance(pt[0], (int, float))
            or not isinstance(pt[1], (int, float))
        ):
            continue

        x, y = pt
        keep = True

        for fx, fy in filtered:
            dx = x - fx
            dy = y - fy
            if (dx * dx + dy * dy) < (min_distance * min_distance):
                keep = False
                break

        if keep:
            filtered.append((int(x), int(y)))

    return filtered


def locate_template(haystack, needle, threshold=MATCH_THRESHOLD, use_gray=False):
    if use_gray:
        haystack = cv2.cvtColor(haystack, cv2.COLOR_BGR2GRAY)
        needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    w, h = needle.shape[1], needle.shape[0]
    return [(int(pt[0] + w / 2), int(pt[1] + h / 2)) for pt in zip(*locations[::-1])]


def region_has_overlap(center, template_size, other_locations):
    """
    EXACTEMENT la logique de ton remove_rune_with_bad_subs().
    center / other_locations sont dans le même repère (relatif à la grille).
    template_size = (w,h) du marqueur (check ou sold)
    """
    x, y = center
    w, h = template_size
    for ox, oy in other_locations:
        if abs(x - ox) < w and abs(y - oy) < h:
            return True
    return False


def _match_in_crop(crop_bgr: np.ndarray, tpl_bgr: np.ndarray, threshold: float) -> bool:
    if crop_bgr is None or tpl_bgr is None:
        return False
    ch, cw = crop_bgr.shape[:2]
    th, tw = tpl_bgr.shape[:2]
    if ch < th or cw < tw:
        return False

    crop_g = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    tpl_g = cv2.cvtColor(tpl_bgr, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(crop_g, tpl_g, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return max_val >= threshold


def tile_has_forbidden_overlay(tile_bbox, sold_tpl, check_tpl) -> bool:
    """
    ✅ Cherche SOLD / CHECK à l’intérieur de la tuile.
    """
    tile_rgb = np.array(ImageGrab.grab(bbox=tile_bbox))
    tile_bgr = cv2.cvtColor(tile_rgb, cv2.COLOR_RGB2BGR)

    return _match_in_crop(tile_bgr, sold_tpl, OVERLAY_CONFIDENCE) or _match_in_crop(
        tile_bgr, check_tpl, OVERLAY_CONFIDENCE
    )


def has_forbidden_overlay(
    screen_x: int, screen_y: int, sold_tpl: np.ndarray, check_tpl: np.ndarray
) -> bool:
    """
    Check un petit carré juste SOUS la rune (où apparaissent SOLD/check chez toi).
    """
    half = OVERLAY_BOX_SIZE // 2
    cx = screen_x
    cy = screen_y + OVERLAY_Y_OFFSET

    left = max(0, cx - half)
    top = max(0, cy - half)
    right = cx + half
    bottom = cy + half

    crop_rgb = np.array(ImageGrab.grab(bbox=(left, top, right, bottom)))
    crop_bgr = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2BGR)

    return _match_in_crop(crop_bgr, sold_tpl, OVERLAY_CONFIDENCE) or _match_in_crop(
        crop_bgr, check_tpl, OVERLAY_CONFIDENCE
    )


def dedupe_points(points, min_dist=30):
    out = []
    md2 = min_dist * min_dist
    for p in points:
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= md2 for q in out):
            out.append(p)
    return out


def _hash_bbox_fast(bbox) -> str:
    img = ImageGrab.grab(bbox=bbox)
    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    arr = cv2.resize(arr, (128, 128), interpolation=cv2.INTER_AREA)
    return hashlib.md5(arr.tobytes()).hexdigest()


def wait_until_selected(prev_stats_hash, tile_bbox, timeout=2.2, poll=0.06):
    """
    Valide si :
    - les substats changent (meilleur signal)
    OU
    - la tuile change (fallback : sélection highlight)
    """
    start = time()
    before_tile = np.array(ImageGrab.grab(bbox=tile_bbox))

    while time() - start < timeout:
        sleep(poll)

        new_stats_hash = _hash_bbox_fast(RUNE_STATS_BBOX)
        if prev_stats_hash is None or new_stats_hash != prev_stats_hash:
            return new_stats_hash, True

        after_tile = np.array(ImageGrab.grab(bbox=tile_bbox))
        diff = cv2.absdiff(before_tile, after_tile)
        ratio = np.count_nonzero(diff) / diff.size
        if ratio > 0.0035:  # seuil stable
            return prev_stats_hash, True

    return prev_stats_hash, False


def _hash_bbox(bbox) -> str:
    img = ImageGrab.grab(bbox=bbox)
    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    arr = cv2.resize(arr, (96, 96), interpolation=cv2.INTER_AREA)
    return hashlib.md5(arr.tobytes()).hexdigest()


def tile_bbox_from_center(cx, cy, w, h, margin=0.85):
    rw = int(w * margin)
    rh = int(h * margin)
    left = cx - rw // 2
    top = cy - rh // 2
    right = cx + rw // 2
    bottom = cy + rh // 2
    return (left, top, right, bottom)


def wait_until_selection_changes(
    prev_info_hash, tile_bbox, require_info_change, timeout=1.8, poll=0.05
):
    """
    - True si infos changent
    - ou (uniquement si require_info_change=False) si la tuile change de façon stable
    """
    start = time()

    before_tile = np.array(ImageGrab.grab(bbox=tile_bbox))
    stable_hits = 0

    while time() - start < timeout:
        sleep(poll)

        new_info_hash = _hash_bbox(RUNE_INFO_BBOX)
        if prev_info_hash is None or new_info_hash != prev_info_hash:
            return new_info_hash, True

        if require_info_change:
            continue

        after_tile = np.array(ImageGrab.grab(bbox=tile_bbox))
        diff = cv2.absdiff(before_tile, after_tile)
        ratio = np.count_nonzero(diff) / diff.size

        # seuil + stabilité pour éviter les animations
        if ratio > 0.004:
            stable_hits += 1
            if stable_hits >= 3:
                return prev_info_hash, True
        else:
            stable_hits = 0

    return prev_info_hash, False


def locate_template_peaks(haystack_bgr, needle_bgr, threshold=0.80):
    hay = cv2.cvtColor(haystack_bgr, cv2.COLOR_BGR2GRAY)
    nee = cv2.cvtColor(needle_bgr, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(hay, nee, cv2.TM_CCOEFF_NORMED)
    h, w = nee.shape[:2]

    points = []
    while True:
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val < threshold:
            break

        x, y = max_loc
        points.append((x + w // 2, y + h // 2))

        # NMS autour du pic
        x1 = max(0, x - w // 2)
        y1 = max(0, y - h // 2)
        x2 = min(res.shape[1], x + w // 2)
        y2 = min(res.shape[0], y + h // 2)
        res[y1:y2, x1:x2] = -1.0

    return points, (w, h)


def sort_grid_points(points):
    return sorted(points, key=lambda p: (p[1], p[0]))


def random_point_in_tile(center_x, center_y, w, h, reduction=0.75):
    rw = int(w * reduction)
    rh = int(h * reduction)
    return (
        random.randint(center_x - rw // 2, center_x + rw // 2),
        random.randint(center_y - rh // 2, center_y + rh // 2),
    )


# ============================================================
#  MAIN
# ============================================================


def debug_draw_check_zones(
    rune_locations,
    MARKS_GRID_REGION=(963, 350, 866, 520),
    check_template_path="img/check2.png",
    sold_template_path="img/sold2.png",
    check_threshold=0.80,
    sold_threshold=0.80,
    check_inflation=(20, 50),  # (extra_w, extra_h) comme ton check_size_inflated
    out_dir="debug",
    show=False,  # True => cv2.imshow
):
    """
    Dessine:
      - en VERT : bounding boxes des matches check2 détectés
      - en ROUGE : bounding boxes des matches sold2 détectés
      - en BLEU : zone attendue (autour de chaque rune center) où un check devrait se trouver

    rune_locations: liste de (cx,cy) en coordonnées RELATIVES à RUNE_GRID_REGION.
    IMPORTANT: ça marche si MARKS_GRID_REGION a le même top-left que RUNE_GRID_REGION (chez toi oui).
    """

    os.makedirs(out_dir, exist_ok=True)

    # Screenshot marks
    marks_img = pyautogui.screenshot(region=MARKS_GRID_REGION)
    marks_bgr = cv2.cvtColor(np.array(marks_img), cv2.COLOR_RGB2BGR)

    # Load templates
    check_t = cv2.imread(check_template_path)
    sold_t = cv2.imread(sold_template_path)

    if check_t is None:
        raise FileNotFoundError(check_template_path)
    if sold_t is None:
        raise FileNotFoundError(sold_template_path)

    ch_h, ch_w = check_t.shape[:2]
    sd_h, sd_w = sold_t.shape[:2]

    # Helper: find centers via matchTemplate (comme ton locate_template)
    def _locate_centers(hay_bgr, needle_bgr, threshold=0.80, use_gray=False):
        hay = cv2.cvtColor(hay_bgr, cv2.COLOR_BGR2GRAY) if use_gray else hay_bgr
        nee = cv2.cvtColor(needle_bgr, cv2.COLOR_BGR2GRAY) if use_gray else needle_bgr

        res = cv2.matchTemplate(hay, nee, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(res >= threshold)
        centers = []
        for x, y in zip(xs, ys):
            centers.append(
                (int(x + needle_bgr.shape[1] / 2), int(y + needle_bgr.shape[0] / 2))
            )
        return centers

    # Detect check/sold in MARKS_GRID_REGION screenshot
    check_centers = _locate_centers(
        marks_bgr, check_t, threshold=check_threshold, use_gray=True
    )
    sold_centers = _locate_centers(
        marks_bgr, sold_t, threshold=sold_threshold, use_gray=False
    )

    # Optionnel: dédoublonner un peu (sinon tu peux voir plusieurs rectangles proches)
    def _dedupe(pts, min_dist=15):
        out = []
        for p in pts:
            if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= min_dist**2 for q in out):
                out.append(p)
        return out

    check_centers = _dedupe(check_centers, 15)
    sold_centers = _dedupe(sold_centers, 15)

    canvas = marks_bgr.copy()

    # Draw CHECK matches (VERT)
    for cx, cy in check_centers:
        x1, y1 = cx - ch_w // 2, cy - ch_h // 2
        x2, y2 = cx + ch_w // 2, cy + ch_h // 2
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Draw SOLD matches (ROUGE)
    for cx, cy in sold_centers:
        x1, y1 = cx - sd_w // 2, cy - sd_h // 2
        x2, y2 = cx + sd_w // 2, cy + sd_h // 2
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # Draw expected check zone around EACH rune center (BLEU)
    extra_w, extra_h = check_inflation
    exp_w = ch_w + extra_w
    exp_h = ch_h + extra_h

    for rx, ry in rune_locations:
        # rx,ry sont déjà dans le repère de MARKS_GRID_REGION (top-left identique à RUNE_GRID_REGION)
        x1, y1 = int(rx - exp_w // 2), int(ry - exp_h // 2)
        x2, y2 = int(rx + exp_w // 2), int(ry + exp_h // 2)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Save
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"debug_marks_{ts}.png")
    cv2.imwrite(out_path, canvas)

    if show:
        cv2.imshow("DEBUG MARKS", canvas)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print(f"[DEBUG] saved: {out_path}")
    return out_path


def check_runes_conditions(upgrade_rune_settings):
    """
    - Clique chaque rune (rune_inventory + rune2) non sold et non déjà checkée
    - Valide sélection par apparition de check2.png (local ROI)
    - Appelle up_runes()
    - Si keep=True : re-clic jusqu'à disparition de check2.png
    """

    # --- regions ---
    RUNE_GRID_REGION = (963, 350, 866, 398)
    MARKS_GRID_REGION = (963, 350, 866, 520)  # même top-left que RUNE_GRID_REGION

    CHECK_OFFSET_Y = 45  # ton offset validé

    # --- templates ---
    rune_template_1 = cv2.imread("img/rune_inventory.png")
    rune_template_2 = cv2.imread("img/rune2.png")
    sold_template = cv2.imread("img/sold2.png")
    check_template = cv2.imread("img/check2.png")

    if rune_template_1 is None or rune_template_2 is None:
        raise FileNotFoundError("img/rune_inventory.png ou img/rune2.png introuvable")
    if sold_template is None or check_template is None:
        raise FileNotFoundError("img/sold2.png ou img/check2.png introuvable")

    # tailles (w,h)
    sold_w, sold_h = sold_template.shape[1], sold_template.shape[0]

    # tile size pour construire tile_bbox
    tile_w = max(rune_template_1.shape[1], rune_template_2.shape[1])
    tile_h = max(rune_template_1.shape[0], rune_template_2.shape[0])

    # --- detect runes in grid ---
    rune_img = pyautogui.screenshot(region=RUNE_GRID_REGION)
    rune_bgr = cv2.cvtColor(np.array(rune_img), cv2.COLOR_RGB2BGR)

    rune_locs_1 = locate_template(
        rune_bgr, rune_template_1, threshold=0.80, use_gray=False
    )
    rune_locs_2 = locate_template(
        rune_bgr, rune_template_2, threshold=0.80, use_gray=False
    )

    rune_locations = filter_close_points(rune_locs_1 + rune_locs_2, min_distance=25)
    rune_locations = sort_grid_points(rune_locations)

    if not rune_locations:
        return

    # ------------------------------------------------------------
    # Helpers: SOLD global (comme remove_rune_with_bad_subs)
    # ------------------------------------------------------------
    def _read_sold_locations():
        marks_img = pyautogui.screenshot(region=MARKS_GRID_REGION)
        marks_bgr = cv2.cvtColor(np.array(marks_img), cv2.COLOR_RGB2BGR)
        sold_locations = locate_template(
            marks_bgr, sold_template, threshold=0.80, use_gray=False
        )
        sold_locations = filter_close_points(sold_locations, min_distance=15)
        return sold_locations

    # ------------------------------------------------------------
    # Helpers: CHECK local (anti faux positifs)
    # ------------------------------------------------------------
    def _is_check_local(cx, cy, roi_half_w=75, roi_half_h=60, threshold=0.80) -> bool:
        """
        Détecte check2.png uniquement dans une petite zone autour de la rune (local).
        cx,cy sont dans le repère de la grille (relatif à RUNE_GRID_REGION / MARKS_GRID_REGION).
        """
        center_x = cx
        center_y = cy + CHECK_OFFSET_Y

        left = MARKS_GRID_REGION[0] + (center_x - roi_half_w)
        top = MARKS_GRID_REGION[1] + (center_y - roi_half_h)
        right = MARKS_GRID_REGION[0] + (center_x + roi_half_w)
        bottom = MARKS_GRID_REGION[1] + (center_y + roi_half_h)

        left = max(0, left)
        top = max(0, top)
        w = max(1, right - left)
        h = max(1, bottom - top)

        roi = pyautogui.screenshot(region=(left, top, w, h))
        roi_bgr = cv2.cvtColor(np.array(roi), cv2.COLOR_RGB2BGR)

        hay = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        nee = cv2.cvtColor(check_template, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(hay, nee, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        return max_val >= threshold

    # ------------------------------------------------------------
    # Helper: stabilité légère (remplace stable_hits_required)
    # ------------------------------------------------------------
    def _stable(fn, hits_required=2):
        hits = {"n": 0}

        def _wrapped():
            if fn():
                hits["n"] += 1
            else:
                hits["n"] = 0
            return hits["n"] >= hits_required

        return _wrapped

    visited = set()
    sold_locations = _read_sold_locations()

    for cx, cy in rune_locations:
        cell_id = (int(cx / 10), int(cy / 10))
        if cell_id in visited:
            continue

        # Skip SOLD (global)
        if region_has_overlap((cx, cy), (sold_w, sold_h), sold_locations):
            visited.add(cell_id)
            continue

        # Skip déjà checkée (local)
        if _is_check_local(cx, cy):
            visited.add(cell_id)
            continue

        # bbox tuile (clic random dans la rune)
        screen_x = RUNE_GRID_REGION[0] + cx
        screen_y = RUNE_GRID_REGION[1] + cy
        tile_bbox = tile_bbox_from_center(
            screen_x, screen_y, tile_w, tile_h, margin=0.85
        )

        # 1) Sélection: click + sondage rapide (anti-glow, anti-toggle)
        # Laisser l'UI se stabiliser après la désélection précédente
        sleep(0.15)
        _prev_info_hash = _hash_bbox(RUNE_INFO_BBOX)
        _call_n = [0]

        def _validate_selected():
            _call_n[0] += 1
            if _call_n[0] == 1:
                # Premier appel (avant le clic) : toujours False pour déclencher le clic
                return False
            # Après le clic : sonder toutes les 80ms sur ~1.5s pour couvrir le cycle de glow
            t_end = time() + 1.5
            while time() < t_end:
                if _is_check_local(cx, cy):
                    return True
                sleep(0.08)
            # Fallback : si le panneau d'info a changé, le clic a bien été pris en compte
            return _hash_bbox(RUNE_INFO_BBOX) != _prev_info_hash

        click_img(box=tile_bbox, validate_fn=_validate_selected)

        # 2) Traitement
        keep = check_rune_conditions(
            upgrade_rune_settings["upgrade_rune_settings"],
            upgrade_rune_settings["save_rune_settings"],
        )

        # 3) Si keep: re-clic jusqu'à disparition du check
        if keep:
            click_img(
                box=tile_bbox,
                validate_fn=_stable(
                    lambda: not _is_check_local(cx, cy), hits_required=2
                ),
            )

        visited.add(cell_id)


def up_runes_group_to_plus_12(upgrade_rune_settings):
    for i in range(4):
        click_img(
            [(f"img/plus_{(i + 1) * 3}_unselected.png",)],
            [(f"img/plus_{(i + 1) * 3}_selected.png",)],
        )
        click_img(
            [("img/ok2.png",)],
            [("img/vente_selective_inventory1.png",)],
        )
        click_img(
            [("img/vente_selective_inventory1.png",)],
            [("img/vente_selective_inventory2.png",)],
            reclick_time=uniform(0.3, 0.4),
        )
        if i > 0:
            drag_and_drop_with_random_area((1279, 403), 20, (1275, 783), 20)
        check_runes_conditions(upgrade_rune_settings)
        while find_img(
            [("img/no_rune_bottom.png",)]
        ) is False and drag_and_drop_with_random_area((1275, 783), 20, (1279, 403), 20):
            check_runes_conditions(upgrade_rune_settings)

        click_img(
            [("img/vente_selective_inventory2.png",)],
            [("img/oui.png",), ("img/ok.png",)],
        )
        if find_img([("img/ok.png",)]):
            click_img(
                [("img/ok.png",)],
                [{"path": "img/annuler_inventory.png", "precise": True}],
            )
            click_img(
                [("img/annuler_inventory.png",)],
                [("img/vente_selective_inventory1.png",)],
            )
        else:
            click_img(
                NOT_SHOW_TODAY_DUNGEON,
                [("img/vente_selective_inventory1.png",)],
                reclick_time=uniform(0.3, 0.4),
            )

        if i < 3:
            click_img(
                [("img/amelioration_selective.png",)],
                [("img/ok2.png",), ("img/ok.png",)],
            )
        if find_img([("img/ok.png",)]):
            click_img(
                [("img/ok.png",)],
                [{"path": "img/vente_selective_inventory1.png", "precise": True}],
            )
            break


def up_runes_group(upgrade_rune_settings):
    up_runes_group_to_plus_12(upgrade_rune_settings)


def up_runes_inventory(upgrade_rune_settings):
    while True:
        click_img(
            [("img/upgrade_group_runes_button.png",)], [("img/selection_groupee.png",)]
        )
        for i in range(3):
            click_img([("img/selection_groupee.png",)])
            click_img(
                [("img/amelioration_selective_inventory.png",)],
                [("img/ok.png",), ("img/ok2.png",)],
            )
            if find_img([("img/ok2.png",)]):
                break
            click_img([("img/ok.png",)], [("img/selection_groupee.png",)])

        if find_img([("img/selection_groupee.png",)]):
            click_img([("img/annuler.png",)], wait_until_images_to_click_gone=True)
            break

        up_runes_group_to_plus_12(upgrade_rune_settings)
        click_img([("img/croix1.png",)], [("img/upgrade_group_runes_button.png",)])
