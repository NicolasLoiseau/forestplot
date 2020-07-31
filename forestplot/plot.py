import collections
import re

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from forestplot import PV_INTER_NAME, SUBGROUPS_NAME


def plot(data, savepath=None):
    delta = 0.5
    top_margin = 2
    bottom_margin = 2
    margin = top_margin + bottom_margin

    # LINES NUMBER
    p = margin
    for k, v in data.items():
        p += 1 + len(v[SUBGROUPS_NAME].keys())

    x = 20
    z = p * x / 30

    decimal = '(\d(?:\.\d+)?)'
    reg = decimal + '\(' + decimal + '-' + decimal + '\)'
    fontsize = 77 * z * (1 - delta) / (p + 1)
    horiz_margin = fontsize / x / 77
    # WRITE COLUMNS NAMES
    col_pos = {
        'Features': horiz_margin,
        'HR (95% CI)': 1 - 18 * horiz_margin,
        'Pvalue': 1 - 5.5 * horiz_margin
    }
    pos_colnames = (p - (1 - delta) / 2) / (p + 1)

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(x, z))

    for name, pos in col_pos.items():
        ax.text(pos, pos_colnames, name, fontsize=fontsize, fontweight='bold')

    lign_count = top_margin
    col_count = 0
    lowest, highest = 1, 1
    biggest = 0
    for name, sub in data.items():
        biggest = max(len(name), biggest)
        pos = (p - lign_count - (1 - delta) / 2) / (p + 1)
        lign_count += 1

        # WRITE FEATURE NAME AND ASSOCIATED INTERACTION PVALUE
        ax.text(col_pos['Features'], pos, name, fontsize=fontsize, fontweight='bold')
        ax.text(col_pos['Pvalue'], pos, round(sub[PV_INTER_NAME], 2), fontsize=fontsize)

        for subname, values in collections.OrderedDict(sorted(sub[SUBGROUPS_NAME].items())).items():
            pos = (p - lign_count - (1 - delta) / 2) / (p + 1)
            lign_count += 1

            # WRITE SUBGROUP NAME AND SUBGROUP HR WRT THE TRT
            ax.text(col_pos['Features'], pos, subname, fontsize=fontsize)
            ax.text(col_pos['HR (95% CI)'], pos, values, fontsize=fontsize)

            # COLLECT HR INFO
            f = re.search(reg, values)
            m, inf, sup = f.groups()
            lowest = min(float(inf), lowest)
            highest = max(float(sup), highest)

    # LIMIT lEFT AND RIGHT FOR THE CI LINES
    pos_ci_left = col_pos['Features'] + biggest * horiz_margin
    pos_ci_right = col_pos['HR (95% CI)'] - 2 * horiz_margin

    def scale(x):
        x = float(x)
        x = (x - lowest) / (highest - lowest)
        return x * (pos_ci_right - pos_ci_left) + pos_ci_left

    # DRAW THE CONF INT LINE
    lign_count = top_margin
    for name, sub in data.items():
        lign_count += 1
        for subname, values in collections.OrderedDict(sorted(sub[SUBGROUPS_NAME].items())).items():
            pos = (p - lign_count + 1 / 5 - (1 - delta) / 2) / (p + 1)
            lign_count += 1
            f = re.search(reg, values)
            m, inf, sup = f.groups()
            ax.hlines(pos, scale(inf), scale(sup))
            ax.scatter((scale(m),), (pos,), c='black')

    # DRAW THE X AXIS AND VERTICAL LINE
    pos_bottom_lign = (bottom_margin + 1 / 5 - (1 - delta) / 2) / (p + 1)
    pos_top_lign = (p - top_margin + 1 - 1 / 5 - (1 - delta) / 2) / (p + 1)
    ax.vlines(scale(1), pos_bottom_lign, pos_top_lign, linestyle='--')
    ax.hlines(pos_bottom_lign, pos_ci_left, pos_ci_right)
    ax.vlines(pos_ci_left, pos_bottom_lign, pos_bottom_lign - horiz_margin * x / z)
    ax.vlines(pos_ci_right, pos_bottom_lign, pos_bottom_lign - horiz_margin * x / z)
    pos_bottom_lign = (bottom_margin - 1 - (1 - delta) / 2) / (p + 1)
    for value in (1, lowest, highest):
        ax.text(scale(value) - horiz_margin / 2, pos_bottom_lign, value, fontsize=fontsize)

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 1)

    if savepath is not None:
        plt.savefig(savepath)

    return ax
