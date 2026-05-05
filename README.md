# Stack Overflow Developer Survey Analysis

This project analyzes the 2025 Stack Overflow Developer Survey to answer one question:

**What factors appear to influence salary and job satisfaction among professional developers?**

The final submission includes a polished Streamlit dashboard, a final written narrative, and a supporting exploratory notebook. The project is designed for a non-technical audience, so the emphasis is on clear comparisons and practical interpretation rather than complex modeling.

## Final Deliverables

- Streamlit dashboard: `app.py`
- Final narrative (Markdown): `docs/final_narrative.md`
- Final narrative (PDF): `docs/Final_Narrative.pdf`
- Supporting EDA notebook: `notebooks/milestone_2_stackoverflow_eda.ipynb`

## Quick Start

The easiest way to view the final deliverable is to run the dashboard with the cleaned dataset already included in the repository:

```bash
git clone https://github.com/bellahavel/stack-overflow-developer-survey-analysis.git
cd stack-overflow-developer-survey-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown in Terminal, usually `http://localhost:8501`.

## Dataset

- Source: [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/)
- Dashboard input: `data/cleaned_stackoverflow_data.csv`
- Supporting schema file: `data/survey_results_schema.csv`

The repository includes a cleaned dataset that is small enough for GitHub and sufficient to reproduce the dashboard directly. The larger raw CSV was used during development and can still be used to rebuild the cleaned file if needed.

## Key Findings

- Salary rises most clearly with professional experience.
- Geography is one of the strongest drivers of salary differences.
- Remote and flexible work arrangements are associated with higher pay and slightly higher job satisfaction.
- Salary and job satisfaction are positively related, but only weakly.

## Reproducibility

There are two ways to reproduce this project:

### 1. Run the dashboard immediately

This is the easiest way to reproduce the project. The repository already includes `data/cleaned_stackoverflow_data.csv`, so the dashboard can be run without downloading any additional files.

```bash
git clone https://github.com/bellahavel/stack-overflow-developer-survey-analysis.git
cd stack-overflow-developer-survey-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### 2. Rebuild the cleaned dataset from the raw survey file

Use this option if you want to reproduce the cleaning pipeline from the original Stack Overflow survey data. First clone the repository, then download `survey_results_public.csv` and place it in the `data/` folder before running the cleaning script.

```bash
git clone https://github.com/bellahavel/stack-overflow-developer-survey-analysis.git
cd stack-overflow-developer-survey-analysis
# Place survey_results_public.csv in the data/ folder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/build_clean_dataset.py
streamlit run app.py
```

## Repository Structure

- `app.py`: final Streamlit dashboard
- `data/`: cleaned dataset and schema reference
- `docs/`: final written narrative
- `notebooks/`: supporting Milestone 2 cleaning and EDA notebook
- `src/`: data preparation code for the dashboard and cleaned dataset

## Project Notes

- The analysis keeps only respondents whose `MainBranch` is `I am a developer by profession`.
- Salary charts use a 99th-percentile cap so extreme outliers do not flatten the rest of the distribution.
- Country remains central in the dashboard because salary comparisons in a global survey can be misleading without geographic context.
