import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Statistical Plotting Tool",
    layout="centered"
)

st.title("Statistical Plotting Tool")

st.write(
    "This tool creates plots from statistical results that you "
    "have already calculated."
)


# ============================================================
# SECTION 1 — BOX-AND-WHISKER PLOT
# ============================================================

st.header("Section 1: Box-and-Whisker Plot")

st.write(
    "Enter your five-number summary and the data label."
)


# ------------------------------------------------------------
# Data label
# ------------------------------------------------------------

box_label = st.text_input(
    "Data label (include the unit if applicable)",
    placeholder="e.g., Resistance (kΩ)",
    key="box_label"
)


# ------------------------------------------------------------
# Five-number summary
# ------------------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    minimum = st.number_input(
        "Minimum",
        value=0.0,
        format="%.6g"
    )

with col2:
    q1 = st.number_input(
        "Q1",
        value=1.0,
        format="%.6g"
    )

with col3:
    median = st.number_input(
        "Median",
        value=2.0,
        format="%.6g"
    )

with col4:
    q3 = st.number_input(
        "Q3",
        value=3.0,
        format="%.6g"
    )

with col5:
    maximum = st.number_input(
        "Maximum",
        value=4.0,
        format="%.6g"
    )


# ------------------------------------------------------------
# Check order of five-number summary
# ------------------------------------------------------------

valid_summary = (
    minimum <= q1 <= median <= q3 <= maximum
)

if not valid_summary:

    st.warning(
        "The values must satisfy: "
        "Minimum ≤ Q1 ≤ Median ≤ Q3 ≤ Maximum."
    )

else:

    # --------------------------------------------------------
    # Create box-and-whisker plot from entered statistics
    # --------------------------------------------------------

    st.subheader("Box-and-Whisker Plot")

    fig1, ax1 = plt.subplots(
        figsize=(8, 3)
    )

    # Matplotlib boxplot statistics
    box_stats = [{
        "med": median,
        "q1": q1,
        "q3": q3,
        "whislo": minimum,
        "whishi": maximum,
        "fliers": []
    }]

    ax1.bxp(
        box_stats,
        vert=False,
        showfliers=False,
        widths=0.45
    )

    ax1.set_xlabel(
        box_label
    )

    ax1.set_yticks([])

    ax1.grid(
        True,
        axis="x",
        alpha=0.3
    )

    fig1.tight_layout()

    st.pyplot(fig1)


    # --------------------------------------------------------
    # Download box plot
    # --------------------------------------------------------

    buffer1 = BytesIO()

    fig1.savefig(
        buffer1,
        format="png",
        dpi=300,
        bbox_inches="tight"
    )

    buffer1.seek(0)

    st.download_button(
        label="Download Box-and-Whisker Plot",
        data=buffer1,
        file_name="box_whisker_plot.png",
        mime="image/png"
    )

    plt.close(fig1)


# ============================================================
# SECTION 2 — HISTOGRAM
# ============================================================

st.header("Section 2: Histogram")

st.write(
    "Upload a CSV file with no header. The columns should contain:"
)

st.markdown(
    """
1. **Bin center**
2. **Frequency**
3. **Relative frequency** *(optional)*
"""
)

st.write(
    "If a third column is included, relative frequency will be "
    "shown on the right y-axis."
)


# ------------------------------------------------------------
# Histogram label
# ------------------------------------------------------------

hist_label = st.text_input(
    "Data label (include the unit if applicable)",
    placeholder="e.g., Resistance (kΩ)",
    key="hist_label"
)


# ------------------------------------------------------------
# Upload histogram CSV
# ------------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload histogram CSV file",
    type=["csv"]
)


