import re

import matplotlib.pyplot as plt

import numpy as np
from forestplot import REGEX


class ForestPlot:
    # conversion fontsize / figsize
    FONT_RATIO = 72

    def __init__(self, headers, results, ci_col=None, ci_center=0, hmargin=0.1, vmargin=0.1, xlim=None,
                 round_x_axis=True, fontsize=10, ci_size=30):
        """
        :param headers: list of str
            Columns titles
        :param results: list of list
        :param ci_col: str
            Confidence intervals column name
        :param ci_center: float
            Confidence intervals central value (eg 0 for log HR and 1 for HR)
        :param hmargin: float between 0 and 1
            Percentage of the horizontal margin
        :param vmargin: float between 0 and 1
            Percentage of the vertical margin
        :param xlim: tuple
            Confidence intervals limits
        :param round_x_axis: int > 0
            The number of decimals to use when rounding the CI x axis boundaries
        :param fontsize: int
        :param ci_size: int
            TODO
        """
        self.headers = self.reformat(headers)

        self.results = results
        for i in range(len(self.results)):
            self.results[i] = self.reformat(self.results[i])

        self.ci_center = ci_center
        self.ci_size = ci_size
        self.hmargin = hmargin
        self.vmargin = vmargin
        self.round_x_axis = round_x_axis
        self.fontsize = fontsize

        self.xlim = xlim
        if self.xlim is None:
            self.xlim = np.array([-1, 1]) * np.inf
        if self.xlim[0] is None:
            self.xlim[0] = -np.inf
        if self.xlim[1] is None:
            self.xlim[1] = np.inf

        self.ci_col = ci_col
        if self.ci_col is not None:
            if self.ci_col not in [txt[0] for txt in self.headers]:
                raise Exception(f'{self.ci_col} not found in {[txt[0] for txt in self.headers]}')
            self.ci_boundaries()

        x, y = self.grid_measures()
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, figsize=(x, y))
        plt.xlim((0, 1))
        plt.ylim((0, 1))
        self.ax.axis("off")

    @staticmethod
    def reformat(ar):
        """
        Transform ar values into tuples
        [a, (b, c)] -> [(a, {}), (b, c)]
        :return: List of tuples
        """
        return [a if isinstance(a, tuple) else (a, {}) for a in ar]

    def ci_boundaries(self):
        """
        Compute the segment that contains all the CIs then intersect with self.xlim
        :return: None
        """
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
        if self.round_x_axis is not None:
            self.xlim[0] = round(self.xlim[0] - 10 ** (-self.round_x_axis) / 2, self.round_x_axis)
            self.xlim[1] = round(self.xlim[1] + 10 ** (-self.round_x_axis) / 2, self.round_x_axis)

    def grid_measures(self):
        """
        Compute the elements positions in the Axe coordinates ((0, 1), (0, 1))
        :return: None
        """
        y_cell = self.fontsize * 2 / ForestPlot.FONT_RATIO
        self.n_rows = len(self.results) + 2 + 2 * int(self.ci_col is not None)
        y = (self.n_rows * y_cell) / (1 - 2 * self.vmargin)

        self.column_sizes = []
        for i, header in enumerate(self.headers):
            if header[0] == self.ci_col:
                self.column_sizes.append(2 * self.fontsize / ForestPlot.FONT_RATIO / 2.5 * self.ci_size)
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

    def draw_cell(self, n_col, n_row, text, fontdict):
        """
        Draw the cell content
        :param n_col: int
        :param n_row: int
        :param text: cell content
        :param fontdict: dict
        :return: None
        """
        x = self.column_pos[n_col]
        y = self.row_pos[n_row]
        fontdict['fontsize'] = self.fontsize
        self.ax.text(x, y, text, fontdict=fontdict, va='center')
        return

    def draw_ci(self, n_row, scale, value, inf, sup, **kwargs):
        """
        Draw the confidence interval line
        :param n_row: int
        :param scale: function
        :param value: mean value
        :param inf: lower bound
        :param sup: upper bound
        :param kwargs: dict
        :return: None
        """
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

    def draw_forest(self, header, values, n_col):

        def scale(point):
            point = (point - self.xlim[0]) / (self.xlim[1] - self.xlim[0])
            return point * self.column_sizes[n_col] + self.column_pos[n_col]

        text, fontdict = header
        self.draw_cell(0, n_col, text, fontdict)
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
                self.draw_forest(('', {}), values, i)
                shift = 1

            # draw column
            text, fontdict = header
            fontdict['fontweight'] = fontdict.get('fontweight', 'bold')
            self.draw_cell(i + shift, 0, text, fontdict)
            for j, (name, fontdict) in enumerate(values):
                self.draw_cell(i + shift, j + 2, name, fontdict)

        if savefig is not None:
            plt.savefig(savefig)
        return self.ax
