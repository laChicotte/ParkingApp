"""Figures du tableau de bord, utilisables avec Tkinter ou sans fenêtre."""
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from app.config import theme


def movement_figure(data):
    figure = Figure(figsize=(6, 3), dpi=100, facecolor="white")
    axes = figure.subplots()
    figure.subplots_adjust(left=.08, right=.98, bottom=.18, top=.82)
    entries = [int(row["entries"]) for row in data]
    exits = [int(row["exits"]) for row in data]
    if not data or not sum(entries + exits):
        axes.set_axis_off()
        axes.text(.5, .5, "Aucun mouvement sur cette période",
                  ha="center", va="center", transform=axes.transAxes,
                  color=theme.Colors.TEXT_SECONDARY, fontsize=10, wrap=True)
        return figure
    positions = list(range(len(data)))
    axes.bar([x - .19 for x in positions], entries, width=.34,
             color=theme.Colors.PRIMARY, label="Entrées", zorder=3)
    axes.bar([x + .19 for x in positions], exits, width=.34,
             color=theme.Colors.WARNING, label="Sorties", zorder=3)
    tick_count = min(7, len(data))
    ticks = ([0] if tick_count == 1 else
             [round(index * (len(data) - 1) / (tick_count - 1))
              for index in range(tick_count)])
    axes.set_xticks(ticks, [data[x]["date"].strftime("%d/%m") for x in ticks])
    axes.set_xlim(-.7, len(data) - .3)
    axes.set_ylim(0, max(entries + exits) * 1.25)
    axes.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=4))
    axes.tick_params(axis="both", labelsize=9, length=0,
                     colors=theme.Colors.TEXT_SECONDARY, pad=8)
    axes.grid(axis="y", color=theme.Colors.BG_MUTED, linewidth=.8, zorder=0)
    for side in ("top", "right", "left"):
        axes.spines[side].set_visible(False)
    axes.spines["bottom"].set_color(theme.Colors.BORDER)
    axes.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=2,
                frameon=False, fontsize=9, borderaxespad=0,
                labelcolor=theme.Colors.TEXT_PRIMARY)
    return figure


def category_figure(counts):
    """Barres avec libellés directs : même une petite catégorie reste lisible."""
    figure = Figure(figsize=(4, 3), dpi=100, facecolor="white")
    axes = figure.subplots()
    figure.subplots_adjust(left=.04, right=.96, bottom=.08, top=.94)
    categories = sorted(((str(key), int(value)) for key, value in counts.items()),
                        key=lambda item: item[1], reverse=True)
    total = sum(value for _, value in categories)
    axes.set_axis_off()
    if not total:
        axes.text(.5, .5, "Aucune moto enregistrée", ha="center", va="center",
                  transform=axes.transAxes, color=theme.Colors.TEXT_SECONDARY, fontsize=10)
        return figure
    labels = {"Etudiant": "Étudiants", "Enseignant": "Enseignants",
              "Personnel": "Personnel"}
    colors = [theme.Colors.PRIMARY, theme.Colors.INFO, theme.Colors.SUCCESS,
              theme.Colors.WARNING]
    for index, (key, count) in enumerate(categories):
        share = count / total * 100
        y = index * 1.1
        axes.text(0, y, labels.get(key, key), fontsize=10,
                  va="center", color=theme.Colors.TEXT_PRIMARY)
        axes.text(100, y, f"{count}  ({share:.1f} %)".replace('.', ','),
                  fontsize=10, ha="right", va="center",
                  color=theme.Colors.TEXT_SECONDARY)
        axes.barh(y + .28, 100, height=.12, color=theme.Colors.BG_MUTED)
        axes.barh(y + .28, share, height=.12, color=colors[index % len(colors)])
    axes.set_xlim(0, 100)
    axes.set_ylim(len(categories) * 1.1 - .1, -.3)
    return figure
