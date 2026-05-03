# PROJECT_CONTEXT

## 1. Project Overview

### Project title/topic
- **Stack Overflow Developer Survey Analysis**

### Main research question / analytical goal
- Main question: **What factors appear to influence salary and job satisfaction among professional developers?**
- The project explores how salary and job satisfaction vary with:
  - professional experience
  - work arrangement
  - geography / country
  - education
  - language usage breadth

### Intended audience
- Primarily a **non-technical audience**
- The dashboard and written narrative are intentionally designed to emphasize clear patterns, direct interpretation, and responsible caveats rather than complex modeling.

### Dataset source(s)
- Main source: **Stack Overflow Developer Survey 2025**
- URL: [https://survey.stackoverflow.co/](https://survey.stackoverflow.co/)
- Files currently in repo:
  - `data/cleaned_stackoverflow_data.csv` — cleaned GitHub-friendly dataset used by the dashboard
  - `data/survey_results_schema.csv` — schema file
  - `data/survey_results_public.csv` — raw CSV used locally during development; ignored by Git because of file size

### Why this project matters
- Developer salary is important, but salary alone does not explain job quality.
- Job satisfaction depends on more than pay and can vary with flexibility, role context, and experience.
- A large real-world developer survey allows workplace, demographic, and technical factors to be studied together.

---

## 2. Course Requirements for Milestone 4

Milestone 4 requires:
- final GitHub repository with complete code
- polished Streamlit dashboard
- final written narrative
- 7–10 minute in-class presentation with live dashboard demo

Presentation should cover:
- motivation
- methodology
- key findings
- limitations
- dashboard demo

Relevant rubric areas:
- Data Acquisition & Cleaning
- Exploratory Data Analysis
- Visualization Design
- Interactive Dashboard
- Data Storytelling & Communication
- Reproducibility & Code Quality

---

## 3. Repository Architecture

### Root-level structure
- `app.py`
  - Final Streamlit dashboard entry point
- `README.md`
  - Main GitHub landing page / run instructions / reproducibility notes
- `requirements.txt`
  - Python package dependencies
- `PROJECT_CONTEXT.md`
  - This portable project summary

### `data/`
- `cleaned_stackoverflow_data.csv`
  - Cleaned analysis dataset used directly by the dashboard
  - GitHub-safe size, currently about **7.18 MB**
- `survey_results_schema.csv`
  - Survey schema / metadata
- `survey_results_public.csv`
  - Raw large dataset used during development
  - Not tracked in GitHub due to size limit

### `docs/`
- `final_narrative.md`
  - Final written narrative source
- `Final_Narrative.pdf`
  - Final narrative PDF
- `.Rhistory`
  - Local artifact; ignored / not needed

### `notebooks/`
- `milestone_2_stackoverflow_eda.ipynb`
  - Supporting Milestone 2 EDA notebook
  - Contains cleaning rationale, 9 static charts, findings, hypotheses, and limitations

### `src/`
- `dashboard_data.py`
  - Shared data-preparation logic for the dashboard
- `build_clean_dataset.py`
  - Rebuilds `data/cleaned_stackoverflow_data.csv` from the raw survey file
- `export_narrative_pdf.py`
  - Builds PDF narrative files from Markdown using ReportLab

### Generated outputs / artifacts
- `figures/`
  - Static EDA PNGs from Milestone 2
  - Not necessary to run the final dashboard
- Various `.png` preview files in root
  - Local artifacts / screenshots, not part of final logic

### Which file runs the Streamlit dashboard
- `app.py`

### Which files handle cleaning, EDA, and visualization
- Cleaning logic reused by app: `src/dashboard_data.py`
- Build cleaned dataset: `src/build_clean_dataset.py`
- EDA notebook: `notebooks/milestone_2_stackoverflow_eda.ipynb`
- Dashboard visuals: `app.py`

---

## 4. Data Pipeline

### Raw data source
- Raw input comes from Stack Overflow Developer Survey 2025 public results CSV.
- Local raw file path during development:
  - `data/survey_results_public.csv`

### Cleaning steps
- Keep only respondents whose `MainBranch` is:
  - `I am a developer by profession`
- Remove duplicate rows by `ResponseId`
- Select only analysis-relevant columns:
  - `ResponseId`
  - `Age`
  - `EdLevel`
  - `WorkExp`
  - `YearsCode`
  - `DevType`
  - `OrgSize`
  - `RemoteWork`
  - `Country`
  - `LanguageHaveWorkedWith`
  - `ConvertedCompYearly`
  - `JobSat`

### Missing value handling
- Missing values are not globally dropped.
- Each visualization or filtered dataset uses only the rows needed for that view.
- This was an intentional design choice documented in Milestone 2 because salary and job satisfaction have meaningful nonresponse.

### Type conversions
- Converted to numeric with `pd.to_numeric(..., errors="coerce")`:
  - `WorkExp`
  - `YearsCode`
  - `ConvertedCompYearly`
  - `JobSat`

### Duplicate/outlier handling
- Duplicates removed by `ResponseId`
- Salary visualizations use a **99th percentile cap**
  - prevents extreme salaries from flattening the rest of the distribution
- Raw salary values are still used for summary logic where appropriate

### Feature engineering
- `experience_bin`
  - bins `WorkExp` into: `0-2`, `3-5`, `6-10`, `11-15`, `16-20`, `20+`
- `language_count`
  - number of reported languages from the multi-select language column
- `salary_k`
  - salary in thousands
- `salary_capped`
  - salary clipped at the 99th percentile
- `RemoteWork`
  - cast to ordered categorical with a defined display order

### Final cleaned datasets
- Primary dashboard dataset:
  - `data/cleaned_stackoverflow_data.csv`
- This file is intentionally lean:
  - professional-developer subset only
  - only needed columns
  - derived dashboard fields are recomputed at runtime by `dashboard_data.py`

---

## 5. Analysis and Findings

### Main EDA questions
- How is salary distributed among professional developers?
- How does salary vary by:
  - experience
  - remote work arrangement
  - education
  - country
- How does job satisfaction vary by:
  - remote work arrangement
  - experience
- How strongly are salary and job satisfaction related?
- Which languages are most common in the professional sample?

### Important visualizations already created
Milestone 2 notebook includes 9 static visualizations:
1. Salary distribution
2. Salary by remote work arrangement
3. Salary by experience
4. Salary by education
5. Salary by country
6. Top programming languages
7. Job satisfaction by remote work
8. Job satisfaction by experience
9. Salary vs. job satisfaction

### Key patterns / insights found
- **Experience is one of the strongest drivers of salary**
  - salary rises clearly across experience levels
- **Remote and flexible work are linked to higher salary**
  - remote groups tend to earn more than fully in-person groups
- **Remote and flexible work are also linked to slightly higher job satisfaction**
  - but the satisfaction gap is modest
- **Geography strongly affects salary**
  - country differences are large enough that global averages can mislead
- **Salary and job satisfaction are only weakly related**
  - higher salary helps somewhat, but it does not fully explain satisfaction
- **Developers typically use multiple languages**
  - common languages include JavaScript, HTML/CSS, SQL, Python, TypeScript

### Statistical reasoning / summaries
- Uses grouped medians, grouped means, distribution views, and scatterplots
- Explicitly frames the work as **associational**, not causal
- Uses salary percentile capping for responsible visualization
- Makes the geography confounder visible instead of hiding it

### Hypotheses / conclusions supported by data
- Salary is shaped most strongly by structural factors such as:
  - experience
  - geography
- Job satisfaction depends on a broader mix of:
  - compensation
  - flexibility
  - work context

---

## 6. Dashboard Details

### Streamlit layout / sections
File: `app.py`

Dashboard tabs:
- `Overview`
- `Salary Explorer`
- `Satisfaction Explorer`
- `Final Narrative`

### Sidebar filters / controls
- `Country` multiselect
- `Work arrangement` multiselect
- `Experience band` multiselect
- `Countries shown in geographic view` slider
  - **dynamic max**
  - max adjusts to the number of countries that actually qualify for the current filtered chart
- `Languages shown` slider

### Plotly visualizations included
Overview:
- Country median salary horizontal bar chart
- Top languages horizontal bar chart

Salary Explorer:
- Salary distribution by work arrangement (boxplot)
- Salary vs. job satisfaction (scatterplot)
- Country drill-down median salary (bar chart)

Satisfaction Explorer:
- Average job satisfaction by work arrangement (bar chart)
- Job satisfaction by experience band (line chart)

### User experience decisions
- Hero section at top to state the question clearly
- Clear dataset citation in Overview
- “How to read this dashboard” note in sidebar
- Methodology summary in Overview
- Short interpretation notes and captions near charts
- Dashboard language updated from “prototype” to final-project framing
- Layout intentionally designed for non-technical viewers

### Edge cases handled
- If filters remove all data, the app shows an error and stops cleanly
- If a specific chart has no data under the current filters, the app shows an informative warning/info box instead of crashing
- Country slider cannot exceed the number of countries the chart can actually show
- Country charts enforce a minimum sample size:
  - `MIN_COUNTRY_RESPONSES = 10`

### Recent dashboard fixes / changes
- Fixed `NameError: salary_cap is not defined` in `dashboard_data.py`
- Satisfaction section wording was simplified so it sounds audience-facing, not like speaker notes
- Each satisfaction chart now has its own short caption
- Country slider now dynamically limits max values instead of appearing broken
- Dataset citation added to the Overview tab

---

## 7. Written Narrative Status

### Current narrative structure
File:
- `docs/final_narrative.md`
- PDF version: `docs/Final_Narrative.pdf`

Structure:
- Research Question
- Findings
- Limitations and Next Steps

### Main story arc
- question
- cleaning / scoped professional-developer sample
- findings on experience, work arrangement, geography, salary vs satisfaction
- limitations
- final conclusion

### Assumptions and limitations included
- Observational and exploratory analysis only
- Associations, not causal claims
- Geography is a major confounder for salary
- Missing values in salary and job satisfaction
- Education / experience / region may overlap in ways that complicate interpretation

### What still needs polishing for final submission
At the time this file is created, the major narrative content is already in final shape.

Possible remaining polish areas:
- confirm final wording in dashboard matches final narrative exactly
- confirm final PDF is current after any last Markdown edits
- possibly remove the line `Bella Havel` from the dashboard display if the visual layout needs adjustment, but keep it in the PDF if desired

---

## 8. Reproducibility / Code Quality

### Required packages
Current `requirements.txt`:
- pandas
- numpy
- matplotlib
- seaborn
- jupyter
- nbformat
- streamlit
- plotly

Note:
- `reportlab` is used by `src/export_narrative_pdf.py`
- It is currently installed in `.venv`, but **not listed in `requirements.txt`**
- This is a known reproducibility gap and should likely be fixed by adding `reportlab` to `requirements.txt`

### How to run locally
From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Commands for setup and running Streamlit
Run app:

```bash
streamlit run app.py
```

Rebuild cleaned dataset from raw:

```bash
python src/build_clean_dataset.py
```

Generate PDF narratives:

```bash
python src/export_narrative_pdf.py
```

Open notebook:

```bash
jupyter notebook
```

### Known issues / bugs / hardcoded paths
- `reportlab` is missing from `requirements.txt` even though PDF export depends on it
- `app.py` currently points directly to:
  - `data/cleaned_stackoverflow_data.csv`
  - `docs/final_narrative.md`
  These are relative project paths and are acceptable, but any refactor should preserve this repo-relative approach
- Raw CSV is still present locally in `data/` but ignored by Git
- There are extra local artifact files in the working tree not intended for final GitHub display:
  - preview PNGs
  - `.DS_Store`
  - `.cache`
  - `.Rhistory`

### Files that should be in `.gitignore`
Current `.gitignore` includes:
- `.venv/`
- `__pycache__/`
- `.ipynb_checkpoints/`
- `*.pyc`
- `.DS_Store`
- `.Rhistory`
- `.cache/`
- `*.png`
- `figures/*.png`
- `data/survey_results_public.csv`

This is mostly correct for final submission.

---

## 9. Final Milestone 4 Checklist

### Already complete
- Final Streamlit dashboard exists and runs from `app.py`
- Final narrative exists in Markdown and PDF
- Supporting EDA notebook exists
- Cleaned GitHub-safe dataset exists and is used by the app
- README explains quick start and reproducibility
- GitHub repo exists at:
  - `https://github.com/bellahavel/stack-overflow-developer-survey-analysis`
- Dashboard includes multiple interactive Plotly views
- Dashboard handles empty states and dynamic country limits

### Still needs to be done
Priority items to verify before final submission:
1. **Push the latest local changes to GitHub**
   - especially:
     - `README.md`
     - `app.py`
     - `src/dashboard_data.py`
     - `src/build_clean_dataset.py`
     - `data/cleaned_stackoverflow_data.csv`
2. **Add `reportlab` to `requirements.txt`**
   - otherwise PDF export is not fully reproducible from a fresh clone
3. **Consider one final repo audit**
   - confirm only final-useful files are tracked
4. **Presentation preparation**
   - slides
   - speaker notes
   - dashboard demo order
   - likely Q&A

### Priority order for finishing the project
1. Fix reproducibility gap (`reportlab` in requirements)
2. Push latest code / README / cleaned dataset to GitHub
3. Do final GitHub repo audit
4. Prepare presentation slides and demo flow
5. Practice Q&A

### Specific next tasks for Codex to help with
If a new Codex session continues from here, the highest-value next tasks are:

1. **Check current Git status and push all unpushed final changes**
   - especially cleaned dataset + README + dashboard fixes

2. **Add `reportlab` to `requirements.txt`**
   - verify `pip install -r requirements.txt` fully supports:
     - app
     - notebook
     - PDF narrative export

3. **Run a final repository audit**
   - confirm tracked files are only:
     - final dashboard
     - cleaned dataset
     - schema
     - final narrative
     - notebook
     - required scripts
     - README / requirements / .gitignore

4. **Help create final presentation materials**
   - PowerPoint slide text
   - speaking script
   - demo order
   - likely professor/peer questions

5. **Optionally verify final app behavior**
   - rerun Streamlit
   - confirm no errors
   - confirm final dashboard text / notes / sliders look correct

---

## Quick Summary for a New Codex Chat

This repo is a CS final project analyzing the 2025 Stack Overflow Developer Survey. The final deliverable is a polished Streamlit dashboard (`app.py`) using a cleaned GitHub-safe dataset (`data/cleaned_stackoverflow_data.csv`) plus a final written narrative (`docs/final_narrative.md` and `docs/Final_Narrative.pdf`). The core finding is that salary is driven most strongly by experience and geography, while job satisfaction depends on a broader mix of pay, flexibility, and work context. The app is already functional and polished, but before final submission a new Codex session should verify GitHub is up to date, add `reportlab` to `requirements.txt`, and then focus on presentation preparation.
