Bella Havel

# Final Project Presentation Outline

## Slide 1: Title

**Stack Overflow Developer Survey Analysis**  
CS 4379G Final Project  
Bella Havel

**Say:**
- This project analyzes the 2025 Stack Overflow Developer Survey.
- The goal is to understand what appears to influence salary and job satisfaction among professional developers.

---

## Slide 2: Motivation

**Why this topic matters**
- Developer salary is important, but salary alone does not explain job quality.
- Job satisfaction is influenced by multiple factors, including flexibility and experience.
- A large real-world survey makes it possible to explore both technical and workplace trends together.

**Say:**
- I wanted to study both compensation and quality of work experience.
- The Stack Overflow survey is a strong dataset because it includes salary, satisfaction, work arrangement, education, experience, and languages.

---

## Slide 3: Research Question

**Main question**
- What factors appear to influence salary and job satisfaction among professional developers?

**Audience**
- Non-technical audience
- Focus on clear patterns rather than advanced modeling

**Say:**
- I designed both the notebook and dashboard so the results would be understandable to someone without a deep statistics background.

---

## Slide 4: Dataset

**Dataset source**
- Stack Overflow Developer Survey 2025
- Source: https://survey.stackoverflow.co/

**Why it fits the project**
- Large international sample
- Includes salary, job satisfaction, country, experience, education, and language usage

**Say:**
- This dataset is especially useful because it combines career, demographic, and technical variables in one place.

---

## Slide 5: Methodology

**Cleaning and preprocessing**
- Kept only respondents who identified as professional developers
- Removed duplicate responses
- Converted salary, experience, and satisfaction to numeric fields
- Documented missing data
- Capped salary at the 99th percentile for visualization

**Feature engineering**
- Experience bands
- Language count
- Capped salary field

**Say:**
- These choices made the analysis easier to interpret while keeping it tied to the original survey data.

---

## Slide 6: Exploratory Analysis

**What I explored**
- Salary distributions
- Salary by experience
- Salary by work arrangement
- Salary by education
- Salary by country
- Job satisfaction by work arrangement
- Job satisfaction by experience
- Salary vs. job satisfaction

**Say:**
- The exploratory analysis showed that experience, work arrangement, and geography were the most important patterns to follow into the dashboard.

---

## Slide 7: Key Finding 1

**Experience is one of the strongest salary drivers**
- Salary rises substantially across experience levels
- The clearest jump appears between early-career and mid-career developers

**Say:**
- Experience had one of the strongest and most consistent relationships with salary in the project.

---

## Slide 8: Key Finding 2

**Remote and flexible work are linked to higher salary**
- Remote workers generally report higher salaries than fully in-person workers
- Remote and flexible groups also report slightly higher job satisfaction

**Say:**
- The salary difference is more noticeable than the satisfaction difference, which suggests flexibility helps, but does not fully determine satisfaction.

---

## Slide 9: Key Finding 3

**Geography strongly affects salary**
- Salary levels vary substantially across countries
- Global averages can be misleading without geographic context

**Say:**
- This was one of the most important limitations and one of the reasons country filters are central in the dashboard.

---

## Slide 10: Key Finding 4

**Salary and job satisfaction are only weakly related**
- Higher salary is associated with slightly higher satisfaction
- But salary does not fully explain job satisfaction

**Say:**
- This is important because it shows that compensation matters, but it is not a complete measure of well-being.

---

## Slide 11: Dashboard Demo

**Demo plan**
- Overview tab
- Salary Explorer
- Satisfaction Explorer
- Final Narrative tab

**Say:**
- Start with the overview and country context.
- Then show salary by work arrangement and salary vs. job satisfaction.
- End by showing that satisfaction changes more gradually than salary.

---

## Slide 12: Limitations

**Important limitations**
- Observational survey data, not causal analysis
- Salary is heavily influenced by geography
- Missing values in salary and job satisfaction
- Multi-select language fields show breadth, not intensity

**Say:**
- These results show patterns and associations, but they should not be interpreted as proof of causation.

---

## Slide 13: Final Conclusion

**Main conclusion**
- Salary is driven most strongly by structural factors such as experience and geography.
- Job satisfaction depends on a broader mix of compensation, flexibility, and work context.

**Say:**
- Overall, developer outcomes are shaped by multiple interacting factors rather than one single variable.

---

## Slide 14: Q&A

**Thank you**

**Possible closing line**
- Thank you. I can now answer questions and show any dashboard view again if needed.
