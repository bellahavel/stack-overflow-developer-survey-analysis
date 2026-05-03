# Stack Overflow Developer Survey Analysis

This project analyzes the 2025 Stack Overflow Developer Survey to answer one question:

**What factors appear to influence salary and job satisfaction among professional developers?**

The final submission includes a Streamlit dashboard, a final written narrative, and a supporting EDA notebook.

## Final Deliverables

- Interactive dashboard: `app.py`
- Final narrative (Markdown): `docs/final_narrative.md`
- Final narrative (PDF): `docs/Final_Narrative.pdf`
- Supporting EDA notebook: `notebooks/milestone_2_stackoverflow_eda.ipynb`

## Quick Start

Run the dashboard with:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown in Terminal, usually `http://localhost:8501`.

## Dataset

- Source: [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/)
- Dashboard input: `data/cleaned_stackoverflow_data.csv`

The repository includes a cleaned dataset that is small enough for GitHub and sufficient to reproduce the dashboard. The larger raw CSV was used during development and can be used to rebuild the cleaned file if needed.

## Reproducibility

To rebuild the cleaned dataset from the raw survey file, place `survey_results_public.csv` in `data/` and run:

```bash
.venv/bin/python src/build_clean_dataset.py
```

To open the supporting notebook:

```bash
.venv/bin/jupyter notebook
```

## Repository Structure

- `app.py`: final Streamlit dashboard
- `data/`: cleaned dataset and survey schema
- `docs/`: final narrative deliverables
- `notebooks/`: milestone analysis notebook
- `src/`: data-preparation and export utilities

## Project Notes

- The analysis keeps only respondents whose `MainBranch` is `I am a developer by profession`.
- Salary charts use a 99th-percentile cap so extreme outliers do not flatten the rest of the distribution.
- Country remains central in the dashboard because salary comparisons in a global survey can be misleading without geographic context.
