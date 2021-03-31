import re

import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import numpy as np
from forestplot import REGEX


class ForestPlot:
    FONT_RATIO = 72
    CI_SIZE = 30

    def __init__(self, headers, results, ci_col=None, ci_center=0, hmargin=0.1, vmargin=0.1, xlim=None,
                 round_x_axis=True, fontsize=10):

        self.headers = self.reformat(headers)
        self.results = results
        self.ci_center = ci_center
        for i in range(len(self.results)):
            self.results[i] = self.reformat(self.results[i])
        self.ci_col = ci_col
        self.hmargin = hmargin
        self.vmargin = vmargin
        self.round_x_axis = round_x_axis
        if xlim is None:
            self.xlim = [-10e10, 10e10]
        else:
            self.xlim = xlim
        if self.xlim[0] is None:
            self.xlim[0] = -10e10
        if self.xlim[1] is None:
            self.xlim[1] = 10e10
        if self.ci_col is not None:
            self.ci_boundaries()

        self.fontsize = fontsize
        x, y = self.grid_measures()
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, figsize=(x, y))
        plt.xlim((0, 1))
        plt.ylim((0, 1))
        self.ax.axis("off")

    @staticmethod
    def reformat(ar):
        return [a if isinstance(a, tuple) else (a, {}) for a in ar]

    def ci_boundaries(self):
        idx = [txt[0] for txt in self.headers].index(self.ci_col)
        cis = [res[idx] for res in self.results]
        inf, sup = [], []
        for text in cis:
            if text[0] is not None:
                f = re.search(REGEX, text[0])
                m, inf_, sup_ = f.groups()
                inf.append(float(inf_))
                sup.append(float(sup_))

        self.xlim[0] = max(self.xlim[0], np.min(inf))
        self.xlim[1] = min(self.xlim[1], np.max(sup))
        if self.round_x_axis:
            self.xlim[0] = int(divmod(self.xlim[0], 1)[0])
            self.xlim[1] = int(divmod(self.xlim[1], 1)[0]) + 1

    def grid_measures(self):
        y_cell = self.fontsize * 2 / ForestPlot.FONT_RATIO
        self.n_rows = len(self.results) + 2 + 2 * int(self.ci_col is not None)
        y = (self.n_rows * y_cell) / (1 - 2 * self.vmargin)

        self.column_sizes = []
        for i, header in enumerate(self.headers):
            if header[0] == self.ci_col:
                self.column_sizes.append(2 * self.fontsize / ForestPlot.FONT_RATIO / 2.5 * ForestPlot.CI_SIZE)
            max_size = np.max(
                [len(texts[i][0]) for texts in self.results if texts[i][0] is not None] + [len(header[0])])
            self.column_sizes.append(2 * self.fontsize / ForestPlot.FONT_RATIO / 2.5 * max_size)

        x = (np.sum(self.column_sizes)) / (1 - 2 * self.hmargin)

        self.column_sizes = np.asarray(self.column_sizes) / np.sum(self.column_sizes) * (1 - 2 * self.hmargin)

        self.column_pos = np.cumsum([0] + list(self.column_sizes[:-1]))
        self.column_pos += self.hmargin
        self.cell_height = (1 - self.vmargin * 2) / self.n_rows
        self.row_pos = 1 - (self.vmargin + self.cell_height * (np.arange(self.n_rows) + 0.5))

        return x, y

    def add_cell(self, n_col, n_row, text, fontdict):
        x = self.column_pos[n_col]
        y = self.row_pos[n_row]
        fontdict['fontsize'] = self.fontsize
        self.ax.text(x, y, text, fontdict=fontdict, va='center')
        return

    def ci_scale(self, left_pos, hsize):
        def f(point):
            point = (point - self.xlim[0]) / (self.xlim[1] - self.xlim[0])
            return point * hsize + left_pos

        return f

    def draw_ci(self, n_row, scale, value, inf, sup, **kwargs):
        y = self.row_pos[n_row]
        inf = max(self.xlim[0], inf)
        sup = min(self.xlim[1], sup)
        self.ax.hlines(y, scale(inf), scale(sup), **kwargs)
        self.ax.scatter((scale(value),), (y,), c='black', **kwargs)
        delta = self.cell_height / 3
        if inf == self.xlim[0]:
            self.ax.vlines(scale(inf), y - delta, y + delta, **kwargs)
        if sup == self.xlim[1]:
            self.ax.vlines(scale(sup), y - delta, y + delta, **kwargs)
        return

    def add_column(self, header, values, n_col):
        text, fontdict = header
        fontdict['fontweight'] = fontdict.get('fontweight', 'bold')
        self.add_cell(n_col, 0, text, fontdict)
        print(values)
        for i, (name, fontdict) in enumerate(values):
            self.add_cell(n_col, i + 2, name, fontdict)

    def add_forest(self, header, values, n_col):
        size = self.column_sizes[n_col]
        x = self.column_pos[n_col]
        scale = self.ci_scale(x, size)

        text, fontdict = header
        self.add_cell(0, n_col, text, fontdict)
        for i, (text, kwargs) in enumerate(values):
            if text is not None:
                f = re.search(REGEX, text)
                m, inf, sup = f.groups()
                self.draw_ci(i + 2, scale, float(m), float(inf), float(sup), **kwargs)

        # DRAW THE AXIS AND VERTICAL LINE
        y = self.row_pos[-2]
        delta = self.cell_height / 3
        self.ax.vlines(scale(self.ci_center), self.row_pos[0], y, linestyle='--')
        self.ax.hlines(y, scale(self.xlim[0]), scale(self.xlim[1]))
        self.ax.vlines(scale(self.xlim[0]), y, y - delta)
        self.ax.vlines(scale(self.xlim[1]), y, y - delta)
        for value in [self.ci_center] + self.xlim:
            self.ax.text(scale(value), self.row_pos[-1], value, va='center', ha='center', fontsize=self.fontsize)

    def plot(self, savefig=None):
        shift = 0
        for i, header in enumerate(self.headers):
            values = [texts[i] for texts in self.results]
            if header[0] == self.ci_col:
                self.add_forest(('', {}), values, i)
                shift = 1
            self.add_column(header, values, i + shift)
        if savefig is not None:
            plt.savefig(savefig)
        return self.ax
