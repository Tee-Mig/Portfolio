"""
Rune upgrade analysis — one chart per page, navigate with ← → arrow keys.

Usage:
    python rune_analysis.py                           # all runes, runes/ folder
    python rune_analysis.py runes/data1               # specific sub-folder
    python rune_analysis.py --today                   # today's runes only
    python rune_analysis.py --date 2026-05-22         # specific date
    python rune_analysis.py --save report.pdf         # save all charts to PDF
    python rune_analysis.py runes/data1 --today --save today.pdf
"""

import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
import numpy as np
import pandas as pd
import datetime as _dt

# ── style ─────────────────────────────────────────────────────────────────────

BG_FIG = "#F5F3FF"
BG_AX = "#FFFFFF"
C_TITLE = "#2E1065"
C_LABEL = "#4C4F69"
C_GRID = "#E9D5FF"
C_SPINE = "#DDD6FE"

COLORS = {
    "KEEP": "#6D28D9",
    "TEST": "#FBBF24",
    "SELL": "#F87171",
}

PURPLE_PALETTE = [
    "#2E1065",
    "#4C1D95",
    "#5B21B6",
    "#6D28D9",
    "#7C3AED",
    "#8B5CF6",
    "#A78BFA",
    "#C4B5FD",
    "#DDD6FE",
    "#EDE9FE",
]

REASON_COLORS = {
    "big_proc": "#2E1065",
    "big_proc_possible": "#7C3AED",
    "eff": "#5B21B6",
    "test_eff": "#8B5CF6",
    "eff_fail": "#C4B5FD",
    "unknown": "#9CA3AF",
    "other": "#D1D5DB",
}

RUNES_ROOT = Path("data")
MARGIN_BINS = [-0.15, -0.10, -0.05, 0.0, 0.02, 0.04, 0.06, 0.10, 0.15, 0.25]
BORDERLINE_THRESH = 0.02
KNOWN_TAGS = {"eff", "big_proc", "big_proc_possible", "test_eff", "eff_fail", "unknown"}


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BG_FIG,
            "axes.facecolor": BG_AX,
            "axes.edgecolor": C_SPINE,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlecolor": C_TITLE,
            "axes.titleweight": "bold",
            "axes.titlesize": 17,
            "axes.titlepad": 16,
            "axes.labelcolor": C_LABEL,
            "axes.labelsize": 11,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": C_GRID,
            "grid.linestyle": "--",
            "grid.alpha": 0.7,
            "xtick.color": C_LABEL,
            "ytick.color": C_LABEL,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "text.color": C_LABEL,
            "legend.framealpha": 0.95,
            "legend.edgecolor": C_SPINE,
            "legend.fontsize": 9,
            "patch.linewidth": 0,
        }
    )


def _rounded_rect_path(x, y, w, h, rx, ry):
    """Path for a rounded rectangle with separate x/y radii (bezier approximation)."""
    rx = min(rx, abs(w) * 0.499)
    ry = min(ry, abs(h) * 0.499)
    k = 0.5522847498
    kx, ky = rx * k, ry * k
    verts = [
        (x + rx, y),
        (x + w - rx, y),
        (x + w - rx + kx, y),
        (x + w, y + ry - ky),
        (x + w, y + ry),
        (x + w, y + h - ry),
        (x + w, y + h - ry + ky),
        (x + w - rx + kx, y + h),
        (x + w - rx, y + h),
        (x + rx, y + h),
        (x + rx - kx, y + h),
        (x, y + h - ry + ky),
        (x, y + h - ry),
        (x, y + ry),
        (x, y + ry - ky),
        (x + rx - kx, y),
        (x + rx, y),
        (x + rx, y),
    ]
    codes = [
        MPath.MOVETO,
        MPath.LINETO,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.LINETO,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.LINETO,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.LINETO,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.CLOSEPOLY,
    ]
    return MPath(verts, codes)


def _axis_ppx_ppy(ax):
    """Approx pixels-per-data-unit for x and y (before tight_layout)."""
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    pos = ax.get_position()
    fw, fh = ax.get_figure().get_size_inches()
    ppx = pos.width * fw * 72 / max(abs(xlim[1] - xlim[0]), 1e-9)
    ppy = pos.height * fh * 72 / max(abs(ylim[1] - ylim[0]), 1e-9)
    return ppx, ppy


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _txt(hex_color: str) -> str:
    return "white" if _lum(hex_color) < 0.5 else C_TITLE


