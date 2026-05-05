from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
DATA_PATH = ROOT / "data" / "cleaned_stackoverflow_data.csv"
NARRATIVE_PATH = ROOT / "docs" / "final_narrative.md"


@st.cache_data(show_spinner=False)
def get_data():
    # Cache the cleaned data so the app does not reload everything on each click.
    return load_dashboard_data(str(DATA_PATH))


def mark_display_controls_dirty():
    # Reset overview display controls when the main filters change.
    st.session_state["reset_display_controls"] = True


def render_note(title: str, body: str):
    # Show a short context note in the same style across the app.
    st.markdown(
        f"""
        <div class="note-card">
        <strong>{title}</strong><br>
        {body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_takeaway(text: str):
    # Show the main message under a chart.
    st.markdown(
        f'<div class="takeaway"><strong>Takeaway:</strong> {text}</div>',
        unsafe_allow_html=True,
    )


def count_eligible_countries(frame: pd.DataFrame) -> int:
    # Count countries with enough salary responses to compare fairly.
    return (
        frame.groupby("Country", dropna=True)
        .agg(respondents=("ResponseId", "count"))
        .query(f"respondents >= {MIN_COUNTRY_RESPONSES}")
        .shape[0]
    )


def add_remote_work_labels(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    # Replace long survey labels with shorter chart labels.
    labeled = frame.copy()
    labeled["RemoteWorkLabel"] = labeled["RemoteWork"].map(REMOTE_DISPLAY_LABELS).fillna(
        labeled["RemoteWork"].astype(str)
    )
    active_labels = [
        label for label in REMOTE_DISPLAY_ORDER if label in labeled["RemoteWorkLabel"].dropna().unique()
    ]
    labeled["RemoteWorkLabel"] = pd.Categorical(
        labeled["RemoteWorkLabel"], categories=active_labels, ordered=True
    )
    return labeled, active_labels


bundle = get_data()
df = bundle.df
MIN_COUNTRY_RESPONSES = 10
# Shorter labels make the work arrangement charts easier to read.
REMOTE_DISPLAY_LABELS = {
    "In-person": "In-person",
    "Hybrid (some remote, leans heavy to in-person)": "Hybrid: mostly in-person",
    "Hybrid (some in-person, leans heavy to flexibility)": "Hybrid: mostly remote",
    "Remote": "Remote",
    "Your choice (very flexible, you can come in when you want or just as needed)": "Flexible / as-needed",
}
REMOTE_DISPLAY_ORDER = [
    "In-person",
    "Hybrid: mostly in-person",
    "Flexible / as-needed",
    "Hybrid: mostly remote",
    "Remote",
]

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
    .takeaway {
        margin-top: 0.35rem;
        margin-bottom: 0.2rem;
        color: #31333f;
        font-size: 1rem;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>What drives developer salary and job satisfaction?</h1>
        <p>This dashboard explores how experience, geography, and work arrangement shape pay and satisfaction.</p>
        <p><strong>Key insight:</strong> Salary is heavily influenced by country and experience, while satisfaction is only weakly tied to pay.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filters")
    st.markdown("**Geography**")
    default_countries = df["Country"].value_counts().head(8).index.tolist()
    selected_countries = st.multiselect(
        "Country",
        options=sorted(df["Country"].dropna().unique().tolist()),
        default=default_countries,
        help="Use country filters to avoid misleading global salary comparisons.",
        key="selected_countries",
        on_change=mark_display_controls_dirty,
    )
    st.markdown("**Work Context**")
    selected_remote = st.multiselect(
        "Work arrangement",
        options=REMOTE_ORDER,
        default=["Remote", "In-person", "Hybrid (some in-person, leans heavy to flexibility)"],
        key="selected_remote",
        on_change=mark_display_controls_dirty,
    )
    selected_experience = st.multiselect(
        "Experience band",
        options=EXPERIENCE_LABELS,
        default=EXPERIENCE_LABELS,
        key="selected_experience",
        on_change=mark_display_controls_dirty,
    )
    render_note(
        "How to read this dashboard",
        "Start with Overview for the big picture, then use Salary Explorer and Satisfaction Explorer to compare filtered groups.",
    )


filtered_df = filter_frame(df, selected_countries, selected_remote, selected_experience)
filtered_salary = filter_frame(bundle.salary_df, selected_countries, selected_remote, selected_experience)
filtered_jobsat = filter_frame(bundle.jobsat_df, selected_countries, selected_remote, selected_experience)
filtered_scatter = filter_frame(bundle.scatter_df, selected_countries, selected_remote, selected_experience)

# These top numbers give a fast summary of the filtered sample.
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
    "Median languages per developer",
    "N/A" if pd.isna(summary["median_languages"]) else f"{summary['median_languages']:.0f}",
)
metric_cols[0].caption("Across selected filters")
metric_cols[1].caption("Across selected filters")
metric_cols[2].caption("Across selected filters")
metric_cols[3].caption("Across selected filters")

render_note("Important", "Salary varies a lot by country. Use the country filter to compare fairly.")

if filtered_df.empty:
    st.error("No responses match the current filters. Broaden the country, work arrangement, or experience selections.")
    st.stop()

selected_section = st.radio(
    "Section",
    ["Overview", "Salary Explorer", "Satisfaction Explorer", "Final Narrative"],
    horizontal=True,
    label_visibility="collapsed",
)

with st.sidebar:
    if selected_section == "Overview":
        st.markdown("**Display Controls**")
        # Only let the country chart show places with enough salary data to compare fairly.
        eligible_country_count = count_eligible_countries(filtered_salary)
        country_slider_max = max(1, eligible_country_count)
        if st.session_state.get("reset_display_controls", True):
            st.session_state["top_n_countries"] = country_slider_max
            st.session_state["reset_display_controls"] = False

        if st.session_state.get("top_n_countries", country_slider_max) > country_slider_max:
            st.session_state["top_n_countries"] = country_slider_max

        if country_slider_max == 1:
            top_n_countries = 1
            st.caption("Countries shown in country salary chart: 1")
        else:
            top_n_countries = st.slider(
                "Countries shown in country salary chart",
                min_value=1,
                max_value=country_slider_max,
                key="top_n_countries",
            )
    else:
        top_n_countries = max(1, count_eligible_countries(filtered_salary))

if selected_section == "Overview":
    st.subheader("What this dashboard shows")
    st.write(
        "This overview highlights how salary and job satisfaction vary across country, experience, and work arrangement."
    )
    st.caption(
        "Dataset source: Stack Overflow Developer Survey 2025 — https://survey.stackoverflow.co/"
    )
    with st.expander("How the data was prepared", expanded=False):
        st.write(
            "The dashboard focuses on respondents who identified as professional developers. "
            "Duplicate responses were removed, salary and job satisfaction were converted to numeric values, "
            "and salary is capped at the 99th percentile in charts so extreme outliers do not flatten the rest of the view."
        )
    st.markdown(
        """
        **What to notice first**
        - Salary changes most with **experience** and **country**.
        - Remote work is linked to **slightly higher pay** and **satisfaction**.
        - Salary and satisfaction are only **weakly related**.
        """
    )
    st.write(
        "Start with the country chart, then use the other tabs to compare salary and satisfaction patterns in more detail."
    )

    country_summary = (
        filtered_salary.groupby("Country", dropna=True)
        .agg(respondents=("ResponseId", "count"), median_salary=("ConvertedCompYearly", "median"))
        .query(f"respondents >= {MIN_COUNTRY_RESPONSES}")
        .sort_values("median_salary", ascending=False)
        .head(top_n_countries)
        .reset_index()
    )
    if not country_summary.empty:
        fig_country = px.bar(
            country_summary.sort_values("median_salary"),
            x="median_salary",
            y="Country",
            orientation="h",
            text="median_salary",
            hover_data={"respondents": True, "median_salary": ":,.0f"},
            labels={"median_salary": "Median annual salary (USD)"},
            title=(
                "Median salary by country (filtered sample)"
                "<br><sup><span style='color:#7a7a7a;'>"
                f"Showing {len(country_summary)} countries; only countries with at least {MIN_COUNTRY_RESPONSES} salary responses are included."
                "</span></sup>"
            ),
            color="median_salary",
            color_continuous_scale="YlOrRd",
        )
        fig_country.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_country.update_layout(
            coloraxis_showscale=False,
            height=520,
            xaxis_range=[0, country_summary["median_salary"].max() * 1.16],
        )
        st.plotly_chart(fig_country, use_container_width=True)
        render_takeaway("Country and experience drive the largest salary differences in the dashboard.")
    else:
        st.info("Not enough salary data for the current country view.")

elif selected_section == "Salary Explorer":
    st.subheader("Interactive salary views")
    st.write(
        "This view focuses on compensation patterns. Use the filters to compare salary distributions across work arrangements, experience groups, and countries."
    )
    st.info(
        "Recommended use: start with the experience view to see the clearest salary progression, then use remote work and country views for added context."
    )

    salary_view = st.radio(
        "Salary chart",
        options=["Remote work comparison", "Experience comparison"],
        horizontal=True,
    )

    if salary_view == "Remote work comparison":
        chart_data = filtered_salary.dropna(subset=["RemoteWork"]).copy()
        if chart_data.empty:
            st.warning("No salary and remote-work responses match the current filters.")
        else:
            st.caption("For the clearest work-arrangement comparison, select one country at a time.")
            # Use simpler names and a fixed order so the chart is easier to read.
            chart_data, active_remote_labels = add_remote_work_labels(chart_data)
            remote_counts = (
                chart_data.groupby("RemoteWorkLabel", observed=False)
                .size()
                .reindex(active_remote_labels, fill_value=0)
            )
            fig = px.box(
                chart_data,
                x="RemoteWorkLabel",
                y="salary_capped",
                color="RemoteWorkLabel",
                points="outliers",
                labels={
                    "RemoteWorkLabel": "Work arrangement",
                    "salary_capped": "Annual salary (USD)",
                },
                title="Salary distribution by work arrangement (filtered sample)",
                hover_data=["Country", "experience_bin", "EdLevel"],
                category_orders={"RemoteWorkLabel": active_remote_labels},
                color_discrete_sequence=["#d8e6f3", "#a9cce3", "#7fb3d5", "#5499c7", "#21618c"],
            )
            fig.update_layout(showlegend=False, height=560)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "Group sizes: "
                + ", ".join(f"{label} (n={remote_counts[label]:,})" for label in active_remote_labels)
            )
            st.caption(
                "Note: salaries are capped at the 99th percentile to prevent extreme outliers from compressing the rest of the distribution."
            )
            render_takeaway("Remote and flexible arrangements trend higher, but country mix may influence the pattern.")

    elif salary_view == "Experience comparison":
        # One chart shows the middle salary in each band, and one shows the spread.
        salary_experience = (
            filtered_salary.dropna(subset=["experience_bin"])
            .groupby("experience_bin", dropna=True)
            .agg(median_salary=("ConvertedCompYearly", "median"), respondents=("ResponseId", "count"))
            .reset_index()
        )
        salary_experience["experience_bin"] = pd.Categorical(
            salary_experience["experience_bin"], categories=EXPERIENCE_LABELS, ordered=True
        )
        salary_experience = salary_experience.sort_values("experience_bin")
        salary_experience_dist = filtered_salary.dropna(subset=["experience_bin"]).copy()
        salary_experience_dist["experience_bin"] = pd.Categorical(
            salary_experience_dist["experience_bin"], categories=EXPERIENCE_LABELS, ordered=True
        )

        salary_col1, salary_col2 = st.columns(2)

        if salary_experience.empty:
            salary_col1.warning("No experience-based salary responses match the current filters.")
        else:
            fig_experience = px.bar(
                salary_experience,
                x="median_salary",
                y="experience_bin",
                orientation="h",
                text="median_salary",
                color_discrete_sequence=["#21618c"],
                hover_data={"respondents": True, "median_salary": ":,.0f"},
                labels={"experience_bin": "Experience band", "median_salary": "Median salary (USD)"},
                title="Median salary by experience band",
            )
            fig_experience.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig_experience.update_layout(
                height=560,
                xaxis_range=[0, salary_experience["median_salary"].max() * 1.18],
                coloraxis_showscale=False,
            )
            salary_col1.plotly_chart(fig_experience, use_container_width=True)
            salary_col1.markdown('<div class="takeaway"><strong>Takeaway:</strong> Median salary rises clearly with experience.</div>', unsafe_allow_html=True)
        if salary_experience_dist.empty:
            salary_col2.warning("No experience-based salary responses match the current filters.")
        else:
            fig_experience_box = px.box(
                salary_experience_dist,
                x="experience_bin",
                y="salary_capped",
                color_discrete_sequence=["#7fb3d5"],
                points="outliers",
                labels={
                    "experience_bin": "Experience band",
                    "salary_capped": "Annual salary (USD, capped at 99th percentile)",
                },
                title="Salary distribution by experience band (filtered sample)",
                hover_data=["Country", "RemoteWork", "EdLevel"],
                category_orders={"experience_bin": EXPERIENCE_LABELS},
            )
            fig_experience_box.update_layout(showlegend=False, height=560)
            salary_col2.plotly_chart(fig_experience_box, use_container_width=True)
            salary_col2.caption(
                "Salaries are capped at the 99th percentile to prevent extreme outliers from compressing the rest of the distribution."
            )
            salary_col2.markdown('<div class="takeaway"><strong>Takeaway:</strong> Salary rises with experience, but pay still varies widely within each band.</div>', unsafe_allow_html=True)

elif selected_section == "Satisfaction Explorer":
    st.subheader("Interactive job satisfaction views")
    st.write(
        "This page shows how job satisfaction changes across work arrangement and experience, and how those patterns compare with the stronger salary differences shown in Salary Explorer."
    )
    st.info(
        "Job satisfaction changes across groups, but much less than salary."
    )
    satisfaction_view = st.radio(
        "Satisfaction chart",
        options=["Satisfaction by work arrangement", "Satisfaction by experience", "Salary vs. job satisfaction"],
        horizontal=True,
    )

    sat_remote = (
        filtered_jobsat.groupby("RemoteWork", dropna=True)
        .agg(respondents=("ResponseId", "count"), avg_jobsat=("JobSat", "mean"))
        .reset_index()
    )
    sat_remote, _ = add_remote_work_labels(sat_remote)
    sat_remote = sat_remote.sort_values("avg_jobsat", ascending=False)

    sat_experience = (
        filtered_jobsat.groupby("experience_bin", dropna=True)
        .agg(respondents=("ResponseId", "count"), avg_jobsat=("JobSat", "mean"))
        .reset_index()
        .sort_values("experience_bin")
    )

    if satisfaction_view == "Satisfaction by work arrangement":
        if not sat_remote.empty:
            fig_sat_remote = px.bar(
                sat_remote,
                x="RemoteWorkLabel",
                y="avg_jobsat",
                text="avg_jobsat",
                hover_data={"respondents": True, "avg_jobsat": ":.2f"},
                labels={"avg_jobsat": "Average job satisfaction (0-10)", "RemoteWorkLabel": "Work arrangement"},
                title="Average job satisfaction by work arrangement",
                color_discrete_sequence=["#4f8f83"],
            )
            fig_sat_remote.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig_sat_remote.update_layout(height=500, yaxis_range=[0, 10], showlegend=False)
            st.plotly_chart(fig_sat_remote, use_container_width=True)
            render_takeaway("Satisfaction is slightly higher for remote and flexible arrangements, but the gap is small.")
        else:
            st.info("No job-satisfaction responses match the current filters.")
    elif satisfaction_view == "Satisfaction by experience":
        if not sat_experience.empty:
            fig_sat_exp = px.bar(
                sat_experience,
                x="experience_bin",
                y="avg_jobsat",
                text="avg_jobsat",
                hover_data={"respondents": True, "avg_jobsat": ":.2f"},
                labels={"experience_bin": "Experience band", "avg_jobsat": "Average job satisfaction (0-10)"},
                title="Job satisfaction by experience band",
                color_discrete_sequence=["#4f8f83"],
            )
            fig_sat_exp.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig_sat_exp.update_layout(height=500, yaxis_range=[0, 10], showlegend=False)
            st.plotly_chart(fig_sat_exp, use_container_width=True)
            render_takeaway("Satisfaction rises only slightly with experience.")
        else:
            st.info("No experience-based satisfaction data match the current filters.")
    else:
        chart_data = filtered_scatter.copy()
        if chart_data.empty:
            st.warning("No joint salary and job satisfaction responses match the current filters.")
        else:
            # Slight x-axis jitter keeps the points from stacking directly on top of each other.
            scatter_sample = chart_data.sample(min(4000, len(chart_data)), random_state=42).copy()
            scatter_sample["JobSatJitter"] = scatter_sample["JobSat"] + (
                pd.Series(range(len(scatter_sample)), index=scatter_sample.index).mod(7) - 3
            ) * 0.045
            salary_by_satisfaction = (
                chart_data.groupby("JobSat", dropna=True)
                .agg(median_salary=("ConvertedCompYearly", "median"), respondents=("ResponseId", "count"))
                .reset_index()
            )
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=scatter_sample["JobSatJitter"],
                    y=scatter_sample["ConvertedCompYearly"],
                    mode="markers",
                    name="Respondents",
                    marker={
                        "color": "#7fb3d5",
                        "size": 7,
                        "opacity": 0.22,
                        "line": {"width": 0},
                    },
                    customdata=scatter_sample[["Country", "RemoteWork", "experience_bin"]],
                    hovertemplate=(
                        "Job satisfaction: %{x:.1f}<br>"
                        "Annual salary: $%{y:,.0f}<br>"
                        "Country: %{customdata[0]}<br>"
                        "Work arrangement: %{customdata[1]}<br>"
                        "Experience band: %{customdata[2]}<extra></extra>"
                    ),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=salary_by_satisfaction["JobSat"],
                    y=salary_by_satisfaction["median_salary"],
                    mode="lines+markers",
                    name="Median salary",
                    line={"color": "#9c6644", "width": 3},
                    marker={"size": 7, "color": "#9c6644"},
                    customdata=salary_by_satisfaction[["respondents"]],
                    hovertemplate=(
                        "Job satisfaction: %{x:.0f}<br>"
                        "Median salary: $%{y:,.0f}<br>"
                        "Respondents: %{customdata[0]:,}<extra></extra>"
                    ),
                )
            )
            fig.update_layout(
                title="Salary vs. job satisfaction (filtered sample)",
                xaxis_title="Job satisfaction (0-10)",
                yaxis_title="Annual salary (USD)",
                height=560,
                showlegend=False,
            )
            fig.update_xaxes(range=[-0.5, 10.5], dtick=1)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "Each point is one respondent. The brown line shows the median salary at each satisfaction rating."
            )
            st.caption(
                "Salaries above the 99th percentile are excluded here so extreme outliers do not dominate the pattern."
            )
            render_takeaway("Higher satisfaction is linked to somewhat higher pay, but the relationship is weak.")

else:
    if NARRATIVE_PATH.exists():
        st.markdown(NARRATIVE_PATH.read_text())
    else:
        st.warning("Final narrative file not found.")
