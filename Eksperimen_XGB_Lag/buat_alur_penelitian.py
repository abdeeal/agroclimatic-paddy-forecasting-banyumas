# Fig. 1 alur penelitian (versi revisi) - gaya mengikuti gambar asli (kotak abu-abu, 3 kolom, Arial)
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, PathPatch
from matplotlib.path import Path

W, H = 492, 527                     # px gambar asli (rasio extent di docx)
DPI = 300
fig = plt.figure(figsize=(W / 100, H / 100), dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
plt.rcParams['font.family'] = 'Arial'
FILL, EDGE, FS, LW = '#f2f2f2', '#555555', 7.6, 1.0
BW, BH = 124, 50
COLS = [72, 236, 408]


def box(cx, cy, text, kind='rect'):
    x0, y0 = cx - BW / 2, cy - BH / 2
    if kind == 'oval':
        ax.add_patch(FancyBboxPatch((x0 + 12, y0 + 2), BW - 24, BH - 4, boxstyle='round,pad=0,rounding_size=23',
                                    fc=FILL, ec=EDGE, lw=LW * 1.6))
    elif kind == 'doc':
        verts = [(x0, y0), (x0 + BW, y0), (x0 + BW, y0 + BH - 6),
                 (x0 + BW * 0.75, y0 + BH - 14), (x0 + BW * 0.5, y0 + BH - 6),
                 (x0 + BW * 0.25, y0 + BH + 2), (x0, y0 + BH - 6), (x0, y0)]
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), fc=FILL, ec=EDGE, lw=LW * 1.6))
    else:
        ax.add_patch(Rectangle((x0, y0), BW, BH, fc=FILL, ec=EDGE, lw=LW))
    ax.text(cx, cy - (3 if kind == 'doc' else 0), text, ha='center', va='center', fontsize=FS, linespacing=1.25)
    return (cx, y0, y0 + BH)


def arrow(x, y1, y2):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='-|>', color=EDGE, lw=LW, mutation_scale=9, shrinkA=0, shrinkB=0))


def column(cx, items, top=16, bottom=H - 14):
    n = len(items)
    gap = (bottom - top - n * BH) / (n - 1)
    out = []
    for i, (t, k) in enumerate(items):
        cy = top + BH / 2 + i * (BH + gap)
        out.append(box(cx, cy, t, k))
    for a, b in zip(out, out[1:]):
        arrow(cx, a[2], b[1])
    return out


c1 = column(COLS[0], [('Start', 'oval'),
                      ('Data Collection: BPS,\nIna-Geoportal,\nNASA POWER', 'rect'),
                      ('Spatial Integration of\nAgroclimatic Data', 'rect'),
                      ('Integrated\nDataset', 'doc'),
                      ('Data Cleaning and\nMissing Value\nHandling', 'rect')])
c2 = column(COLS[1], [('Exploratory Data\nAnalysis', 'rect'),
                      ('Outlier Detection', 'rect'),
                      ('Wet-Month Features\n(Count and\nConsecutive Runs)', 'rect'),
                      ('One-Hot Encoding', 'rect'),
                      ('One-Year Lag and\nPrevious-Year\nProductivity', 'rect')])
c3 = column(COLS[2], [('Expanding and\nSliding Window\nScenarios', 'rect'),
                      ('XGBoost Training with\nNested Hyperparameter\nTuning', 'rect'),
                      ('Productivity Evaluation\nvs. Baselines\n(R², RMSE, MAE, MAPE)', 'rect'),
                      ('Wet-Month Ablation\nand SHAP Analysis', 'rect'),
                      ('2025 Paddy Production\nProjection with\n95% Interval', 'rect'),
                      ('End', 'oval')], top=10, bottom=H - 8)


def link(last, cx_from, cx_to, first):
    gx = (cx_from + BW / 2 + cx_to - BW / 2) / 2      # jalur di celah antarkolom
    ymid = (last[1] + last[2]) / 2
    ax.plot([cx_from + BW / 2, gx, gx, cx_to], [ymid, ymid, 4, 4], color=EDGE, lw=LW, solid_joinstyle='miter')
    arrow(cx_to, 4, first[1])


link(c1[-1], COLS[0], COLS[1], c2[0])
link(c2[-1], COLS[1], COLS[2], c3[0])
fig.savefig(sys.argv[1], dpi=DPI, facecolor='white')
