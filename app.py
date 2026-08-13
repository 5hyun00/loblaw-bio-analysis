import streamlit as st
import pandas as pd
from analysis import (
    get_summary_table,
    get_melanoma_miraclib_pbmc,
    run_stats,
    get_baseline_cohort,
    get_baseline_breakdowns,
    get_avg_bcell_melanoma_males,
)

st.title("Loblaw Bio - Immune Cell Analysis")
st.write("Dashboard for Bob's miraclib trial analysis")

tab2, tab3, tab4 = st.tabs([
    "Part 2 - Frequencies",
    "Part 3 - Responders vs Non-responders",
    "Part 4 - Subset Analysis"
])

with tab2: 
    st.header("Cell population relative frequencies")
    summary = get_summary_table()
    st.dataframe(summary)

    sample_ids = sorted(summary["sample"].unique())
    chosen = st.selectbox("Choose a sample to inspect:", sample_ids)

    one = summary[summary["sample"] == chosen]
    st.dataframe(one, hide_index = True)
    st.caption(f"Percentages for {chosen} sum to {one['percentage'].sum():.1f}%")

    st.subheader("Full summary table (all samples)")
    st.dataframe(summary, hide_index = True)

with tab3: 
    st.header("Responders vs Non-responders")
    st.write("Melanoma patients on miraclib, PBMC samples only.")

    st.subheader("Relative frequency by cell population")
    st.image("outputs/boxplot_responders_vs_nonresponders.png")

    st.subheader("Statistical test results")
    stats = run_stats()
    st.dataframe(stats, hide_index = True)

    st.subheader("Conclusion")
    st.markdown(
        """
        Each cell population was compared between responders and non-responders
        using a Mann–Whitney U test (non-parametric, robust to the outliers
        visible in the boxplot). Because five populations were tested, p-values
        were adjusted using the Benjamini–Hochberg correction to control the
        false discovery rate.

        - cd4_t_cell showed the strongest signal (raw p ≈ 0.013), with
          responders having a slightly higher relative frequency.
        - After multiple-comparison correction, no population reached
          significance (cd4_t_cell corrected p ≈ 0.067).

        The cd4_t_cell difference is a borderline, hypothesis-generating
        finding worth following up in a larger cohort, rather than an
        established biomarker of miraclib response.
        """
    )

with tab4:
    st.header("Subset Analysis - Baseline Cohort")
    st.write(
        "Melanoma PBMC samples at baseline (time = 0) from patients "
        "treated with miraclib"
    )

    cohort = get_baseline_cohort()
    by_project, by_response, by_sex = get_baseline_breakdowns()

    st.metric("Samples in baseline cohort", len(cohort))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("By project")
        st.dataframe(by_project)
    with col2:
        st.subheader("Responders")
        st.dataframe(by_response)
    with col3:
        st.subheader("By sex")
        st.dataframe(by_sex)

    st.divider()
    st.subheader("Average B cells - melanoma males, responders, time = 0")
    st.caption("All sample and treatment types included.")
    avg_bcell = get_avg_bcell_melanoma_males()
    st.metric("Average B-cell count", f"{avg_bcell:.2f}")

