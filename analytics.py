"""Create the compliance-history chart used by Streamlit."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_compliance_over_time(history):
    """Plot each session's compliance percentage over time."""
    chart_data = history.copy()
    chart_data["timestamp"] = pd.to_datetime(chart_data["timestamp"])

    figure, axes = plt.subplots()
    axes.plot(
        chart_data["timestamp"],
        chart_data["compliance_percentage"],
        marker="o",
    )
    axes.set_title("Compliance Score Over Time")
    axes.set_xlabel("Session time")
    axes.set_ylabel("Compliance (%)")
    axes.set_ylim(0, 100)
    figure.autofmt_xdate()
    figure.tight_layout()

    return figure