def _round_bars(ax, *, horizontal: bool, r_frac: float = 0.45) -> None:
    """Replace single-segment bar patches with rounded PathPatch (display-correct radii)."""
    ppx, ppy = _axis_ppx_ppy(ax)
    to_add = []
    for patch in ax.patches:
        x, y = patch.get_x(), patch.get_y()
        w, h = patch.get_width(), patch.get_height()
        if horizontal:
            if abs(w) < 1e-9:
                patch.set_visible(False)
                continue
            ry = min(abs(h) * r_frac, abs(h) * 0.499)
            rx = min(ry * ppy / max(ppx, 1e-9), abs(w) * 0.499)
        else:
            if abs(h) < 1e-9:
                patch.set_visible(False)
                continue
            rx = min(abs(w) * r_frac, abs(w) * 0.499)
            ry = min(rx * ppx / max(ppy, 1e-9), abs(h) * 0.499)
        fp = PathPatch(
            _rounded_rect_path(x, y, abs(w), abs(h), rx, ry),
            facecolor=patch.get_facecolor(),
            edgecolor="none",
            linewidth=0,
            zorder=patch.get_zorder(),
            transform=ax.transData,
            clip_on=True,
        )
        patch.set_visible(False)
        to_add.append(fp)
    for fp in to_add:
        ax.add_patch(fp)


def _round_stacked(ax, *, horizontal: bool, r_frac: float = 0.45) -> None:
    """Clip stacked bars to a rounded outer shape — only outer ends are rounded."""
    ppx, ppy = _axis_ppx_ppy(ax)
    groups: dict = {}
    for patch in ax.patches:
        w, h = patch.get_width(), patch.get_height()
        if horizontal:
            if abs(w) < 1e-9:
                continue
            key = round(patch.get_y(), 6)
        else:
            if abs(h) < 1e-9:
                continue
            key = round(patch.get_x(), 6)
        groups.setdefault(key, []).append(patch)

    for key, patches in groups.items():
        if horizontal:
            h_bar = patches[0].get_height()
            y_bar = patches[0].get_y()
            x_min = min(p.get_x() for p in patches)
            x_max = max(p.get_x() + p.get_width() for p in patches)
            w_bar = x_max - x_min
            ry = min(h_bar * r_frac, h_bar * 0.499)
            rx = min(ry * ppy / max(ppx, 1e-9), w_bar * 0.499)
            path = _rounded_rect_path(x_min, y_bar, w_bar, h_bar, rx, ry)
        else:
            w_bar = patches[0].get_width()
            x_bar = patches[0].get_x()
            y_min = min(p.get_y() for p in patches)
            y_max = max(p.get_y() + p.get_height() for p in patches)
            h_bar = y_max - y_min
            rx = min(w_bar * r_frac, w_bar * 0.499)
            ry = min(rx * ppx / max(ppy, 1e-9), h_bar * 0.499)
            path = _rounded_rect_path(x_bar, y_min, w_bar, h_bar, rx, ry)

        clip = PathPatch(
            path, transform=ax.transData, facecolor="none", edgecolor="none"
        )
        ax.add_patch(clip)
        for patch in patches:
            patch.set_clip_path(clip)


# ── helpers ───────────────────────────────────────────────────────────────────


def _val(v) -> str:
    """Return empty string for None/NaN, else str(v)."""
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    return str(v)


def _slot_str(v) -> str:
    try:
        return str(int(float(v)))
    except (TypeError, ValueError):
        return _val(v)


def _dedup_runes(df: pd.DataFrame) -> pd.DataFrame:
    """Keep one entry per unique rune, highest level first.

    Identity: set + slot + main + sub_keys (subset match to handle OCR misses and
    hero runes where the 4th sub is only revealed at +12).
    Priority: higher level > KEEP > TEST > SELL > latest timestamp.
    """
    if df.empty:
        return df

    def _sks(subs_val):
        if not isinstance(subs_val, (list, tuple)):
            return frozenset()
        return frozenset(
            s["key"] for s in subs_val if isinstance(s, dict) and "key" in s
        )

    df = df.copy()
    df["_sks"] = df["subs"].apply(_sks) if "subs" in df.columns else [frozenset()] * len(df)
    df["_gkey"] = (
        df["set"].astype(str) + "|" +
        df["slot"].astype(str) + "|" +
        df["main"].astype(str)
    )
    _dec_order = {"KEEP": 0, "TEST": 1, "SELL": 2}
    df["_dec_ord"] = df["decision"].map(_dec_order).fillna(3)
    df["_ts"] = pd.to_datetime(df.get("timestamp", pd.Series(dtype=str)), errors="coerce")
    df["_lvl"] = pd.to_numeric(df.get("level", pd.Series(dtype=float)), errors="coerce").fillna(0)

    df = df.sort_values(
        ["_gkey", "_lvl", "_dec_ord", "_ts"],
        ascending=[True, False, True, False],
    ).reset_index(drop=True)

    to_drop: set[int] = set()
    for _, grp in df.groupby("_gkey", sort=False):
        idx = grp.index.tolist()
        for i in range(len(idx)):
            if idx[i] in to_drop:
                continue
            si = df.at[idx[i], "_sks"]
            for j in range(i + 1, len(idx)):
                if idx[j] in to_drop:
                    continue
                sj = df.at[idx[j], "_sks"]
                if si.issubset(sj) or sj.issubset(si):
                    to_drop.add(idx[j])

    df = df.drop(index=list(to_drop))
    df = df.drop(columns=["_sks", "_gkey", "_dec_ord", "_ts", "_lvl"], errors="ignore")
    return df.reset_index(drop=True)


