import numpy as np
import parallel as par
from matplotlib import cm
from plotsUtil import *


def cornerPlotScatter(data, title=None):

    if not par.irank == par.iroot:
        return

    nDim = data.shape[1]
    if nDim > 2:
        fig, axs = plt.subplots(nDim - 1, nDim - 1, figsize=(8, 8))
        for idim in range(nDim - 1):
            for jdim in range(idim + 1, nDim):
                axs[idim, jdim - 1].plot(
                    data[:, idim], data[:, jdim], "o", markersize=0.5
                )
                axprettyLabels(
                    axs[idim, jdim - 1],
                    "feat" + str(idim),
                    "feat" + str(jdim),
                    10,
                )
        if not title == None:
            fig.suptitle(
                title,
                fontsize=16,
                fontweight="bold",
                fontname="Times New Roman",
            )
    elif nDim == 2:
        fig = plt.figure()
        plt.plot(data[:, 0], data[:, 1], "o", markersize=0.5)
        prettyLabels("feat" + str(0), "feat" + str(1), 10, title=title)


def cornerPlotScatterColor(data, colorData):

    if not par.irank == par.iroot:
        return

    nDim = data.shape[1]
    if nDim > 2:
        fig, axs = plt.subplots(nDim - 1, nDim - 1, figsize=(8, 8))
        for idim in range(nDim - 1):
            for jdim in range(idim + 1, nDim):
                a = axs[idim, jdim - 1].scatter(
                    data[:, idim],
                    data[:, jdim],
                    c=colorData,
                    s=0.5,
                    cmap=cm.gray_r,
                    alpha=0.9,
                )
                axprettyLabels(
                    axs[idim, jdim - 1],
                    "feat" + str(idim),
                    "feat" + str(jdim),
                    10,
                )
    elif nDim == 2:
        fig = plt.figure()
        plt.scatter(
            data[:, 0],
            data[:, 1],
            c=colorData,
            s=0.5,
            cmap=cm.gray_r,
            alpha=0.9,
        )
        prettyLabels("feat" + str(0), "feat" + str(1), 10)
        plt.colorbar()