if uploaded_file is not None:

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    df = pd.read_csv(
        uploaded_file,
        header=None
    )


    # --------------------------------------------------------
    # Check number of columns
    # --------------------------------------------------------

    if df.shape[1] < 2:

        st.error(
            "The CSV file must contain at least two columns: "
            "bin center and frequency."
        )

        st.stop()


    if df.shape[1] > 3:

        st.warning(
            "More than three columns were found. "
            "Only the first three columns will be used."
        )


    # Keep at most first three columns
    df = df.iloc[:, :3]


    # --------------------------------------------------------
    # Assign column names
    # --------------------------------------------------------

    if df.shape[1] == 2:

        df.columns = [
            "Bin Center",
            "Frequency"
        ]

        has_relative_frequency = False

    else:

        df.columns = [
            "Bin Center",
            "Frequency",
            "Relative Frequency"
        ]

        has_relative_frequency = True


    # --------------------------------------------------------
    # Convert columns to numeric
    # --------------------------------------------------------

    df["Bin Center"] = pd.to_numeric(
        df["Bin Center"],
        errors="coerce"
    )

    df["Frequency"] = pd.to_numeric(
        df["Frequency"],
        errors="coerce"
    )

    if has_relative_frequency:

        df["Relative Frequency"] = pd.to_numeric(
            df["Relative Frequency"],
            errors="coerce"
        )


    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    required_columns = [
        "Bin Center",
        "Frequency"
    ]

    if has_relative_frequency:

        required_columns.append(
            "Relative Frequency"
        )

    df = df.dropna(
        subset=required_columns
    )


    # --------------------------------------------------------
    # Check data
    # --------------------------------------------------------

    if len(df) < 2:

        st.error(
            "At least two valid bins are required."
        )

        st.stop()


    # --------------------------------------------------------
    # Sort according to bin center
    # --------------------------------------------------------

    df = df.sort_values(
        "Bin Center"
    ).reset_index(drop=True)


    # --------------------------------------------------------
    # Extract data
    # --------------------------------------------------------

    bin_centers = df["Bin Center"].to_numpy()

    frequencies = df["Frequency"].to_numpy()

    if has_relative_frequency:

        relative_frequencies = (
            df["Relative Frequency"].to_numpy()
        )


    # ========================================================
    # CALCULATE BIN SIZE
    # ========================================================

    differences = np.diff(
        bin_centers
    )

    bin_size = differences[0]


    # --------------------------------------------------------
    # Check whether bin spacing is uniform
    # --------------------------------------------------------

    uniform_bins = np.allclose(
        differences,
        bin_size,
        rtol=1e-5,
        atol=1e-8
    )


    if not uniform_bins:

        st.error(
            "The spacing between adjacent bin centers is not "
            "constant. This tool requires equal-width bins."
        )

        st.stop()


    # --------------------------------------------------------
    # Display imported data
    # --------------------------------------------------------

    st.subheader("Imported Histogram Data")

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Display bin size
    # --------------------------------------------------------

    st.write(
        f"Bin size: **{bin_size:.6g}**"
    )


    # ========================================================
    # CREATE HISTOGRAM
    # ========================================================

    st.subheader("Histogram")

    fig2, ax_left = plt.subplots(
        figsize=(8, 5)
    )


    # --------------------------------------------------------
    # Plot frequency bars
    # --------------------------------------------------------

    ax_left.bar(
        bin_centers,
        frequencies,
        width=bin_size,
        align="center",
        facecolor="none",
        edgecolor="black",
        linewidth=1.2
    )


    # --------------------------------------------------------
    # X-axis
    # --------------------------------------------------------

    ax_left.set_xlabel(
        hist_label
    )

    # Bin centers appear as x-axis values
    ax_left.set_xticks(
        bin_centers
    )

    ax_left.set_xticklabels(
        [
            f"{x:.6g}"
            for x in bin_centers
        ],
        fontsize=10
    )


    # --------------------------------------------------------
    # Left y-axis
    # --------------------------------------------------------

    ax_left.set_ylabel(
        "Frequency"
    )

    ax_left.grid(
        True,
        axis="y",
        alpha=0.3
    )


    # ========================================================
    # OPTIONAL RIGHT Y-AXIS
    # ========================================================

    if has_relative_frequency:

        # Determine conversion between frequency
        # and relative frequency from the uploaded data.

        valid = frequencies > 0

        if np.any(valid):

            conversion_factors = (
                relative_frequencies[valid]
                / frequencies[valid]
            )

            conversion_factor = np.mean(
                conversion_factors
            )

            # Create right y-axis
            ax_right = ax_left.twinx()

            ymin, ymax = ax_left.get_ylim()

            ax_right.set_ylim(
                ymin * conversion_factor,
                ymax * conversion_factor
            )

            ax_right.set_ylabel(
                "Relative Frequency"
            )

        else:

            st.warning(
                "A relative-frequency axis could not be created "
                "because all frequencies are zero."
            )


    # --------------------------------------------------------
    # Finish figure
    # --------------------------------------------------------

    fig2.tight_layout()

    st.pyplot(fig2)


    # ========================================================
    # DOWNLOAD HISTOGRAM
    # ========================================================

    buffer2 = BytesIO()

    fig2.savefig(
        buffer2,
        format="png",
        dpi=300,
        bbox_inches="tight"
    )

    buffer2.seek(0)

    st.download_button(
        label="Download Histogram",
        data=buffer2,
        file_name="histogram.png",
        mime="image/png"
    )

    plt.close(fig2)
