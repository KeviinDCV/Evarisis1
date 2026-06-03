# -*- coding: utf-8 -*-
"""Renderiza un grafico de muestra con el estilo OSCURO para validar la estetica."""
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({
    "figure.facecolor": "#23262b", "axes.facecolor": "#2b2f36",
    "savefig.facecolor": "#23262b", "axes.edgecolor": "#3a3f47",
    "axes.linewidth": 0.8, "axes.labelcolor": "#e6e8ec",
    "axes.titlecolor": "#eef1f6", "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.grid": True, "axes.axisbelow": True,
    "grid.color": "#3a3f47", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": "#c2c7d0", "ytick.color": "#c2c7d0", "text.color": "#e6e8ec",
    "axes.prop_cycle": mpl.cycler(color=["#5b8def", "#4ecb8d", "#e0a458", "#d9647a", "#9aa6bf", "#7c8cff"]),
})

fig, axs = plt.subplots(1, 3, figsize=(13, 3.6), dpi=100)
axs[0].bar(["Patología", "Cirugía", "Onco", "Lab", "Rx"], [42, 31, 27, 18, 9])
axs[0].set_title("Top Servicios (n=127)")
axs[0].tick_params(axis="x", rotation=25, labelsize=8)
axs[1].pie([58, 42], labels=["Maligno", "Benigno"], autopct="%1.1f%%",
           colors=["#d9647a", "#4ecb8d"], startangle=90)
axs[1].set_title("Distribución de Malignidad")
axs[2].plot([1, 2, 3, 4, 5, 6], [12, 19, 15, 22, 18, 25], marker="o")
axs[2].set_title("Informes por mes")
axs[2].set_xlabel("Mes")
fig.tight_layout()
fig.savefig(r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\herramientas_ia\resultados\_test_dark_chart.png",
            facecolor="#23262b")
print("OK")
