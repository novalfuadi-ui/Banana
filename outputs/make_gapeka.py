#!/usr/bin/env python3
"""
GAPEKA (Grafik Perjalanan Kereta Api) - Lintas Tabang - Marang Kayu
KA Khusus Logistik Batubara PT Bayan Resources Tbk (Tahap 1, 165 km).
Dibuat untuk dua skenario: 70 MTPA (headway 45') dan 80 MTPA (headway 40').

Data bersumber dari Bab VI Analisis Operasi KA (Draft Akhir, 01-06-2026):
  - Stasiun & posisi KM (Tabel 6.3-1 / 6.11)
  - Kecepatan: Vmax 60 km/jam, Vops rata-rata 55 km/jam (Tabel 6.10)
  - Kelandaian maksimum 0,6% (6 permil) (Tabel 6.10) -> profil per-petak indikatif
  - Waktu tempuh 180 menit/arah; headway 45'/40', frekuensi 24/28 trip (Tabel 6.5/6.7)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator
import matplotlib.patches as mpatches

# ----------------------------------------------------------------------------
# DATA OPERASI
# ----------------------------------------------------------------------------
STATIONS = [
    ("Tabang\n(Hulu - St. Muat)",        165, "terminal"),
    ("St. Antara 3",                      132, "antara"),
    ("St. Antara 2\n(tengah lintas)",      99, "antara"),
    ("St. Antara 1",                       66, "antara"),
    ("Marang Kayu\n(Hilir - St. Bongkar)",  0, "terminal"),
]
YMIN, YMAX = 0, 165

# Petak jalan (arah bermuatan hulu->hilir): km_atas, km_bawah, jarak, Vmax, Vops, gradien_permil
SEGMENTS = [
    (165, 132, 33, 60, 55, 6.0),
    (132,  99, 33, 60, 55, 4.0),
    ( 99,  66, 33, 60, 55, 5.0),
    ( 66,   0, 66, 60, 55, 3.0),
]
VOPS = 55.0
def seg_minutes(d): return d / VOPS * 60.0

# Skenario
SCENARIOS = {
    "70": dict(headway=45, freq=24, label="70 MTPA", file="gapeka_70mtpa.png"),
    "80": dict(headway=40, freq=28, label="80 MTPA", file="gapeka_80mtpa.png"),
}

T_START, T_END = 0, 24 * 60   # 00:00 - 24:00


def path_loaded(dep):
    pts, t = [(dep, 165)], dep
    for k_top, k_bot, dist, *_ in SEGMENTS:
        t += seg_minutes(dist); pts.append((t, k_bot))
    return pts

def path_empty(dep):
    pts, t = [(dep, 0)], dep
    for k_top, k_bot, dist, *_ in reversed(SEGMENTS):
        t += seg_minutes(dist); pts.append((t, k_top))
    return pts

def hhmm(m): return f"{int(m)//60:02d}:{int(m)%60:02d}"


def build(scn, annotate_all=False, dpi=150, figsize=(22, 11.5)):
    headway, freq, label, fname = scn["headway"], scn["freq"], scn["label"], scn["file"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig = plt.figure(figsize=figsize, dpi=dpi)
    gs = GridSpec(1, 5, figure=fig,
                  width_ratios=[1.9, 0.6, 0.85, 0.85, 0.95],
                  wspace=0.06, left=0.004, right=0.215, top=0.90, bottom=0.07)
    ax_name = fig.add_subplot(gs[0, 0])
    ax_km   = fig.add_subplot(gs[0, 1], sharey=ax_name)
    ax_vmax = fig.add_subplot(gs[0, 2], sharey=ax_name)
    ax_vops = fig.add_subplot(gs[0, 3], sharey=ax_name)
    ax_grad = fig.add_subplot(gs[0, 4], sharey=ax_name)
    ax_main = fig.add_axes([0.235, 0.07, 0.755, 0.83], sharey=ax_name)

    for ax in (ax_name, ax_km, ax_vmax, ax_vops, ax_grad, ax_main):
        ax.set_ylim(YMIN - 4, YMAX + 4)

    def station_lines(ax, lw_major=1.3):
        for name, km, typ in STATIONS:
            ax.axhline(km, color=("#222" if typ == "terminal" else "#9a9a9a"),
                       lw=(lw_major if typ == "terminal" else 0.9),
                       ls=("-" if typ == "terminal" else "--"), zorder=1)

    # Kolom 1: nama
    ax_name.set_xlim(0, 1); station_lines(ax_name)
    for name, km, typ in STATIONS:
        ax_name.text(0.97, km, name, ha="right", va="center", fontsize=14,
                     fontweight=("bold" if typ == "terminal" else "normal"),
                     color=("#062c5c" if typ == "terminal" else "#333"))
    ax_name.set_title("STASIUN", fontsize=13, fontweight="bold", pad=8)

    # Kolom 2: KM
    ax_km.set_xlim(0, 1); station_lines(ax_km)
    for name, km, typ in STATIONS:
        ax_km.text(0.5, km, f"KM {km:g}", ha="center", va="center", fontsize=13, color="#444")
    ax_km.set_title("POSISI", fontsize=13, fontweight="bold", pad=8)

    for ax in (ax_name, ax_km):
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_visible(False)

    def profile(ax, values, lim, color, fill, unit, title, fmt="{:g}"):
        ax.set_xlim(0, lim); station_lines(ax, 1.0)
        for (kt, kb, d, vmax, vops, g), val in zip(SEGMENTS, values):
            ax.barh((kt + kb) / 2, val, height=abs(kt - kb) - 1.2,
                    color=fill, edgecolor=color, lw=1.2, zorder=2)
            ax.text(val * 0.5, (kt + kb) / 2, fmt.format(val), ha="center", va="center",
                    fontsize=14, fontweight="bold", color=color, zorder=3)
        ax.set_title(title, fontsize=13, fontweight="bold", pad=8)
        ax.set_xlabel(unit, fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_color("#ccc")

    profile(ax_vmax, [s[3] for s in SEGMENTS], 70, "#9c1006", "#f4c9c2", "km/jam", "V-MAX")
    profile(ax_vops, [s[4] for s in SEGMENTS], 70, "#0a5c2c", "#bfe6cd", "km/jam", "V-OPS")
    profile(ax_grad, [s[5] for s in SEGMENTS], 8, "#7a4b00", "#f3dfb0", "permil (‰)",
            "GRADIEN", fmt="{:.0f}‰")
    ax_grad.text(0.5, -10, "turun arah hilir\n(maks 0,6%)", ha="center", va="top",
                 fontsize=9.5, style="italic", color="#7a4b00")

    # PANEL UTAMA
    station_lines(ax_main)
    ax_main.set_xlim(T_START, T_END)
    xt = list(range(0, T_END + 1, 60))
    ax_main.set_xticks(xt)
    ax_main.set_xticklabels([hhmm(t) for t in xt], fontsize=11, rotation=0)
    ax_main.xaxis.set_minor_locator(MultipleLocator(30))
    ax_main.grid(which="major", axis="x", color="#cfe0f0", lw=0.8, zorder=0)
    ax_main.grid(which="minor", axis="x", color="#eef3f8", lw=0.5, zorder=0)
    ax_main.set_xlabel("WAKTU (kedatangan / keberangkatan tiap stasiun) — 00:00 s.d. 24:00",
                       fontsize=13, fontweight="bold")
    ax_main.set_title(f"GRAFIK PERJALANAN KERETA API — {freq} trip/hari, headway {headway} menit",
                      fontsize=13, fontweight="bold", pad=8, loc="left")
    ax_main.tick_params(axis="y", left=False, labelleft=False)

    lw_l, lw_e = (1.2, 1.0) if annotate_all else (1.7, 1.3)
    lab_fs = 7.5 if annotate_all else 7.6
    DAY = 24 * 60  # batas 24:00; perjalanan yang melewatinya dibungkus (wrap) ke 00:00

    def draw_path(pts, color, lw, ls, lab_color=None, dy=0, zorder=4):
        kw = dict(color=color, lw=lw, ls=ls, zorder=zorder)
        if ls == "-":
            kw["solid_capstyle"] = "round"
        # gambar tiap petak; bagi di batas 24:00 lalu lanjutkan di sisi kiri (t-DAY)
        for (t0, k0), (t1, k1) in zip(pts, pts[1:]):
            if t1 <= DAY:
                ax_main.plot([t0, t1], [k0, k1], **kw)
            elif t0 >= DAY:
                ax_main.plot([t0 - DAY, t1 - DAY], [k0, k1], **kw)
            else:
                f = (DAY - t0) / (t1 - t0); kb = k0 + f * (k1 - k0)
                ax_main.plot([t0, DAY], [k0, kb], **kw)
                ax_main.plot([0, t1 - DAY], [kb, k1], **kw)
        if lab_color is not None:
            for (t, km) in pts:
                x = t if t <= DAY else t - DAY
                ax_main.plot(x, km, "o", ms=3.2, color=lab_color, mec="white", mew=0.5, zorder=6)
                ax_main.annotate(hhmm(t % DAY), (x, km), textcoords="offset points",
                                 xytext=(0, dy), ha="center", fontsize=lab_fs,
                                 color=lab_color, zorder=7, fontweight="bold", clip_on=True)

    # Sesi operasi 06:00-24:00 (mulai pukul 06:00 per dokumen); 00:00-06:00 = window perawatan
    OP_START = 6 * 60

    # KA bermuatan (Tabang -> MK), berangkat tiap headway sejumlah frekuensi
    for i in range(freq):
        pts = path_loaded(OP_START + i * headway)
        draw_path(pts, "#c1121f", lw_l, "-",
                  lab_color=("#9c1006" if annotate_all else None), dy=6, zorder=4)
    # KA kosong (MK -> Tabang)
    for i in range(freq):
        pts = path_empty(OP_START + i * headway + headway / 2)
        draw_path(pts, "#1d4e89", lw_e, (0, (6, 4)),
                  lab_color=("#123a66" if annotate_all else None), dy=-13, zorder=3)

    if not annotate_all:
        # KA referensi (Tabang dep 06:00) + anotasi waktu tiap stasiun
        ref = path_loaded(OP_START)
        for (t, km), (name, _, typ) in zip(ref, STATIONS):
            lab = "ber." if km == 165 else ("tiba" if km == 0 else "lewat")
            ax_main.plot(t, km, "o", ms=6, color="#c1121f", mec="white", mew=1.0, zorder=6)
            ax_main.annotate(f"{hhmm(t)}\n({lab})", (t, km), textcoords="offset points",
                             xytext=(7, 9 if km != 0 else -24), fontsize=7.6, fontweight="bold",
                             color="#7a0a13", zorder=7,
                             bbox=dict(boxstyle="round,pad=0.18", fc="#fff3f3", ec="#c1121f", lw=0.6))

    # window perawatan = area yang BENAR-BENAR tanpa kereta, yaitu celah menyerong antara
    # KA terakhir siklus sebelumnya (yang dibungkus dari 24:00) dan KA pertama pukul 06:00.
    TT = sum(seg_minutes(s[2]) for s in SEGMENTS)   # 180 menit/arah
    slope = TT / 165.0
    LD = OP_START + (freq - 1) * headway             # keberangkatan terakhir (24:00)
    def loaded_left(km):  return (LD - DAY) + (165 - km) * slope
    def loaded_right(km): return OP_START + (165 - km) * slope
    def empty_left(km):   return (LD + headway / 2 - DAY) + km * slope
    def empty_right(km):  return (OP_START + headway / 2) + km * slope
    kms = [k for k in range(0, 166, 2)]
    Lb = [max(loaded_left(k), empty_left(k)) for k in kms]
    Rb = [min(loaded_right(k), empty_right(k)) for k in kms]
    ax_main.fill_betweenx(kms, Lb, Rb, color="#e6e6e6", lw=0, zorder=0)
    # label di tengah area perawatan
    cx = (max(loaded_left(82), empty_left(82)) + min(loaded_right(82), empty_right(82))) / 2
    ax_main.text(cx, 82, "jendela perawatan\n(window time)\n00:00–06:00",
                 ha="center", va="center", fontsize=11, color="#777", style="italic", zorder=8,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#bbb", alpha=0.85))

    leg = [mpatches.Patch(color="#c1121f", label="KA Bermuatan (Tabang → Marang Kayu)"),
           mpatches.Patch(color="#1d4e89", label="KA Kosong (Marang Kayu → Tabang)")]
    # legenda diletakkan di ATAS grafik (di luar area data) agar tidak menimpa garis
    ax_main.legend(handles=leg, loc="lower right", bbox_to_anchor=(1.0, 1.005),
                   ncol=2, fontsize=12, framealpha=1.0, borderaxespad=0.0,
                   columnspacing=1.6, handlelength=1.6)

    fig.suptitle(
        f"GRAFIK PERJALANAN KERETA API (GAPEKA)  —  Lintas Tabang – Marang Kayu (165 km, Jalur Ganda)\n"
        f"KA Khusus Logistik Batubara PT Bayan Resources Tbk  •  Skenario {label} "
        f"(headway {headway} menit, {freq} trip/hari, waktu tempuh 180 menit/arah)",
        fontsize=18, fontweight="bold", y=0.975)
    fig.text(0.004, 0.012,
             "Sumber: Bab VI Analisis Operasi KA (Draft Akhir 01-06-2026), Tabel 6.3-1, 6.5, 6.7, 6.10, 6.11; profil gradien per-petak indikatif (maks 0,6%).",
             fontsize=9.5, style="italic", color="#666")

    fig.savefig(f"outputs/{fname}", dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("Saved: outputs/" + fname)


# 80 MTPA: anotasi waktu di tiap stasiun untuk setiap perjalanan + resolusi tinggi
build(SCENARIOS["80"], annotate_all=True, dpi=300, figsize=(40, 16))