# ── load ──────────────────────────────────────────────────────────────────────


def load_jsonl(root: Path) -> pd.DataFrame:
    records = []
    for path in sorted(root.rglob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    if not records:
        print(f"No .jsonl files found under {root}")
        sys.exit(0)
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["date"] = df["timestamp"].dt.date
    for col in ("margin", "req", "eff_current", "eff_proj", "eff_dps", "eff_support"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "reason_tag" in df.columns:

        def _normalize_tag(t):
            if pd.isna(t):
                return t
            if t in KNOWN_TAGS:
                return t
            if re.search(r"BIG_PROC possible", str(t)):
                return "big_proc_possible"
            if re.search(r"try reach \+9|hero gate|could PASS|PASS with", str(t)):
                return "test_eff"
            return "other"

        df["reason_tag"] = df["reason_tag"].apply(_normalize_tag)
    return df


# ── helpers ───────────────────────────────────────────────────────────────────


def _keep_rate_h(df, col, ax, title):
    grp = df.groupby(col)["decision"].value_counts(normalize=True).unstack(fill_value=0)
    grp = grp.reindex(columns=["KEEP", "TEST", "SELL"], fill_value=0)
    grp = grp.sort_values("KEEP", ascending=True)
    counts = df.groupby(col)["decision"].count()
    grp.index = [f"{v}  (n={counts.get(v, 0)})" for v in grp.index]

    grp[["SELL", "TEST", "KEEP"]].plot(
        kind="barh",
        stacked=True,
        ax=ax,
        color=[COLORS["SELL"], COLORS["TEST"], COLORS["KEEP"]],
        edgecolor="none",
        width=0.7,
    )

    dec_order = ["SELL", "TEST", "KEEP"]
    for ci, bar_container in enumerate(ax.containers):
        dec = dec_order[ci] if ci < len(dec_order) else "SELL"
        txt_clr = _txt(COLORS[dec])
        for rect in bar_container:
            w = rect.get_width()
            if w > 0.02:
                ax.text(
                    rect.get_x() + w / 2,
                    rect.get_y() + rect.get_height() / 2,
                    f"{w:.0%}",
                    ha="center",
                    va="center",
                    fontsize=7.5,
                    color=txt_clr,
                    fontweight="bold",
                )

    _round_stacked(ax, horizontal=True, r_frac=0.20)
    ax.set_title(title)
    ax.set_xlabel("proportion")
    ax.set_xlim(0, 1)
    ax.set_xticks(np.arange(0, 1.01, 0.1))
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.xaxis.grid(True, alpha=0.5, linestyle="--", color=C_GRID)
    ax.yaxis.grid(False)
    ax.legend(loc="lower right")
    ax.set_ylabel("")
    ax.tick_params(axis="y", labelsize=9)


# ── individual charts ─────────────────────────────────────────────────────────


def chart_keep_rate_set(fig, df, kept):
    ax = fig.add_subplot(111)
    if "set" in df.columns:
        _keep_rate_h(df.dropna(subset=["set"]), "set", ax, "Keep rate by set")
    else:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)


def chart_keep_rate_slot(fig, df, kept):
    ax = fig.add_subplot(111)
    _keep_rate_h(
        df.dropna(subset=["slot"]).astype({"slot": int}),
        "slot",
        ax,
        "Keep rate by slot",
    )


def chart_keep_rate_rarity(fig, df, kept):
    ax = fig.add_subplot(111)
    _keep_rate_h(df.dropna(subset=["rarity"]), "rarity", ax, "Keep rate by rarity")


def chart_reasons(fig, df, kept):
    ax = fig.add_subplot(111)
    if "reason_tag" not in df.columns:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    counts = df["reason_tag"].value_counts().sort_values()
    clr = [REASON_COLORS.get(str(t), "#9CA3AF") for t in counts.index]
    bars = ax.barh(counts.index, counts.values, color=clr, edgecolor="none", height=0.6)
    total = counts.sum()
    for bar, v in zip(bars, counts.values):
        ax.text(
            v + total * 0.005,
            bar.get_y() + bar.get_height() / 2,
            f"{v}  ({v / total:.1%})",
            va="center",
            fontsize=10,
            color=C_LABEL,
        )
    ax.set_xlim(0, counts.max() * 1.25)
    ax.set_title("Decision reasons")
    ax.set_xlabel("count")
    ax.xaxis.grid(True, alpha=0.5, linestyle="--", color=C_GRID)
    ax.yaxis.grid(False)
    _round_bars(ax, horizontal=True, r_frac=0.20)


def chart_margin(fig, df, kept):
    ax = fig.add_subplot(111)
    margin_data = kept["margin"].dropna()
    if margin_data.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    ax.hist(
        margin_data,
        bins=MARGIN_BINS,
        color=COLORS["KEEP"],
        edgecolor=BG_FIG,
        linewidth=0.8,
    )
    ax.axvline(
        0,
        color="#E879F9",
        linestyle="--",
        linewidth=2,
        label="req threshold  (0 = eff exactement à la limite, normal)",
    )
    ax.axvline(
        BORDERLINE_THRESH,
        color="#F59E0B",
        linestyle=":",
        linewidth=2,
        label=f"borderline limit ({BORDERLINE_THRESH})",
    )
    ax.axvline(
        margin_data.median(),
        color="#818CF8",
        linestyle="--",
        linewidth=2,
        label=f"median  {margin_data.median():.3f}",
    )
    ax.set_title("Margin (eff − req) — kept runes")
    ax.set_xlabel("eff − req")
    ax.set_ylabel("count")
    ax.legend(fontsize=9)
    stats = (
        f"n={len(margin_data)}  |  min={margin_data.min():.3f}"
        f"  |  median={margin_data.median():.3f}  |  max={margin_data.max():.3f}"
    )
    ax.text(
        0.99,
        0.97,
        stats,
        transform=ax.transAxes,
        fontsize=9,
        ha="right",
        va="top",
        color=C_LABEL,
    )


def chart_scatter(fig, df, kept):
    ax = fig.add_subplot(111)
    scatter_df = df.dropna(subset=["eff_current", "req"])
    if scatter_df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    for dec, grp in scatter_df.groupby("decision"):
        ax.scatter(
            grp["req"],
            grp["eff_current"],
            color=COLORS.get(dec, "#A78BFA"),
            alpha=0.75,
            s=25,
            label=dec,
            edgecolors="none",
        )
    lims = [
        min(scatter_df["req"].min(), scatter_df["eff_current"].min()) - 0.01,
        max(scatter_df["req"].max(), scatter_df["eff_current"].max()) + 0.01,
    ]
    ax.plot(
        lims,
        lims,
        color="#7C3AED",
        linestyle="--",
        linewidth=1.5,
        alpha=0.9,
        label="eff = req  (diagonal)",
    )
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    step = 0.05
    ticks = np.arange(round(lims[0] / step) * step, lims[1] + step, step)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.tick_params(labelsize=8)
    ax.set_xlabel("req (threshold)")
    ax.set_ylabel("eff_current")
    ax.set_title("Eff vs req — all runes")
    ax.legend(fontsize=10)
    ax.text(
        0.02,
        0.97,
        "Above diagonal = KEEP / Below = SELL",
        transform=ax.transAxes,
        fontsize=9,
        va="top",
        color=C_LABEL,
    )


def chart_bucket(fig, df, kept):
    ax = fig.add_subplot(111)
    if "bucket" not in kept.columns:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    bucket_counts = kept["bucket"].dropna().astype(int).value_counts().sort_index()
    bars = ax.bar(
        bucket_counts.index.astype(str),
        bucket_counts.values,
        color=COLORS["KEEP"],
        edgecolor="none",
        width=0.5,
    )
    ax.set_title("Good subs bucket — kept runes")
    ax.set_xlabel("bucket (2 / 3 / 4 good subs)")
    ax.set_ylabel("count")
    ax.margins(y=0.18)
    total = bucket_counts.sum()
    for bar, v in zip(bars, bucket_counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + ax.get_ylim()[1] * 0.01,
            f"{v}\n({v / total:.0%})",
            ha="center",
            va="bottom",
            fontsize=11,
            color=C_TITLE,
        )


def chart_big_proc(fig, df, kept):
    ax = fig.add_subplot(111)
    bp_kept = (
        kept[kept["reason_tag"] == "big_proc"]
        if "reason_tag" in kept.columns
        else pd.DataFrame()
    )
    if bp_kept.empty or "big_proc_stat" not in bp_kept.columns:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    bp_counts = bp_kept["big_proc_stat"].value_counts()
    n = len(bp_counts)
    pal = (PURPLE_PALETTE * ((n // len(PURPLE_PALETTE)) + 1))[:n]
    bars = ax.bar(bp_counts.index, bp_counts.values, color=pal, edgecolor="none")
    ax.set_title("Big proc stat — kept via big proc")
    ax.set_ylabel("count")
    ax.margins(y=0.18)
    for bar, v in zip(bars, bp_counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + ax.get_ylim()[1] * 0.01,
            str(v),
            ha="center",
            va="bottom",
            fontsize=11,
            color=C_TITLE,
        )


def chart_temporal(fig, df, kept):
    ax = fig.add_subplot(111)
    if "date" not in kept.columns or kept["date"].isna().all():
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    daily = kept.groupby("date")["eff_current"].agg(["mean", "count"]).reset_index()
    ax.plot(
        daily["date"],
        daily["mean"],
        marker="o",
        color=COLORS["KEEP"],
        linewidth=2.5,
        markersize=8,
        label="avg eff kept",
        markerfacecolor=COLORS["KEEP"],
        markeredgecolor=BG_FIG,
        markeredgewidth=2,
    )
    for _, row in daily.iterrows():
        ax.annotate(
            f"{row['mean']:.3f}",
            xy=(row["date"], row["mean"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=8,
            color=COLORS["KEEP"],
        )
    ax_r = ax.twinx()
    ax_r.bar(
        daily["date"],
        daily["count"],
        alpha=0.25,
        color=COLORS["TEST"],
        width=0.6,
        label="count kept",
    )
    ax_r.set_ylabel("count kept", fontsize=10, color=C_LABEL)
    ax_r.tick_params(axis="y", labelcolor=C_LABEL)
    ax.set_title("Avg eff_current of kept runes — by day")
    ax.set_ylabel("avg eff_current")
    ax.tick_params(axis="x", rotation=30, labelsize=9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
    ax.legend(loc="upper left", fontsize=10)
    ax_r.legend(loc="upper right", fontsize=10)


_BORDERLINE_RPP = 12  # rows per page per sub-table


def chart_borderline(fig, df, kept, page=0,
                     reason_keep=None, reason_sell=None, label=""):
    """Borderline table chart.

    reason_keep / reason_sell: sets of reason_tag strings to filter each sub-table.
    label: short name shown in titles (e.g. "eff" or "big proc").
    """
    def _fmt_subs(subs_val):
        if not isinstance(subs_val, list):
            return ""
        return "  ".join(f"{s['key']}:{s['value']}" for s in subs_val)

    def _fmt_num(v, fmt=".3f"):
        try:
            if pd.isna(v):
                return ""
        except (TypeError, ValueError):
            pass
        try:
            return format(float(v), fmt)
        except (TypeError, ValueError):
            return ""

    def _build_table(ax, all_rows, title, header_color, page, n_pages):
        ax.axis("off")
        page_info = f"  (↑↓)  page {page + 1}/{n_pages}" if n_pages > 1 else ""
        ax.set_title(title + page_info, fontsize=10, color=C_TITLE, fontweight="bold", pad=18)
        if not all_rows:
            ax.text(0.5, 0.5, "No borderline runes", ha="center", va="center",
                    transform=ax.transAxes, fontsize=11, color=C_LABEL)
            return
        slice_rows = all_rows[page * _BORDERLINE_RPP : (page + 1) * _BORDERLINE_RPP]
        if not slice_rows:
            ax.text(0.5, 0.5, "–", ha="center", va="center",
                    transform=ax.transAxes, fontsize=14, color=C_LABEL)
            return
        cols = ["date", "set", "slot", "rarity", "level", "main",
                "profile", "req", "eff_current", "margin", "subs"]
        tbl = ax.table(cellText=slice_rows, colLabels=cols, bbox=[0, 0, 1, 1], cellLoc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.auto_set_column_width(list(range(len(cols))))
        for (row, col), cell in tbl.get_celld().items():
            if row == 0:
                cell.set_facecolor(header_color)
                cell.set_text_props(color="white", fontweight="bold")
            else:
                cell.set_facecolor(BG_FIG if row % 2 == 0 else BG_AX)
                cell.set_text_props(color=C_TITLE)
            cell.set_edgecolor(C_SPINE)

    df["_margin_num"] = pd.to_numeric(df["margin"], errors="coerce")
    df["_date_str"] = df["timestamp"].astype(str).str[:10] if "timestamp" in df.columns else ""

    def _filter(decision, margin_lo, margin_hi, reason_filter, ascending_margin):
        mask = (
            (df["decision"] == decision)
            & df["_margin_num"].notna()
            & (df["_margin_num"] >= margin_lo)
            & (df["_margin_num"] < margin_hi)
        )
        if reason_filter and "reason_tag" in df.columns:
            mask &= df["reason_tag"].isin(reason_filter)
        return df[mask].sort_values(
            ["_date_str", "_margin_num"], ascending=[False, ascending_margin]
        )

    bl_keep = _filter("KEEP", 0, BORDERLINE_THRESH, reason_keep, True)
    bl_sell = _filter("SELL", -BORDERLINE_THRESH, 0, reason_sell, False)

    def _to_rows(subset):
        rows = []
        for _, r in subset.iterrows():
            rows.append([
                _val(r.get("_date_str", ""))[:10],
                _val(r.get("set")),
                _slot_str(r.get("slot")),
                _val(r.get("rarity")),
                f"+{_slot_str(r.get('level'))}",
                _val(r.get("main")),
                _val(r.get("profile")),
                _fmt_num(r.get("req")),
                _fmt_num(r.get("eff_current")),
                _fmt_num(r.get("margin")),
                _fmt_subs(r.get("subs")),
            ])
        return rows

    keep_rows = _to_rows(bl_keep)
    sell_rows = _to_rows(bl_sell)
    n_pages = max(1,
        -(-len(keep_rows) // _BORDERLINE_RPP),
        -(-len(sell_rows) // _BORDERLINE_RPP),
    )
    page = max(0, min(page, n_pages - 1))

    tag = f" ({label})" if label else ""
    ax_keep = fig.add_subplot(211)
    ax_sell = fig.add_subplot(212)
    fig.subplots_adjust(hspace=0.40)
    _build_table(ax_keep, keep_rows,
                 f"Borderline KEEPS{tag} — 0 ≤ margin < {BORDERLINE_THRESH}",
                 C_TITLE, page, n_pages)
    _build_table(ax_sell, sell_rows,
                 f"Borderline SELLS{tag} — -{BORDERLINE_THRESH} ≤ margin < 0",
                 COLORS["SELL"], page, n_pages)
    return n_pages

chart_borderline._pageable = True




def chart_heatmap(fig, df, kept):
    ax = fig.add_subplot(111)
    pivot_df = df.dropna(subset=["set", "slot"]).copy()
    pivot_df["slot"] = pivot_df["slot"].astype(int)
    pivot_df["is_keep"] = (pivot_df["decision"] == "KEEP").astype(float)
    pivot = (
        pivot_df.groupby(["set", "slot"])["is_keep"].mean().unstack(fill_value=np.nan)
    )
    pivot = pivot.reindex(columns=sorted(pivot.columns))
    overall = pivot_df.groupby("set")["is_keep"].mean().sort_values()
    pivot = pivot.loc[overall.index]
    if pivot.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    _keep_cmap = mcolors.LinearSegmentedColormap.from_list(
        "keep_cmap", [COLORS["SELL"], "#F5F3FF", COLORS["KEEP"]], N=256
    )
    im = ax.imshow(
        pivot.values,
        aspect="auto",
        cmap=_keep_cmap,
        vmin=0,
        vmax=1,
        interpolation="nearest",
    )
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"slot {c}" for c in pivot.columns], fontsize=10)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    ax.set_title("Keep rate heatmap — set × slot")
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if not np.isnan(val):
                ax.text(
                    j,
                    i,
                    f"{val:.0%}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white" if (val > 0.65 or val < 0.15) else C_TITLE,
                )
    fig.colorbar(
        im,
        ax=ax,
        orientation="vertical",
        fraction=0.02,
        pad=0.02,
        format=mticker.PercentFormatter(xmax=1),
    )


def _volume_chart(ax, vol_df, freq, title):
    vol_df = vol_df.copy()
    if freq == "week":
        vol_df["week"] = pd.to_datetime(vol_df["date"]).dt.to_period("W").astype(str)
        key = "week"
    else:
        key = "date"
    grp = (
        vol_df.groupby([key, "decision"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["KEEP", "TEST", "SELL"], fill_value=0)
    )
    grp.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        color=[COLORS["KEEP"], COLORS["TEST"], COLORS["SELL"]],
        edgecolor="none",
        width=0.8,
    )
    totals_arr = grp.sum(axis=1).values
    dec_order = ["KEEP", "TEST", "SELL"]
    for ci, bar_container in enumerate(ax.containers):
        dec = dec_order[ci] if ci < len(dec_order) else "KEEP"
        txt_clr = _txt(COLORS[dec])
        for i, rect in enumerate(bar_container):
            h = rect.get_height()
            total = totals_arr[i]
            if h > 0 and total > 0 and h / total > 0.04:
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    rect.get_y() + h / 2,
                    f"{int(h)}\n({h / total:.0%})",
                    ha="center",
                    va="center",
                    fontsize=7.5,
                    color=txt_clr,
                    fontweight="bold",
                )
    totals = grp.sum(axis=1)
    max_total = totals.max()
    for i, (idx, total) in enumerate(totals.items()):
        ax.text(
            i,
            total + max_total * 0.01,
            str(int(total)),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=C_TITLE,
        )
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel("count")
    ax.margins(y=0.15)
    ax.tick_params(axis="x", rotation=30, labelsize=9)
    ax.legend(fontsize=10)


def chart_volume_day(fig, df, kept):
    ax = fig.add_subplot(111)
    vol_df = df.dropna(subset=["date"])
    if vol_df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    _volume_chart(ax, vol_df, "day", "Volume runes traitées — par jour")


def chart_volume_week(fig, df, kept):
    ax = fig.add_subplot(111)
    vol_df = df.dropna(subset=["date"])
    if vol_df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    _volume_chart(ax, vol_df, "week", "Volume runes traitées — par semaine")


_ALL_KEEPS_RPP = 30  # rows per page


def chart_all_keeps(
    fig, df, kept, page=0, reason_filter=None, label=None, show_bp_stat=True, show_reason=True
):
    ax = fig.add_subplot(111)
    ax.axis("off")

    display = kept.copy()
    if reason_filter is not None and "reason_tag" in display.columns:
        display = display[display["reason_tag"].isin(reason_filter)]

    chart_label = label or (
        "All kept runes" if reason_filter is None else ", ".join(sorted(reason_filter))
    )
    if display.empty:
        ax.set_title(chart_label, fontsize=11, color=C_TITLE, fontweight="bold", pad=18)
        ax.text(
            0.5,
            0.5,
            "No runes",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=12,
            color=C_LABEL,
        )
        return 1

    def _fmt_subs(subs_val):
        if not isinstance(subs_val, list):
            return ""
        return "  ".join(f"{s['key']}:{s['value']}" for s in subs_val)

    display["_date_str"] = (
        display["timestamp"].astype(str).str[:10]
        if "timestamp" in display.columns
        else ""
    )
    display = display.sort_values("_date_str", ascending=False)

    def _fmt_num(v, fmt=".3f"):
        try:
            if pd.isna(v):
                return ""
        except (TypeError, ValueError):
            pass
        try:
            return format(float(v), fmt)
        except (TypeError, ValueError):
            return ""

    cols = ["date", "set", "slot", "rarity", "level", "main",
            "profile", "req", "eff_current", "margin", "reason", "big_proc_stat", "subs"]
    if not show_bp_stat:
        cols = [c for c in cols if c != "big_proc_stat"]
    if not show_reason:
        cols = [c for c in cols if c != "reason"]
    all_rows = []
    for _, r in display.iterrows():
        row = [
            _val(r.get("_date_str", ""))[:10],
            _val(r.get("set")),
            _slot_str(r.get("slot")),
            _val(r.get("rarity")),
            f"+{_slot_str(r.get('level'))}",
            _val(r.get("main")),
            _val(r.get("profile")),
            _fmt_num(r.get("req")),
            _fmt_num(r.get("eff_current")),
            _fmt_num(r.get("margin")),
            _val(r.get("reason_tag")),
            _val(r.get("big_proc_stat")),
            _fmt_subs(r.get("subs")),
        ]
        if not show_bp_stat:
            row = row[:11] + row[12:]
        if not show_reason:
            row = row[:10] + row[11:]
        all_rows.append(row)

    n_pages = max(1, -(-len(all_rows) // _ALL_KEEPS_RPP))
    page = max(0, min(page, n_pages - 1))
    page_rows = all_rows[page * _ALL_KEEPS_RPP : (page + 1) * _ALL_KEEPS_RPP]

    page_info = f"  (↑↓)  page {page + 1}/{n_pages}" if n_pages > 1 else ""
    ax.set_title(
        f"{chart_label} — most recent first{page_info}",
        fontsize=11,
        color=C_TITLE,
        fontweight="bold",
        pad=18,
    )

    tbl = ax.table(
        cellText=page_rows, colLabels=cols, bbox=[0, 0, 1, 1], cellLoc="center"
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.auto_set_column_width(list(range(len(cols))))
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_facecolor(C_TITLE)
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor(BG_FIG if row % 2 == 0 else BG_AX)
            cell.set_text_props(color=C_TITLE)
        cell.set_edgecolor(C_SPINE)
    return n_pages


chart_all_keeps._pageable = True


def chart_keeps_bigproc(fig, df, kept, page=0):
    return chart_all_keeps(
        fig,
        df,
        kept,
        page=page,
        reason_filter={"big_proc", "big_proc_possible"},
        label="Big proc keeps",
        show_reason=False,
    )


chart_keeps_bigproc._pageable = True


def chart_keeps_eff(fig, df, kept, page=0):
    return chart_all_keeps(
        fig,
        df,
        kept,
        page=page,
        reason_filter={"eff"},
        label="Eff keeps",
        show_bp_stat=False,
        show_reason=False,
    )


chart_keeps_eff._pageable = True


CHARTS = [
    ("All kept runes", chart_all_keeps),
    ("Big proc keeps", chart_keeps_bigproc),
    ("Eff keeps", chart_keeps_eff),
    ("Borderline keeps",     chart_borderline),
    ("Keep rate by set", chart_keep_rate_set),
    ("Keep rate by slot", chart_keep_rate_slot),
    ("Keep rate by rarity", chart_keep_rate_rarity),
    ("Decision reasons", chart_reasons),
    ("Margin distribution", chart_margin),
    ("Eff vs req scatter", chart_scatter),
    ("Bucket distribution", chart_bucket),
    ("Big proc stats", chart_big_proc),
    ("Temporal evolution", chart_temporal),
    ("Heatmap set × slot", chart_heatmap),
    ("Volume by day", chart_volume_day),
    ("Volume by week", chart_volume_week),
]

# ── navigator ─────────────────────────────────────────────────────────────────


def _make_subtitle(df: pd.DataFrame, date_filter: "str | None" = None) -> str:
    n_total = len(df)
    if n_total == 0:
        return "0 runes"
    n_keep = (df["decision"] == "KEEP").sum()
    n_sell = (df["decision"] == "SELL").sum()
    n_test = (df["decision"] == "TEST").sum()
    base = (
        f"{n_total} runes  |  KEEP {n_keep} ({n_keep / n_total:.0%})  "
        f"SELL {n_sell} ({n_sell / n_total:.0%})  TEST {n_test} ({n_test / n_total:.0%})"
    )
    if date_filter:
        return f"{date_filter}  —  {base}"
    return base


class Navigator:
    def __init__(self, df: pd.DataFrame, date_filter: "str | None" = None):
        self.df = df
        self.kept = df[df["decision"] == "KEEP"]
        self.idx = 0
        self.page = 0
        self.max_page = 0
        self.n = len(CHARTS)
        self.subtitle = _make_subtitle(df, date_filter)
        self.fig = plt.figure(figsize=(14, 8), facecolor=BG_FIG)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self._draw()
        plt.show()

    def _on_key(self, event):
        if event.key in ("right", "d"):
            self.idx = (self.idx + 1) % self.n
            self.page = 0
            self._draw()
        elif event.key in ("left", "a"):
            self.idx = (self.idx - 1) % self.n
            self.page = 0
            self._draw()
        elif event.key == "down" and self.page < self.max_page:
            self.page += 1
            self._draw()
        elif event.key == "up" and self.page > 0:
            self.page -= 1
            self._draw()
        elif event.key in ("q", "escape"):
            plt.close(self.fig)

    def _draw(self):
        self.fig.clear()
        title, fn = CHARTS[self.idx]
        nav_hint = (
            "← → navigate  |  ↑↓ scroll"
            if getattr(fn, "_pageable", False)
            else "← → navigate"
        )
        self.fig.suptitle(
            f"{title}   [{self.idx + 1} / {self.n}]  —  {nav_hint}  |  Q to quit\n{self.subtitle}",
            fontsize=11,
            y=0.98,
            color=C_TITLE,
            fontweight="bold",
        )
        if getattr(fn, "_pageable", False):
            n_pages = fn(self.fig, self.df, self.kept, page=self.page) or 1
            self.max_page = n_pages - 1
        else:
            fn(self.fig, self.df, self.kept)
            self.max_page = 0
        self.fig.tight_layout(rect=[0, 0, 1, 0.90])
        self.fig.canvas.draw()


# ── save to PDF ───────────────────────────────────────────────────────────────


def save_pdf(
    df: pd.DataFrame, save_path: Path, date_filter: "str | None" = None
) -> None:
    kept = df[df["decision"] == "KEEP"]
    subtitle = _make_subtitle(df, date_filter)
    n_saved = 0
    with PdfPages(save_path) as pdf:
        for title, fn in CHARTS:
            if getattr(fn, "_pageable", False):
                page = 0
                while True:
                    fig = plt.figure(figsize=(14, 8), facecolor=BG_FIG)
                    fig.suptitle(
                        f"{title}\n{subtitle}",
                        fontsize=11,
                        y=0.98,
                        color=C_TITLE,
                        fontweight="bold",
                    )
                    n_pages = fn(fig, df, kept, page=page) or 1
                    fig.tight_layout(rect=[0, 0, 1, 0.93])
                    pdf.savefig(fig)
                    plt.close(fig)
                    n_saved += 1
                    if page >= n_pages - 1:
                        break
                    page += 1
            else:
                fig = plt.figure(figsize=(14, 8), facecolor=BG_FIG)
                fig.suptitle(
                    f"{title}\n{subtitle}",
                    fontsize=11,
                    y=0.98,
                    color=C_TITLE,
                    fontweight="bold",
                )
                fn(fig, df, kept)
                fig.tight_layout(rect=[0, 0, 1, 0.93])
                pdf.savefig(fig)
                plt.close(fig)
                n_saved += 1
    print(f"Saved {n_saved} pages to {save_path}")


# ── entry point ───────────────────────────────────────────────────────────────


if __name__ == "__main__":
    _setup_style()
    args = sys.argv[1:]
    save_path = None
    root = RUNES_ROOT
    date_filter: str | None = None

    i = 0
    while i < len(args):
        if args[i] == "--save" and i + 1 < len(args):
            save_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--today":
            date_filter = _dt.date.today().isoformat()
            i += 1
        elif args[i] == "--date" and i + 1 < len(args):
            date_filter = args[i + 1]
            i += 2
        else:
            root = Path(args[i])
            i += 1

    df = load_jsonl(root)
    df = _dedup_runes(df)
    print(f"Loaded {len(df)} unique runes from {root}")

    if date_filter:
        if "timestamp" in df.columns:
            mask = df["timestamp"].astype(str).str[:10] == date_filter
            df = df[mask].copy()
        print(f"Filtered to {date_filter}: {len(df)} records")
        if df.empty:
            print("No records for this date.")
            sys.exit(0)

    if save_path:
        save_pdf(df, save_path, date_filter)
    else:
        print("← → (ou A / D) pour naviguer  |  Q pour quitter")
        Navigator(df, date_filter)
