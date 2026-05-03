from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


REMOTE_ORDER = [
    "In-person",
    "Hybrid (some remote, leans heavy to in-person)",
    "Hybrid (some in-person, leans heavy to flexibility)",
    "Remote",
    "Your choice (very flexible, you can come in when you want or just as needed)",
]

EXPERIENCE_LABELS = ["0-2", "3-5", "6-10", "11-15", "16-20", "20+"]


@dataclass(frozen=True)
class DashboardDataBundle:
    df: pd.DataFrame
    salary_df: pd.DataFrame
    jobsat_df: pd.DataFrame
    scatter_df: pd.DataFrame
    language_df: pd.DataFrame


def load_dashboard_data(csv_path: str) -> DashboardDataBundle:
    df = pd.read_csv(csv_path, low_memory=False)
    df = df[df["MainBranch"] == "I am a developer by profession"].copy()
    df = df.drop_duplicates(subset="ResponseId")

    keep_cols = [
        "ResponseId",
        "Age",
        "EdLevel",
        "WorkExp",
        "YearsCode",
        "DevType",
        "OrgSize",
        "RemoteWork",
        "Country",
        "LanguageHaveWorkedWith",
        "ConvertedCompYearly",
        "JobSat",
    ]
    df = df[keep_cols].copy()

    for col in ["WorkExp", "YearsCode", "ConvertedCompYearly", "JobSat"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["experience_bin"] = pd.cut(
        df["WorkExp"],
        bins=[0, 2, 5, 10, 15, 20, 50],
        labels=EXPERIENCE_LABELS,
        include_lowest=True,
    )
    df["experience_bin"] = pd.Categorical(df["experience_bin"], categories=EXPERIENCE_LABELS, ordered=True)

    df["language_count"] = df["LanguageHaveWorkedWith"].fillna("").str.split(";").apply(
        lambda values: len([value for value in values if value.strip()])
    )
    df["salary_k"] = df["ConvertedCompYearly"] / 1000
    salary_cap = df["ConvertedCompYearly"].quantile(0.99)
    df["salary_capped"] = df["ConvertedCompYearly"].clip(upper=salary_cap)
    df["RemoteWork"] = pd.Categorical(df["RemoteWork"], categories=REMOTE_ORDER, ordered=True)

    salary_df = df[df["ConvertedCompYearly"].notna()].copy()
    jobsat_df = df[df["JobSat"].notna()].copy()
    scatter_df = df[df["ConvertedCompYearly"].notna() & df["JobSat"].notna()].copy()
    scatter_df = scatter_df[scatter_df["ConvertedCompYearly"] <= salary_cap].copy()

    language_df = (
        df[["ResponseId", "Country", "RemoteWork", "experience_bin", "ConvertedCompYearly", "JobSat", "LanguageHaveWorkedWith"]]
        .dropna(subset=["LanguageHaveWorkedWith"])
        .assign(Language=lambda frame: frame["LanguageHaveWorkedWith"].str.split(";"))
        .explode("Language")
    )
    language_df["Language"] = language_df["Language"].str.strip()
    language_df = language_df[language_df["Language"].ne("")]

    return DashboardDataBundle(
        df=df,
        salary_df=salary_df,
        jobsat_df=jobsat_df,
        scatter_df=scatter_df,
        language_df=language_df,
    )


def filter_frame(
    frame: pd.DataFrame,
    countries: list[str],
    remote_options: list[str],
    experience_bins: list[str],
) -> pd.DataFrame:
    filtered = frame.copy()
    if countries:
        filtered = filtered[filtered["Country"].isin(countries)]
    if remote_options:
        filtered = filtered[filtered["RemoteWork"].astype(str).isin(remote_options)]
    if experience_bins and "experience_bin" in filtered.columns:
        filtered = filtered[filtered["experience_bin"].astype(str).isin(experience_bins)]
    return filtered


def salary_summary(frame: pd.DataFrame) -> dict[str, float]:
    if frame.empty:
        return {
            "responses": 0,
            "median_salary": np.nan,
            "median_jobsat": np.nan,
            "median_languages": np.nan,
        }
    return {
        "responses": int(len(frame)),
        "median_salary": float(frame["ConvertedCompYearly"].median()) if frame["ConvertedCompYearly"].notna().any() else np.nan,
        "median_jobsat": float(frame["JobSat"].median()) if frame["JobSat"].notna().any() else np.nan,
        "median_languages": float(frame["language_count"].median()) if frame["language_count"].notna().any() else np.nan,
    }
