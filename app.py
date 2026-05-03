from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard_data import (
    EXPERIENCE_LABELS,
    REMOTE_ORDER,
    filter_frame,
    load_dashboard_data,
    salary_summary,
)


st.set_page_config(
    page_title="Stack Overflow Developer Survey Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "survey_results_public.csv"
NARRATIVE_PATH = ROOT / "docs" / "final_narrative.md"


@st.cache_data(show_spinner=False)
def get_data():
    return load_dashboard_data(str(DATA_PATH))


bundle = get_data()
df = bundle.df
MIN_COUNTRY_RESPONSES = 10

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .hero {
        padding: 1.25rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #f4efe6 0%, #fdf8f1 45%, #eef4f7 100%);
        border: 1px solid #e7ddd1;
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0 0 0.35rem 0;
        color: #4b1d0f;
        font-size: 2.2rem;
    }
    .hero p {
        margin: 0.3rem 0;
        color: #3a332f;
        font-size: 1rem;
    }
    .note-card {
        padding: 0.9rem 1rem;
        border-radius: 14px;
        background: #f8f7f4;
        border-left: 5px solid #9c6644;
        margin: 0.4rem 0 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Stack Overflow Developer Survey Dashboard</h1>
        <p><strong>Question:</strong> What factors appear to influence salary and job satisfaction among professional developers?</p>
        <p>This final dashboard is designed for a non-technical audience. It highlights the patterns that mattered most in the analysis: experience, geography, remote work, and the gap between pay and satisfaction.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filters")
    default_countries = df["Country"].value_counts().head(8).index.tolist()
    selected_countries = st.multiselect(
        "Country",
        options=sorted(df["Country"].dropna().unique().tolist()),
        default=default_countries,
        help="Use country filters to avoid misleading global salary comparisons.",
    )
    selected_remote = st.multiselect(
        "Work arrangement",
        options=REMOTE_ORDER,
        default=["Remote", "In-person", "Hybrid (some in-person, leans heavy to flexibility)"],
    )
    selected_experience = st.multiselect(
        "Experience band",
        options=EXPERIENCE_LABELS,
        default=EXPERIENCE_LABELS,
    )
    eligible_country_count = (
        filter_frame(bundle.salary_df, selected_countries, selected_remote, selected_experience)
        .groupby("Country", dropna=True)
        .agg(respondents=("ResponseId", "count"))
        .query(f"respondents >= {MIN_COUNTRY_RESPONSES}")
        .shape[0]
    )
    country_slider_max = max(1, eligible_country_count)
    country_slider_default = min(10, country_slider_max)
    top_n_countries = st.slider(
        "Countries shown in geographic view",
        min_value=1,
        max_value=country_slider_max,
        value=country_slider_default,
    )
    top_n_languages = st.slider("Languages shown", min_value=5, max_value=15, value=10)
    st.markdown(
        """
        <div class="note-card">
        <strong>How to read this dashboard</strong><br>
        Start with the Overview tab for the big picture, then use Salary Explorer and Satisfaction Explorer to compare filtered groups.
        </div>
        """,
        unsafe_allow_html=True,
    )


filtered_df = filter_frame(df, selected_countries, selected_remote, selected_experience)
filtered_salary = filter_frame(bundle.salary_df, selected_countries, selected_remote, selected_experience)
filtered_jobsat = filter_frame(bundle.jobsat_df, selected_countries, selected_remote, selected_experience)
filtered_scatter = filter_frame(bundle.scatter_df, selected_countries, selected_remote, selected_experience)
filtered_languages = filter_frame(bundle.language_df, selected_countries, selected_remote, selected_experience)

summary = salary_summary(filtered_df)

metric_cols = st.columns(4)
metric_cols[0].metric("Filtered responses", f"{summary['responses']:,}")
metric_cols[1].metric(
    "Median salary",
    "N/A" if pd.isna(summary["median_salary"]) else f"${summary['median_salary']:,.0f}",
)
metric_cols[2].metric(
    "Median job satisfaction",
    "N/A" if pd.isna(summary["median_jobsat"]) else f"{summary['median_jobsat']:.1f} / 10",
)
metric_cols[3].metric(
    "Median languages used",
    "N/A" if pd.isna(summary["median_languages"]) else f"{summary['median_languages']:.0f}",
)

st.markdown(
    """
    <div class="note-card">
    <strong>Key interpretation rule:</strong> salary in this survey is strongly influenced by country. That is why the dashboard puts country filters up front and keeps geography visible in the overview.
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.error("No responses match the current filters. Broaden the country, work arrangement, or experience selections.")
    st.stop()

tab_overview, tab_salary, tab_satisfaction, tab_narrative = st.tabs(
    ["Overview", "Salary Explorer", "Satisfaction Explorer", "Final Narrative"]
)

with tab_overview:
    st.subheader("Question and dashboard purpose")
    st.write(
        "The project asks which factors appear to influence salary and job satisfaction among professional developers. "
        "This dashboard is designed for a non-technical audience, so it emphasizes interactive comparisons rather than dense modeling output."
    )
    st.caption(
        "Dataset source: Stack Overflow Developer Survey 2025 — https://survey.stackoverflow.co/"
    )
    with st.expander("Methodology summary", expanded=False):
        st.write(
            "The analysis focuses on respondents who identified themselves as professional developers. "
            "The dataset was cleaned by removing duplicate responses, converting salary and job satisfaction fields to numeric values, "
            "documenting missingness, and capping salary at the 99th percentile for visualization clarity."
        )
    st.markdown(
        """
        **What to notice first**
        - Salary changes the most across **experience** and **country**.
        - Remote and flexible work patterns are linked to both **higher pay** and **slightly higher job satisfaction**.
        - Salary and job satisfaction move together only weakly, so they should not be treated as the same outcome.
        """
    )

    country_summary = (
        filtered_salary.groupby("Country", dropna=True)
        .agg(respondents=("ResponseId", "count"), median_salary=("ConvertedCompYearly", "median"))
        .query(f"respondents >= {MIN_COUNTRY_RESPONSES}")
        .sort_values("median_salary", ascending=False)
        .head(top_n_countries)
        .reset_index()
    )
    language_summary = (
        filtered_languages.groupby("Language", dropna=True)
        .agg(respondents=("ResponseId", "nunique"))
        .sort_values("respondents", ascending=False)
        .head(top_n_languages)
        .reset_index()
    )

    chart_col1, chart_col2 = st.columns(2)

    if not country_summary.empty:
        fig_country = px.bar(
            country_summary.sort_values("median_salary"),
            x="median_salary",
            y="Country",
            orientation="h",
            hover_data={"respondents": True, "median_salary": ":,.0f"},
            labels={"median_salary": "Median annual salary (USD)"},
            title="Country view: median salary in the filtered sample",
            color="median_salary",
            color_continuous_scale="YlOrRd",
        )
        fig_country.update_layout(coloraxis_showscale=False, height=520)
        chart_col1.plotly_chart(fig_country, use_container_width=True)
        chart_col1.caption(
            f"Showing {len(country_summary)} countries. The chart only includes countries with at least {MIN_COUNTRY_RESPONSES} salary responses after filtering."
        )
    else:
        chart_col1.info("Not enough salary data for the current country view.")

    if not language_summary.empty:
        fig_language = px.bar(
            language_summary.sort_values("respondents"),
            x="respondents",
            y="Language",
            orientation="h",
            labels={"respondents": "Number of respondents"},
            title="Most common languages in the filtered sample",
            color="respondents",
            color_continuous_scale="Tealgrn",
        )
        fig_language.update_layout(coloraxis_showscale=False, height=520)
        chart_col2.plotly_chart(fig_language, use_container_width=True)
    else:
        chart_col2.info("No language responses match the current filters.")

    st.markdown(
        """
        **Overview takeaway:** Experience and geography still drive the strongest salary differences, while remote-work patterns appear more closely tied to both pay and perceived job quality.
        """
    )

with tab_salary:
    st.subheader("Interactive salary views")
    st.write(
        "This view focuses on compensation patterns. Use the filters to compare salary distributions across work arrangements, experience groups, and countries."
    )
    st.info(
        "Recommended use: start with the remote-work comparison, then switch to the salary-vs-satisfaction view to see whether higher pay actually maps cleanly onto happier developers."
    )

    salary_view = st.radio(
        "Salary chart",
        options=["Remote work comparison", "Salary vs. job satisfaction", "Country drill-down"],
        horizontal=True,
    )

    if salary_view == "Remote work comparison":
        chart_data = filtered_salary.dropna(subset=["RemoteWork"]).copy()
        if chart_data.empty:
            st.warning("No salary and remote-work responses match the current filters.")
        else:
            fig = px.box(
                chart_data,
                x="RemoteWork",
                y="salary_capped",
                color="RemoteWork",
                points="outliers",
                labels={
                    "RemoteWork": "Work arrangement",
                    "salary_capped": "Annual salary (USD, capped at 99th percentile)",
                },
                title="Salary distribution by work arrangement",
                hover_data=["Country", "experience_bin", "EdLevel"],
            )
            fig.update_layout(showlegend=False, height=560)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Interactive View 1: Hover to inspect distributions and compare the spread as well as the median.")
            st.markdown(
                """
                **Why this matters:** This chart helps separate a simple “remote workers earn more” claim from the fuller distribution. It shows typical salary and spread, not just one average.
                """
            )

    elif salary_view == "Salary vs. job satisfaction":
        chart_data = filtered_scatter.copy()
        if chart_data.empty:
            st.warning("No joint salary and job satisfaction responses match the current filters.")
        else:
            fig = px.scatter(
                chart_data.sample(min(6000, len(chart_data)), random_state=42),
                x="JobSat",
                y="ConvertedCompYearly",
                color="experience_bin",
                size="language_count",
                hover_data=["Country", "RemoteWork", "DevType"],
                labels={"JobSat": "Job satisfaction (0-10)", "ConvertedCompYearly": "Annual salary (USD)"},
                title="Salary vs. job satisfaction",
            )
            fig.update_layout(height=560)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Interactive View 2: This scatterplot supports drill-down into how salary and job satisfaction vary together by experience.")
            st.markdown(
                """
                **Why this matters:** If salary alone explained job satisfaction, the points would form a much tighter upward pattern. Instead, the relationship is positive but still loose.
                """
            )

    else:
        chart_data = (
            filtered_salary.groupby("Country", dropna=True)
            .agg(respondents=("ResponseId", "count"), median_salary=("ConvertedCompYearly", "median"))
            .query(f"respondents >= {MIN_COUNTRY_RESPONSES}")
            .sort_values("median_salary", ascending=False)
            .head(top_n_countries)
            .reset_index()
        )
        if chart_data.empty:
            st.warning("Not enough salary responses remain for a country drill-down.")
        else:
            fig = px.bar(
                chart_data,
                x="Country",
                y="median_salary",
                color="respondents",
                hover_data={"respondents": True, "median_salary": ":,.0f"},
                labels={"median_salary": "Median salary (USD)"},
                title="Top countries by median salary in the filtered sample",
            )
            fig.update_layout(height=560)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("This view keeps the country effect visible so users do not overinterpret a single global salary number.")
            st.markdown(
                """
                **Why this matters:** This is the main geographic reality check in the app. It reminds the audience that global salary comparisons need context.
                """
            )
            st.caption(
                f"Showing {len(chart_data)} countries. Only countries with at least {MIN_COUNTRY_RESPONSES} salary responses in the filtered data are included."
            )

with tab_satisfaction:
    st.subheader("Interactive job satisfaction views")
    st.write(
        "This view emphasizes the non-salary side of the project question by showing how job satisfaction changes across flexibility, experience, and location."
    )
    st.info(
        "Job satisfaction varies across work arrangements and experience levels, but the differences are smaller than the salary gaps shown elsewhere in the dashboard."
    )

    sat_col1, sat_col2 = st.columns(2)

    sat_remote = (
        filtered_jobsat.groupby("RemoteWork", dropna=True)
        .agg(respondents=("ResponseId", "count"), avg_jobsat=("JobSat", "mean"))
        .reset_index()
    )
    sat_remote["RemoteWork"] = pd.Categorical(sat_remote["RemoteWork"], categories=REMOTE_ORDER, ordered=True)
    sat_remote = sat_remote.sort_values("RemoteWork")

    if not sat_remote.empty:
        fig_sat_remote = px.bar(
            sat_remote,
            x="RemoteWork",
            y="avg_jobsat",
            color="respondents",
            text="avg_jobsat",
            hover_data={"respondents": True, "avg_jobsat": ":.2f"},
            labels={"avg_jobsat": "Average job satisfaction (0-10)", "RemoteWork": "Work arrangement"},
            title="Average job satisfaction by work arrangement",
        )
        fig_sat_remote.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_sat_remote.update_layout(height=500, yaxis_range=[0, 8.5], coloraxis_colorbar_title="Respondents")
        sat_col1.plotly_chart(fig_sat_remote, use_container_width=True)
        sat_col1.caption("Remote workers report the highest average satisfaction, but the gap is small.")
    else:
        sat_col1.info("No job-satisfaction responses match the current filters.")

    sat_experience = (
        filtered_jobsat.groupby("experience_bin", dropna=True)
        .agg(respondents=("ResponseId", "count"), avg_jobsat=("JobSat", "mean"))
        .reset_index()
        .sort_values("experience_bin")
    )
    if not sat_experience.empty:
        fig_sat_exp = px.line(
            sat_experience,
            x="experience_bin",
            y="avg_jobsat",
            markers=True,
            hover_data={"respondents": True, "avg_jobsat": ":.2f"},
            labels={"experience_bin": "Experience band", "avg_jobsat": "Average job satisfaction (0-10)"},
            title="Job satisfaction by experience band",
        )
        fig_sat_exp.update_layout(height=500)
        sat_col2.plotly_chart(fig_sat_exp, use_container_width=True)
        sat_col2.caption("Satisfaction rises slightly with experience, and the change is gradual.")
    else:
        sat_col2.info("No experience-based satisfaction data match the current filters.")

with tab_narrative:
    if NARRATIVE_PATH.exists():
        st.markdown(NARRATIVE_PATH.read_text())
    else:
        st.warning("Final narrative file not found.")
