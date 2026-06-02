#!/usr/bin/env python3
"""
GAPEKA (Grafik Perjalanan Kereta Api) - Lintas Tabang - Marang Kayu
KA Khusus Logistik Batubara PT Bayan Resources Tbk (Tahap 1, 165 km)
Skenario 70 MTPA (headway 45 menit).

Data bersumber dari Bab VI Analisis Operasi KA (Draft Akhir, 01-06-2026):
  - Stasiun & posisi KM (Tabel 6.3-1 / 6.11)
  - Kecepatan: Vmax 60 km/jam, Vops rata-rata 55 km/jam (Tabel 6.10)
  - Kelandaian maksimum 0,6% (6 permil) (Tabel 6.10) -> profil per-petak indikatif
  - Waktu tempuh 180 menit/arah, headway 45 menit (Tabel 6.5 / 6.7)
  - Emplasemen Stasiun Antara: 4 jalur + wesel kedua ujung (6.6.2.3)
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
# Posisi KM diukur dari Marang Kayu (KM 0). Tabang di hulu (KM 165).
STATIONS = [
    # nama,            km,   tipe
    ("Tabang\n(Hulu - St. Muat)",        165, "terminal"),
    ("St. Antara 3",                      132, "antara"),
    ("St. Antara 2\n(tengah lintas)",      99, "antara"),
    ("St. Antara 1",                       66, "antara"),
    ("Marang Kayu\n(Hilir - St. Bongkar)",  0, "terminal"),
]
KM = {s[0]: s[1] for s in STATIONS}
NAMES = [s[0] for s in STATIONS]
YMIN, YMAX = 0, 165

# Petak jalan (antar-stasiun), arah bermuatan hulu->hilir (Tabang -> MK)
# (km_atas, km_bawah, jarak, Vmax, Vops, gradien_permil_turun)
SEGMENTS = [
    (165, 132, 33, 60, 55, 6.0),  # Tabang  - Antara 3
    (132,  99, 33, 60, 55, 4.0),  # Antara 3 - Antara 2
    ( 99,  66, 33, 60, 55, 5.0),  # Antara 2 - Antara 1
    ( 66,   0, 66, 60, 55, 3.0),  # Antara 1 - Marang Kayu
]

# Jadwal: kecepatan operasi 55 km/jam -> total 180 menit / arah
VOPS = 55.0
def seg_minutes(dist_km):
    return dist_km / VOPS * 60.0

HEADWAY = 45          # menit (skenario 70 MTPA)
T_START = 5 * 60      # mulai jendela tampilan 05:00 (menit sejak 00:00)
T_END   = 11 * 60     # 11:00
N_TRAINS = 8          # jumlah path tiap arah dalam jendela

# ----------------------------------------------------------------------------
# FIGURE LAYOUT
# ----------------------------------------------------------------------------
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
fig = plt.figure(figsize=(20, 11.5), dpi=150)
gs = GridSpec(
    1, 6, figure=fig,
    width_ratios=[2.4, 0.7, 0.95, 0.95, 1.05, 11.0],
    wspace=0.06, left=0.005, right=0.985, top=0.90, bottom=0.07,
)
ax_name = fig.add_subplot(gs[0, 0])
ax_km   = fig.add_subplot(gs[0, 1], sharey=ax_name)
ax_vmax = fig.add_subplot(gs[0, 2], sharey=ax_name)
ax_vops = fig.add_subplot(gs[0, 3], sharey=ax_name)
ax_grad = fig.add_subplot(gs[0, 4], sharey=ax_name)
ax_main = fig.add_subplot(gs[0, 5], sharey=ax_name)

for ax in (ax_name, ax_km, ax_vmax, ax_vops, ax_grad, ax_main):
    ax.set_ylim(YMIN - 4, YMAX + 4)

# Garis horizontal stasiun di seluruh panel kiri + main
def station_lines(ax, lw_major=1.3):
    for name, km, typ in STATIONS:
        ax.axhline(km, color=("#222222" if typ == "terminal" else "#9a9a9a"),
                   lw=(lw_major if typ == "terminal" else 0.9),
                   ls=("-" if typ == "terminal" else "--"), zorder=1)

# ---- Kolom 1: Nama stasiun -------------------------------------------------
ax_name.set_xlim(0, 1)
station_lines(ax_name)
for name, km, typ in STATIONS:
    ax_name.text(0.97, km, name, ha="right", va="center",
                 fontsize=10, fontweight=("bold" if typ == "terminal" else "normal"),
                 color=("#062c5c" if typ == "terminal" else "#333333"))
ax_name.set_title("STASIUN", fontsize=9, fontweight="bold", pad=8)
ax_name.set_xticks([]); ax_name.set_yticks([])
for sp in ax_name.spines.values():
    sp.set_visible(False)

# ---- Kolom 2: KM -----------------------------------------------------------
ax_km.set_xlim(0, 1)
station_lines(ax_km)
for name, km, typ in STATIONS:
    ax_km.text(0.5, km, f"KM {km:g}", ha="center", va="center", fontsize=8.5,
               color="#444")
ax_km.set_title("POSISI", fontsize=9, fontweight="bold", pad=8)
ax_km.set_xticks([]); ax_km.set_yticks([])
for sp in ax_km.spines.values():
    sp.set_visible(False)

# ---- Helper untuk panel profil per-petak (step horizontal) -----------------
def profile_panel(ax, values, vmaxlim, color, fill, unit, title, fmt="{:g}"):
    ax.set_xlim(0, vmaxlim)
    station_lines(ax, lw_major=1.0)
    for (k_top, k_bot, dist, vmax, vops, grad), val in zip(SEGMENTS, values):
        ax.barh(y=(k_top + k_bot) / 2, width=val, height=abs(k_top - k_bot) - 1.2,
                color=fill, edgecolor=color, lw=1.2, align="center", zorder=2)
        ax.text(val * 0.5, (k_top + k_bot) / 2, fmt.format(val),
                ha="center", va="center", fontsize=9, fontweight="bold",
                color=color, zorder=3)
    ax.set_title(title, fontsize=9, fontweight="bold", pad=8)
    ax.set_xlabel(unit, fontsize=7.5)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#cccccc")

# ---- Kolom 3: Vmax ---------------------------------------------------------
profile_panel(ax_vmax, [s[3] for s in SEGMENTS], 70, "#9c1006", "#f4c9c2",
              "km/jam", "V-MAX")
# ---- Kolom 4: Vops ---------------------------------------------------------
profile_panel(ax_vops, [s[4] for s in SEGMENTS], 70, "#0a5c2c", "#bfe6cd",
              "km/jam", "V-OPS")
# ---- Kolom 5: Gradien ------------------------------------------------------
profile_panel(ax_grad, [s[5] for s in SEGMENTS], 8, "#7a4b00", "#f3dfb0",
              "permil (‰)", "GRADIEN", fmt="{:.0f}‰")
ax_grad.text(0.5, -10, "turun arah hilir\n(maks 0,6%)", transform=ax_grad.transData,
             ha="center", va="top", fontsize=6.8, style="italic", color="#7a4b00")

# ----------------------------------------------------------------------------
# PANEL UTAMA: GRAFIK PERJALANAN (time-distance string lines)
# ----------------------------------------------------------------------------
station_lines(ax_main)
ax_main.set_xlim(T_START, T_END)

# sumbu waktu
def hhmm(m):
    return f"{int(m)//60:02d}:{int(m)%60:02d}"
xt = list(range(T_START, T_END + 1, 30))
ax_main.set_xticks(xt)
ax_main.set_xticklabels([hhmm(t) for t in xt], fontsize=8)
ax_main.xaxis.set_minor_locator(MultipleLocator(15))
ax_main.grid(which="major", axis="x", color="#cfe0f0", lw=0.8, zorder=0)
ax_main.grid(which="minor", axis="x", color="#e9f0f7", lw=0.5, zorder=0)
ax_main.set_xlabel("WAKTU (kedatangan / keberangkatan tiap stasiun)",
                   fontsize=10, fontweight="bold")
ax_main.set_title("GRAFIK PERJALANAN KERETA API", fontsize=10, fontweight="bold", pad=8)
ax_main.tick_params(axis="y", left=False, labelleft=False)

# bangun titik (waktu, km) sebuah KA dari satu ujung
def path_loaded(dep_tabang):
    """Tabang(165)->MK(0). Mengembalikan list (t,km)."""
    pts = [(dep_tabang, 165)]
    t = dep_tabang
    for k_top, k_bot, dist, *_ in SEGMENTS:
        t += seg_minutes(dist)
        pts.append((t, k_bot))
    return pts

def path_empty(dep_mk):
    """MK(0)->Tabang(165)."""
    pts = [(dep_mk, 0)]
    t = dep_mk
    for k_top, k_bot, dist, *_ in reversed(SEGMENTS):
        t += seg_minutes(dist)
        pts.append((t, k_top))
    return pts

# KA bermuatan (merah, garis tebal solid), berangkat Tabang tiap headway
for i in range(N_TRAINS):
    dep = T_START - 60 + i * HEADWAY
    pts = path_loaded(dep)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ax_main.plot(xs, ys, color="#c1121f", lw=2.0, solid_capstyle="round", zorder=4)

# KA kosong (biru, garis putus-putus), berangkat Marang Kayu tiap headway
for i in range(N_TRAINS):
    dep = T_START - 60 + i * HEADWAY + 22  # offset agar tidak bertumpuk
    pts = path_empty(dep)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ax_main.plot(xs, ys, color="#1d4e89", lw=1.6, ls=(0, (6, 4)), zorder=3)

# --- KA referensi (Tabang dep 06:00) + anotasi waktu di tiap stasiun --------
ref_dep = 6 * 60
ref = path_loaded(ref_dep)
for (t, km), (name, _, typ) in zip(ref, STATIONS):
    label = "ber." if typ == "terminal" and km == 165 else ("tiba" if km == 0 else "lewat")
    ax_main.plot(t, km, "o", ms=6, color="#c1121f", mec="white", mew=1.0, zorder=6)
    ax_main.annotate(f"{hhmm(t)}\n({label})", (t, km),
                     textcoords="offset points", xytext=(7, 8 if km not in (0,) else -22),
                     fontsize=7.8, fontweight="bold", color="#7a0a13", zorder=7,
                     bbox=dict(boxstyle="round,pad=0.18", fc="#fff3f3", ec="#c1121f", lw=0.6))

# legenda
leg = [
    mpatches.Patch(color="#c1121f", label="KA Bermuatan (Tabang → Marang Kayu)"),
    mpatches.Patch(color="#1d4e89", label="KA Kosong (Marang Kayu → Tabang)"),
]
ax_main.legend(handles=leg, loc="upper right", fontsize=8.5, framealpha=0.95)

# anotasi headway & waktu tempuh
ax_main.annotate("", xy=(T_START - 60 + 60, 168), xytext=(T_START - 60 + 60 + HEADWAY, 168),
                 arrowprops=dict(arrowstyle="<->", color="#555"), zorder=8)
ax_main.text(T_START - 60 + 60 + HEADWAY/2, 171, f"headway {HEADWAY} mnt",
             ha="center", fontsize=8, color="#555")

# ----------------------------------------------------------------------------
# INSET (sisi kanan-bawah panel utama): EMPLASEMEN STASIUN ANTARA (4 jalur)
# ----------------------------------------------------------------------------
ax_emp = fig.add_axes([0.74, 0.085, 0.235, 0.235])
ax_emp.set_xlim(0, 10); ax_emp.set_ylim(0, 6)
ax_emp.set_title("EMPLASEMEN STASIUN ANTARA (Stasiun Kecil)",
                 fontsize=8.5, fontweight="bold")
ax_emp.axis("off")
ax_emp.add_patch(mpatches.FancyBboxPatch((0.05, 0.05), 9.9, 5.9,
                 boxstyle="round,pad=0.02", fc="#fbfbf5", ec="#888", lw=1.0))

# 4 jalur lurus: 1 & 4 = jalur raya (sepur lurus), 2 & 3 = sepur belok (penyusulan/persilangan)
track_y = {1: 1.2, 2: 2.4, 3: 3.6, 4: 4.8}
xL, xR = 1.6, 8.4
for j, y in track_y.items():
    main = j in (1, 4)
    ax_emp.plot([xL, xR], [y, y], color=("#111" if main else "#1d4e89"),
                lw=(2.4 if main else 1.8), zorder=3,
                ls=("-" if main else "-"))
    ax_emp.text(xL - 0.15, y, f"{j}", ha="right", va="center", fontsize=8,
                fontweight="bold")
# leher/ujung jalur + wesel (turnouts) ke jalur raya di kedua ujung
for xend, xin in ((xL, xL + 1.0), (xR, xR - 1.0)):
    ax_emp.plot([xend - 0.0 if xend == xL else xend, xin], [track_y[1], track_y[1]],
                color="#111", lw=2.4)
    # konvergensi sepur belok ke jalur raya (wesel sederhana)
    for j in (2, 3):
        ax_emp.plot([xin, xin + (0.7 if xend == xL else -0.7)],
                    [track_y[1], track_y[j]], color="#1d4e89", lw=1.5, zorder=2)
    for j in (4, 3, 2):
        pass
# tanda wesel
for wx in (xL + 1.0, xR - 1.0):
    ax_emp.plot(wx, track_y[1], "s", ms=5, color="#b8860b", zorder=5)
    ax_emp.plot(wx, track_y[4], "s", ms=5, color="#b8860b", zorder=5)
# sambungan jalur 4 (raya kedua)
for xend, xin in ((xL, xL + 1.0), (xR, xR - 1.0)):
    ax_emp.plot([xin, xin + (0.7 if xend == xL else -0.7)],
                [track_y[4], track_y[3]], color="#1d4e89", lw=1.5, zorder=2)

# sinyal masuk (lingkaran) di kedua ujung
for sx in (xL - 0.0, xR + 0.0):
    ax_emp.plot(sx, 5.5, "o", ms=6, mfc="#cc0000", mec="#111", zorder=6)
ax_emp.text(xL, 5.5, "  sinyal masuk", fontsize=6.5, va="center")

ax_emp.text(5.0, 0.35,
            "4 jalur • jalur 1&4 = sepur raya (hilir/udik) • jalur 2&3 = sepur belok\n"
            "wesel (■) di kedua ujung untuk penyusulan/persilangan saat gangguan",
            ha="center", va="bottom", fontsize=6.6, color="#333")

# ----------------------------------------------------------------------------
# JUDUL UTAMA
# ----------------------------------------------------------------------------
fig.suptitle(
    "GRAFIK PERJALANAN KERETA API (GAPEKA)  —  Lintas Tabang – Marang Kayu (165 km, Jalur Ganda)\n"
    "KA Khusus Logistik Batubara PT Bayan Resources Tbk  •  Skenario 70 MTPA (headway 45 menit, waktu tempuh 180 menit/arah)",
    fontsize=14, fontweight="bold", y=0.975)

fig.text(0.006, 0.012,
         "Sumber data: Bab VI Analisis Operasi KA (Draft Akhir 01-06-2026), Tabel 6.3-1, 6.5, 6.7, 6.10, 6.11; profil gradien per-petak bersifat indikatif (maks 0,6%).",
         fontsize=7, style="italic", color="#666")

out = "outputs/gapeka_tabang_marangkayu.png"
fig.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
print("Saved:", out)
