"""
NEEDS REFORMATTING
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from wordcloud import WordCloud
from FormatData import FormatData

def get_card_counts_df(card_set):
    mains = card_set.main_boards()
    return (
        pd.DataFrame(
            mains[~mains.set.isna()]
            .groupby(["card", "color"])
            ["count"]
            .sum()
        )
        .sort_values(
            "count",
            ascending=False
        )
        .reset_index()
    )

def make_table(df, color, ax):
    ax.set_axis_off()
    ax.set_frame_on(False)
    table = pd.plotting.table(
        ax, df[df.color.str.contains(color)].head(5), 
        loc="center")
    table.auto_set_column_width(0)
    table.set_fontsize(16)
    table.scale(1, 2)

    return table

def gather_tables(df):
    fig, axes = plt.subplots(3, 2, figsize=(15, 10))
    plt.subplots_adjust(wspace=2, hspace=600)
    make_table(df, "", axes[0][0])
    make_table(df, "W", axes[0][1])
    make_table(df, "U", axes[1][0])
    make_table(df, "B", axes[1][1])
    make_table(df, "R", axes[2][0])
    make_table(df, "G", axes[2][1])
    
    return fig

def save_tables(df, file):
    tables = gather_tables(df)
    plt.savefig(r"C:\Users\gfmar_000\Desktop\MTG Webpage\\" + file)
    plt.close(tables)

def plot_colors_bar(color_count, axs):
    x = list(color_count.keys())
    y = list(color_count.values())
    axs.bar(x, y)
    for x_coord in color_count:
        axs.annotate(color_count[x_coord], (x_coord, color_count[x_coord] + 0.75))
    
    return axs

def plot_colors_pie(color_count, axs):
    axs.pie(color_count.values(),
           colors = ["white", "blue", "black", "red", "green", "grey"],
           wedgeprops={"edgecolor": "k"},
           labels=["W", "U", "B", "R", "G", "A"],
           autopct="%.1f%%",
           pctdistance=0.5)
    centre_circle = plt.Circle((0,0),0.70,fc='white', ec="black")
    plt.sca(axs)
    plt.gca().add_artist(centre_circle)
    
    return axs

def plot_sets(set_count, axs):
    axs.pie(
        set_count.values(),
        colors = [
            "white",
            "blue",
            "black",
            "red",
            "green",
            "grey"
        ],
        wedgeprops={"edgecolor": "black"},
        labels=["THB", "ELD", "M20", "WAR", "RNA", "GRN"],
        autopct="%.1f%%",
        pctdistance=0.5
    )
    centre_circle = plt.Circle((0,0),0.70,fc='white', ec="black")
    plt.sca(axs)
    plt.gca().add_artist(centre_circle)
    
    return axs

def compare_standard_colors(set_1_data, set_2_data, set_1="ELD", set_2="THB"):
    labels=["W", "U", "B", "R", "G", "A"]
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    plot_colors_bar(set_1_data, axs[0][0])
    plot_colors_bar(set_2_data, axs[0][1])
    plot_colors_pie(set_1_data, axs[1][0])
    plot_colors_pie(set_2_data, axs[1][1])
    axs[0][0].set_title(f"Colors in {set_1} Standard")
    axs[0][1].set_title(f"Colors in {set_2} Standard")
    fig.suptitle("Comparing Colors in Standard")

    return fig

def compare_standard_sets(set_1_data, set_2_data, set_1="ELD", set_2="THB"):
    fig, axs = plt.subplots(1, 2, figsize=(12, 12))
    plot_sets(set_1_data, axs[0])
    plot_sets(set_2_data, axs[1])
    axs[0].set_title(f"Sets in {set_1} Standard", loc="left")
    axs[1].set_title(f"Sets in {set_2} Standard", loc="left")
    fig.suptitle("Comparing Sets in Standard")
    
    return fig

def generate_pdf(set_1="ELD", set_2="THB"):
    set_1_data = FormatData("Set Metrics", set_1)
    set_2_data = FormatData("Set Metrics", set_2)
    with PdfPages("test_pdf.pdf") as export_pdf:
        colors_fig = compare_standard_colors(set_1_data.color_count, set_2_data.color_count)
        export_pdf.savefig()
        plt.close(colors_fig)
        sets_fig = compare_standard_sets(set_1_data.set_count, set_2_data.set_count)
        export_pdf.savefig()
        plt.close(sets_fig)
