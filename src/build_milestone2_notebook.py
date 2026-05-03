from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "milestone_2_stackoverflow_eda.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(text)


def code(text: str):
    return nbf.v4.new_code_cell(text)


def fig_md(path: str, alt: str):
    return nbf.v4.new_markdown_cell(f"![{alt}]({path})")


nb = nbf.v4.new_notebook()
nb["cells"] = [
    md(
        """# Milestone 2: Data Cleaning and EDA Notebook

## Stack Overflow Developer Survey Analysis

**Student topic:** Stack Overflow Developer Survey Analysis  
**Dataset source:** [Stack Overflow Developer Survey](https://survey.stackoverflow.co/)

### Project focus
This notebook analyzes the 2025 Stack Overflow Developer Survey to identify trends in programming languages, salaries, job satisfaction, and developer demographics. The guiding question is:

**What factors appear to influence developer salary and job satisfaction most strongly?**

To answer that question, this milestone focuses on a clean, reproducible exploratory analysis for professional developers and prepares hypotheses for the later dashboard stage.
"""
    ),
    code(
        """import os
import warnings
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str((Path.cwd().resolve() / ".cache" / "matplotlib")))
os.environ.setdefault("XDG_CACHE_HOME", str((Path.cwd().resolve() / ".cache")))

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

pd.set_option("display.max_columns", 200)
pd.set_option("display.max_rows", 100)
pd.set_option("display.max_colwidth", 120)

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (12, 7)
plt.rcParams["axes.titlesize"] = 18
plt.rcParams["axes.labelsize"] = 13

ROOT = Path.cwd().resolve().parent if Path.cwd().name == "notebooks" else Path.cwd().resolve()
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)

SURVEY_PATH = DATA_DIR / "survey_results_public.csv"
SCHEMA_PATH = DATA_DIR / "survey_results_schema.csv"
"""
    ),
    md(
        """## 1. Data Loading

This section loads the raw Stack Overflow survey responses and the schema file. The schema is useful when matching column names to survey questions, while the public results CSV is the main analysis dataset.
"""
    ),
    code(
        """df_raw = pd.read_csv(SURVEY_PATH, low_memory=False)
schema = pd.read_csv(SCHEMA_PATH)

print(f"Raw survey shape: {df_raw.shape[0]:,} rows x {df_raw.shape[1]:,} columns")
print(f"Schema shape: {schema.shape[0]:,} rows x {schema.shape[1]:,} columns")
df_raw.head(3)
"""
    ),
    md(
        """## 2. Cleaning Plan

To align the notebook with the project question and rubric, the cleaning pipeline makes several explicit choices:

1. Restrict the analysis to respondents who identified as **developers by profession**.
2. Remove duplicate responses based on `ResponseId`.
3. Convert salary, work experience, years coding, and job satisfaction columns to numeric types.
4. Create derived features for:
   - experience bands
   - salary in thousands
   - log salary
   - language count
   - job satisfaction band
5. Keep raw salary values for summary statistics, but create a **99th percentile capped** version for visualizations so extreme outliers do not flatten the rest of the data.

These choices improve interpretability without discarding the core structure of the original survey.
"""
    ),
    md(
        """### Why These Derived Features Matter

This notebook uses a few simple engineered variables to make the survey easier to interpret for a non-technical audience:

- **`experience_bin`** groups respondents into career stages so salary and satisfaction patterns are easier to compare than with raw year values alone.
- **`salary_capped`** preserves the overall salary distribution while preventing a small number of extremely large values from flattening every chart.
- **`language_count`** captures how broad a respondent's working toolkit is, which is more informative than only listing raw multi-select responses.
- **`jobsat_band`** turns the 0-10 satisfaction scale into broader low / mid / high groupings that can support later dashboard summaries.

These are lightweight feature-engineering steps, but they are analytically useful because they improve readability without changing the underlying survey responses.
"""
    ),
    code(
        """analysis_cols = [
    "ResponseId",
    "MainBranch",
    "Age",
    "EdLevel",
    "Employment",
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

df = df_raw[analysis_cols].copy()
df = df.drop_duplicates(subset="ResponseId")
df = df[df["MainBranch"] == "I am a developer by profession"].copy()

numeric_cols = ["WorkExp", "YearsCode", "ConvertedCompYearly", "JobSat"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["language_count"] = df["LanguageHaveWorkedWith"].fillna("").str.split(";").apply(
    lambda items: len([item for item in items if item.strip()])
)
df["salary_k"] = df["ConvertedCompYearly"] / 1000
df["log_salary"] = np.log10(df["ConvertedCompYearly"].where(df["ConvertedCompYearly"] > 0))

salary_cap = df["ConvertedCompYearly"].quantile(0.99)
df["salary_capped"] = df["ConvertedCompYearly"].clip(upper=salary_cap)

df["experience_bin"] = pd.cut(
    df["WorkExp"],
    bins=[0, 2, 5, 10, 15, 20, 50],
    labels=["0-2", "3-5", "6-10", "11-15", "16-20", "20+"],
    include_lowest=True,
)

df["jobsat_band"] = pd.cut(
    df["JobSat"],
    bins=[-0.1, 4, 7, 10],
    labels=["Low (0-4)", "Mid (5-7)", "High (8-10)"],
)

remote_order = [
    "In-person",
    "Hybrid (some remote, leans heavy to in-person)",
    "Hybrid (some in-person, leans heavy to flexibility)",
    "Remote",
    "Your choice (very flexible, you can come in when you want or just as needed)",
]

education_order = [
    "Primary/elementary school",
    "Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)",
    "Some college/university study without earning a degree",
    "Associate degree (A.A., A.S., etc.)",
    "Bachelor’s degree (B.A., B.S., B.Eng., etc.)",
    "Master’s degree (M.A., M.S., M.Eng., MBA, etc.)",
    "Professional degree (JD, MD, Ph.D, Ed.D, etc.)",
]

print(f"Professional developer subset: {df.shape[0]:,} rows")
print(f"Salary cap used for charts (99th percentile): ${salary_cap:,.0f}")
df.head(3)
"""
    ),
    md(
        """## 3. Missingness and Basic Quality Checks

Missing values are common in large surveys, so it is important to document where they appear. For milestone two, the analysis keeps the full professional-developer subset and lets each chart use the rows relevant to that question.
"""
    ),
    code(
        """missing_summary = (
    df[["Age", "EdLevel", "WorkExp", "YearsCode", "RemoteWork", "LanguageHaveWorkedWith", "ConvertedCompYearly", "JobSat"]]
    .isna()
    .mean()
    .sort_values(ascending=False)
    .mul(100)
    .round(1)
    .rename("missing_pct")
    .to_frame()
)
missing_summary
"""
    ),
    code(
        """raw_professional = df_raw[df_raw["MainBranch"] == "I am a developer by profession"].copy()
duplicate_count = int(raw_professional.duplicated(subset="ResponseId").sum())
salary_missing_pct = round(df["ConvertedCompYearly"].isna().mean() * 100, 1)
jobsat_missing_pct = round(df["JobSat"].isna().mean() * 100, 1)
remote_missing_pct = round(df["RemoteWork"].isna().mean() * 100, 1)

cleaning_decisions = pd.DataFrame(
    {
        "decision": [
            "Filter to professional developers",
            "Drop duplicate ResponseId values",
            "Convert experience, salary, and job satisfaction to numeric",
            "Use chart-specific filtering for missing values",
            "Cap salary at the 99th percentile for visualizations",
        ],
        "justification": [
            "This aligns the sample with the project question about professional developer salary and job satisfaction.",
            f"The professional subset contains {duplicate_count} duplicate response IDs; removing them avoids double-counting respondents.",
            "Survey exports can contain mixed types, so numeric conversion is needed before computing statistics or plotting.",
            f"Key variables have meaningful nonresponse, including salary ({salary_missing_pct}%), job satisfaction ({jobsat_missing_pct}%), and remote work ({remote_missing_pct}%). Keeping the full cleaned dataset and filtering only where needed preserves more information across the notebook.",
            f"Extremely high salaries compress the rest of the distribution. Capping charts at ${salary_cap:,.0f} preserves visibility for the bulk of respondents while leaving raw values available for summaries.",
        ],
    }
)

cleaning_decisions
"""
    ),
    md(
        """### Cleaning Decision Notes

The cleaning choices above are intended to be transparent rather than automatic:

- The notebook **does not drop all rows with missing values at once** because different questions have different nonresponse rates.
- Salary values remain in their raw form for summary statistics, but chart displays use a capped version to reduce distortion from extreme outliers.
- Because this is a global survey, missingness and salary differences can reflect both respondent choice and structural differences across countries and roles.
"""
    ),
    code(
        """summary_stats = pd.Series({
    "professional_responses": len(df),
    "responses_with_salary": int(df["ConvertedCompYearly"].notna().sum()),
    "responses_with_job_sat": int(df["JobSat"].notna().sum()),
    "median_salary": float(df["ConvertedCompYearly"].median()),
    "mean_salary": float(df["ConvertedCompYearly"].mean()),
    "median_job_satisfaction": float(df["JobSat"].median()),
    "mean_job_satisfaction": float(df["JobSat"].mean()),
    "median_work_experience_years": float(df["WorkExp"].median()),
    "median_languages_used": float(df["language_count"].median()),
}).round(2)

summary_stats.to_frame("value")
"""
    ),
    md(
        """## 4. Exploratory Data Analysis

The following visualizations focus on salary, job satisfaction, experience, education, remote work, and language usage. Each plot is accompanied by a short interpretation written for a non-technical audience.
"""
    ),
    md(
        """### EDA Roadmap

The exploratory analysis is organized in three stages:

1. Understand the shape of compensation overall.
2. Compare compensation and satisfaction across major explanatory factors such as experience, education, remote work, and country.
3. Translate the visual patterns into early findings and testable hypotheses for the dashboard milestone.
"""
    ),
    code(
        """salary_plot = df[df["ConvertedCompYearly"].notna()].copy()

fig, ax = plt.subplots()
sns.histplot(salary_plot["salary_capped"], bins=40, color="#8c2d04", ax=ax)
ax.set_title("Distribution of Annual Compensation for Professional Developers")
ax.set_xlabel("Annual compensation in USD (capped at 99th percentile)")
ax.set_ylabel("Number of respondents")
ax.ticklabel_format(style="plain", axis="x")
fig.tight_layout()
fig.savefig(FIG_DIR / "01_salary_distribution.png", dpi=200, bbox_inches="tight")
plt.show()
"""
    ),
    md(
        """**Figure 1 interpretation:** Annual compensation is strongly right-skewed. Most professional developers in the survey cluster well below the very highest salaries, which justifies capping the display at the 99th percentile so the typical range remains readable.
"""
    ),
    md(
        """**Analytical note:** This first chart establishes that salary is not normally distributed, so medians are usually more informative than means in the comparisons that follow.
"""
    ),
    fig_md("../figures/01_salary_distribution.png", "Figure 1: Salary distribution"),
    code(
        """remote_salary = df[df["ConvertedCompYearly"].notna() & df["RemoteWork"].notna()].copy()
remote_salary["RemoteWork"] = pd.Categorical(remote_salary["RemoteWork"], categories=remote_order, ordered=True)

fig, ax = plt.subplots(figsize=(13, 7))
sns.boxplot(
    data=remote_salary,
    y="RemoteWork",
    x="salary_capped",
    palette="YlOrBr",
    showfliers=False,
    ax=ax,
)
ax.set_title("Salary Distribution by Work Arrangement")
ax.set_xlabel("Annual compensation in USD (capped at 99th percentile)")
ax.set_ylabel("")
ax.ticklabel_format(style="plain", axis="x")
fig.tight_layout()
fig.savefig(FIG_DIR / "02_salary_by_remotework.png", dpi=200, bbox_inches="tight")
plt.show()
"""
    ),
    md(
        """**Figure 2 interpretation:** Fully remote and highly flexible arrangements tend to have higher salary distributions than fully in-person work. This suggests that workplace flexibility may be associated with better compensation, though the survey alone does not prove causation.
"""
    ),
    md(
        """**Analytical note:** Because this is a boxplot rather than a simple average bar chart, it shows both typical salary levels and spread within each work arrangement.
"""
    ),
    fig_md("../figures/02_salary_by_remotework.png", "Figure 2: Salary by remote work"),
    code(
        """exp_salary = (
    df[df["ConvertedCompYearly"].notna() & df["experience_bin"].notna()]
    .groupby("experience_bin", observed=False)["ConvertedCompYearly"]
    .median()
    .reset_index()
)

fig, ax = plt.subplots()
sns.barplot(data=exp_salary, x="experience_bin", y="ConvertedCompYearly", color="#1f78b4", ax=ax)
ax.set_title("Median Salary by Professional Experience")
ax.set_xlabel("Years of professional experience")
ax.set_ylabel("Median annual compensation (USD)")
ax.ticklabel_format(style="plain", axis="y")
fig.tight_layout()
fig.savefig(FIG_DIR / "03_salary_by_experience.png", dpi=200, bbox_inches="tight")
plt.show()
exp_salary
"""
    ),
    md(
        """**Figure 3 interpretation:** Median salary rises sharply with experience, especially moving from early-career developers into the 6 to 15 year range. Experience appears to be one of the strongest drivers of pay in the dataset.
"""
    ),
    md(
        """**Analytical note:** The use of experience bands here is deliberate. Grouping raw years into career stages makes the trend easier to interpret and is one of the notebook's main feature-engineering steps.
"""
    ),
    fig_md("../figures/03_salary_by_experience.png", "Figure 3: Salary by experience"),
    code(
        """edu_salary = (
    df[df["ConvertedCompYearly"].notna() & df["EdLevel"].notna()]
    .groupby("EdLevel")["ConvertedCompYearly"]
    .median()
    .reindex(education_order)
    .dropna()
    .reset_index()
)

fig, ax = plt.subplots(figsize=(13, 7))
sns.barplot(data=edu_salary, y="EdLevel", x="ConvertedCompYearly", palette="crest", ax=ax)
ax.set_title("Median Salary by Education Level")
ax.set_xlabel("Median annual compensation (USD)")
ax.set_ylabel("")
ax.ticklabel_format(style="plain", axis="x")
fig.tight_layout()
fig.savefig(FIG_DIR / "04_salary_by_education.png", dpi=200, bbox_inches="tight")
plt.show()
edu_salary
"""
    ),
    md(
        """**Figure 4 interpretation:** Higher education levels generally correspond to higher median salaries, with professional and master’s degrees at the top. The differences are not extreme enough to imply education is the only factor, but education does appear positively associated with compensation.
"""
    ),
    md(
        """**Analytical note:** Education appears to matter, but the separation between groups is smaller than the experience trend, suggesting that education is only one part of the compensation story.
"""
    ),
    fig_md("../figures/04_salary_by_education.png", "Figure 4: Salary by education"),
    code(
        """country_salary = (
    df[df["ConvertedCompYearly"].notna() & df["Country"].notna()]
    .groupby("Country")
    .agg(
        respondents=("ResponseId", "count"),
        median_salary=("ConvertedCompYearly", "median"),
    )
    .query("respondents >= 100")
    .sort_values("median_salary", ascending=False)
    .head(12)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(13, 8))
sns.barplot(data=country_salary, y="Country", x="median_salary", palette="flare", ax=ax)
ax.set_title("Median Salary by Country (Countries With at Least 100 Responses)")
ax.set_xlabel("Median annual compensation (USD)")
ax.set_ylabel("")
ax.ticklabel_format(style="plain", axis="x")
fig.tight_layout()
fig.savefig(FIG_DIR / "05_salary_by_country.png", dpi=200, bbox_inches="tight")
plt.show()
country_salary
"""
    ),
    md(
        """**Figure 5 interpretation:** Country-level salary differences are large, which means any global salary comparison should be interpreted carefully. This plot shows that geography is a major confounder, so differences by education, language, or remote work may partly reflect where developers live and work.
"""
    ),
    md(
        """**Analytical note:** This is an important control-style check for the notebook. It does not solve the geography issue completely, but it makes the biggest global salary limitation visible rather than hidden.
"""
    ),
    fig_md("../figures/05_salary_by_country.png", "Figure 5: Salary by country"),
    code(
        """lang_counts = (
    df["LanguageHaveWorkedWith"]
    .dropna()
    .str.split(";")
    .explode()
    .str.strip()
    .value_counts()
    .head(10)
    .sort_values()
)

fig, ax = plt.subplots(figsize=(12, 8))
lang_counts.plot(kind="barh", color="#238b45", ax=ax)
ax.set_title("Most Common Programming Languages Among Professional Developers")
ax.set_xlabel("Number of respondents")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig(FIG_DIR / "06_top_languages.png", dpi=200, bbox_inches="tight")
plt.show()
lang_counts
"""
    ),
    md(
        """**Figure 6 interpretation:** JavaScript, HTML/CSS, SQL, Python, and shell scripting dominate the language stack for professional developers. This reinforces that modern developer work is often multi-language rather than centered on a single tool.
"""
    ),
    md(
        """**Analytical note:** This chart is descriptive rather than causal, but it helps anchor the rest of the project by showing which tools define the most common professional developer environments.
"""
    ),
    fig_md("../figures/06_top_languages.png", "Figure 6: Top languages"),
    code(
        """jobsat_remote = df[df["JobSat"].notna() & df["RemoteWork"].notna()].copy()
jobsat_remote["RemoteWork"] = pd.Categorical(jobsat_remote["RemoteWork"], categories=remote_order, ordered=True)

fig, ax = plt.subplots(figsize=(13, 7))
sns.boxplot(data=jobsat_remote, y="RemoteWork", x="JobSat", palette="Set2", showfliers=False, ax=ax)
ax.set_title("Job Satisfaction by Work Arrangement")
ax.set_xlabel("Job satisfaction score (0-10)")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig(FIG_DIR / "07_jobsat_by_remotework.png", dpi=200, bbox_inches="tight")
plt.show()
"""
    ),
    md(
        """**Figure 7 interpretation:** Developers in remote or highly flexible arrangements report somewhat higher job satisfaction than in-person respondents. The effect is noticeable but not huge, which suggests that flexibility matters, but it is not the only source of satisfaction.
"""
    ),
    md(
        """**Analytical note:** The smaller gap here, compared with salary differences, suggests that work arrangement may influence developer experience, but job satisfaction is likely shaped by multiple overlapping factors.
"""
    ),
    fig_md("../figures/07_jobsat_by_remotework.png", "Figure 7: Job satisfaction by remote work"),
    code(
        """jobsat_exp = (
    df[df["JobSat"].notna() & df["experience_bin"].notna()]
    .groupby("experience_bin", observed=False)["JobSat"]
    .mean()
    .reset_index()
)

fig, ax = plt.subplots()
sns.lineplot(data=jobsat_exp, x="experience_bin", y="JobSat", marker="o", linewidth=3, color="#6a3d9a", ax=ax)
ax.set_title("Average Job Satisfaction by Experience Band")
ax.set_xlabel("Years of professional experience")
ax.set_ylabel("Average job satisfaction (0-10)")
ax.set_ylim(6.7, 7.5)
fig.tight_layout()
fig.savefig(FIG_DIR / "08_jobsat_by_experience.png", dpi=200, bbox_inches="tight")
plt.show()
jobsat_exp
"""
    ),
    md(
        """**Figure 8 interpretation:** Job satisfaction tends to rise gradually with experience, although the increase is much smaller than the salary increase. This suggests that experience may improve role fit and stability, but satisfaction is influenced by more than seniority alone.
"""
    ),
    md(
        """**Analytical note:** This result is useful because it separates salary growth from satisfaction growth. The two move in the same direction, but not at the same rate.
"""
    ),
    fig_md("../figures/08_jobsat_by_experience.png", "Figure 8: Job satisfaction by experience"),
    code(
        """sat_salary = df[df["ConvertedCompYearly"].notna() & df["JobSat"].notna()].copy()
sat_salary = sat_salary[sat_salary["ConvertedCompYearly"] <= sat_salary["ConvertedCompYearly"].quantile(0.99)]

fig, ax = plt.subplots()
sns.regplot(
    data=sat_salary.sample(min(len(sat_salary), 8000), random_state=42),
    x="JobSat",
    y="ConvertedCompYearly",
    scatter_kws={"alpha": 0.15, "s": 25, "color": "#1b9e77"},
    line_kws={"color": "#d95f02", "linewidth": 3},
    ax=ax,
)
ax.set_title("Salary vs. Job Satisfaction")
ax.set_xlabel("Job satisfaction score (0-10)")
ax.set_ylabel("Annual compensation in USD")
ax.ticklabel_format(style="plain", axis="y")
fig.tight_layout()
fig.savefig(FIG_DIR / "09_salary_vs_jobsat.png", dpi=200, bbox_inches="tight")
plt.show()

print("Correlation between salary and job satisfaction:", round(sat_salary["ConvertedCompYearly"].corr(sat_salary["JobSat"]), 3))
"""
    ),
    md(
        """**Figure 9 interpretation:** Salary and job satisfaction have only a weak positive relationship in this survey. Higher pay helps somewhat, but it does not fully explain whether developers feel satisfied in their jobs.
"""
    ),
    md(
        """**Analytical note:** The weak relationship here supports the project's broader motivation: salary is important, but it should not be treated as a complete proxy for developer well-being.
"""
    ),
    fig_md("../figures/09_salary_vs_jobsat.png", "Figure 9: Salary vs job satisfaction"),
    md(
        """### Transition to Findings

Taken together, the charts suggest that compensation is shaped most strongly by structural factors such as experience and geography, while job satisfaction appears to depend on a broader mix of salary, flexibility, and role context. The next section summarizes those patterns as concise findings.
"""
    ),
    md(
        """## 5. Final Summary of Initial Findings

Based on the exploratory analysis above, several early patterns stand out:

- **Experience is the clearest salary signal** in the notebook. Median pay increases substantially across experience bands.
- **Remote and flexible work arrangements are associated with both higher salary and slightly higher job satisfaction** compared with fully in-person work.
- **Country is a major driver of salary differences** in the global survey, so salary comparisons across other categories must be interpreted with geographic caution.
- **Education appears to matter for salary**, but the effect is smaller than the experience effect.
- **Compensation and job satisfaction are not the same thing.** The relationship is positive but weak, which implies non-salary factors still matter a lot.
- **Developers work across multiple languages**, with JavaScript, SQL, Python, and TypeScript appearing especially common in the professional subset.
"""
    ),
    md(
        """## 6. Hypotheses for Further Exploration

These EDA results motivate several hypotheses for Milestone 3 and the final dashboard:

1. Developers with more professional experience will earn more even after controlling for education level.
2. Remote-work flexibility will remain positively associated with job satisfaction even within similar experience groups.
3. Salary differences by language will weaken once experience, developer role, and country are considered.
4. Job satisfaction will be influenced more by work arrangement and role context than by salary alone.
"""
    ),
    md(
        """## 7. Limitations

- The survey is observational and self-reported, so the notebook identifies associations rather than causal effects.
- Salary values depend heavily on geographic context, taxation, and local labor markets; the new country-level chart shows that geography is one of the strongest sources of variation in the dataset.
- Missing values are non-random for some questions, especially salary and satisfaction.
- Multi-select language fields describe breadth of usage, not intensity of usage.

Overall, this milestone establishes a clean and reproducible baseline for the later dashboard prototype and written narrative.
"""
    ),
]

nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3",
    },
}

NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, NOTEBOOK_PATH)
print(f"Wrote notebook to {NOTEBOOK_PATH}")
