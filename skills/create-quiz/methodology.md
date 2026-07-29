# Create-Quiz Methodology

## Why This Skill Exists

Creating interactive quiz questions for lectures is time-consuming and requires:

1. **Deep understanding** of lecture content
2. **Pedagogical design** - questions must test understanding, not just recall
3. **Technical precision** - Vevox has strict formatting requirements
4. **Consistency** - questions should follow similar patterns and difficulty levels

This skill automates the technical parts while maintaining pedagogical quality.

## Design Principles

### 1. Test Understanding, Not Memorization

Bad question (rote memorization):
> Q: What does WYSIATI stand for?
> A: What You See Is All There Is

Better question (application):
> Q: System 1 constructs a story from currently activated ideas. It cannot allow for information it does not have. This describes which principle?
> A: WYSIATI (What You See Is All There Is)

### 2. Use Specific Examples from Lectures

Questions should reference:
- Actual studies mentioned (e.g., "Cohn et al. 2015", "Malmendier & Tate 2009")
- Specific problems (e.g., "bat and ball", "Linda problem", "cab problem")
- Data from slides (e.g., "41%", "85-90% of respondents")
- Visual examples (e.g., "Müller-Lyer illusion", "wheel of fortune experiment")

This grounds questions in the actual lecture content rather than generic textbook material.

### 3. Write Educational Explanations

The `CorrectAnswerExplanation` field should:
- Explain **why** the answer is correct
- Reference the underlying concept or formula
- Sometimes contrast with why distractors are incorrect
- Include specific numbers when relevant (e.g., "Using Bayes' rule: P(Blue|Witness) = 0.12/0.29 = 41%")

### 4. Create Plausible Distractors

Good distractors:
- Are based on common misconceptions
- Represent partial understanding
- Look reasonable at first glance

Example from the cab problem:
- Correct: 41% (using Bayes' rule with base rate)
- Distractor 1: 80% (ignoring base rate - most common error)
- Distractor 2: 15% (just the base rate, ignoring witness)
- Distractor 3: 50% (complete uncertainty)

Each distractor represents a different reasoning error.

## Question Difficulty Progression

### Review Quiz (10 questions)

Structure questions from easier to harder:

**Questions 1-3: Identification (easier)**
- Recognize definitions
- Identify which system performs which function
- Match concepts to examples

**Questions 4-7: Application (moderate)**
- Apply concepts to new scenarios
- Recognize which bias explains a situation
- Interpret study results

**Questions 8-10: Analysis/Synthesis (harder)**
- Solve problems requiring calculation
- Compare and contrast concepts
- Evaluate claims using course concepts

### Recap Quiz (6 questions)

Shorter format focuses on key takeaways:

**Questions 1-2: Core concepts**
- Main theories covered
- Key definitions

**Questions 3-5: Main examples**
- Important studies
- Problem demonstrations

**Question 6: Integration**
- Connects multiple concepts
- Real-world application

## The Vevox Format Challenge

Vevox is strict about Excel formatting:

### Critical Requirements

1. **Sheet name must be "Sample Template"** - Not "Sheet1", not "Questions"
2. **21 columns in exact order** - Type, Title, Choice1-8, CorrectAnswer1-4, CorrectAnswerExplanation, AllowedSelections, Minimum, Maximum, NumberOfDecimals, LowerLabel, UpperLabel
3. **Numeric columns must be float64** - Pandas tends to convert whole numbers (1.0, 2.0) to integers during Excel I/O, which Vevox rejects
4. **CorrectAnswer must use decimals** - 1.0, not 1; 2.0, not 2
5. **Empty cells must be None/NaN** - Not empty strings

### The Float64 Problem

This is subtle but critical. When you write:
```python
questions = [{'CorrectAnswer1': 1.0, ...}]
df = pd.DataFrame(questions)
df.to_excel('output.xlsx')
```

Pandas/Excel may store this as integer 1 internally. When Vevox reads it, import fails or warns.

**Solution:**
```python
df['CorrectAnswer1'] = df['CorrectAnswer1'].astype('float64')
```

Force the type before writing. This ensures Vevox sees 1.0 (float) not 1 (int).

### Column Order Matters

Vevox expects columns in a specific order. If they're scrambled, import fails. Always use the column_order list to reorder before writing:

```python
column_order = ['Type', 'Title', 'Choice1', 'Choice2', ...]
df = df[column_order]
```

## Content Extraction from LaTeX

Lecture slides are in LaTeX/Beamer format. Key patterns to extract:

### Section Headings
```latex
\section{Heuristics and Biases Approach}
\subsection{Law of Small Numbers}
```
These indicate major topics and subtopics.

### Key Terms
```latex
\alert{Representativeness}
\textbf{System 2}
```
Terms in `\alert{}` or `\textbf{}` are definitions and important concepts.

### Examples and Studies
```latex
\href{https://www.jstor.org/stable/40506267}{\textcolor{StAndrewsBlue}{Malmendier \& Tate (2009)}}
```
Studies are hyperlinked with author-year citations.

### Problems and Scenarios
```latex
\begin{frame}{The Bat and Ball Problem}
...
\emph{A bat and a ball cost \$1.10.\\
The bat costs one dollar more than the ball.\\
How much does the ball cost?}
```
Embedded problem statements make excellent quiz questions.

### Data and Results
```latex
P(B \mid W) = \frac{0.80 \times 0.15}{0.80 \times 0.15 + 0.20 \times 0.85} = \alert{41.4\%}
```
Specific numbers and formulas provide correct answers and explanations.

## Workflow

1. **Read lecture .tex file** - Extract content using Read tool
2. **Parse structure** - Identify sections, subsections, key terms, examples
3. **Generate question pool** - Create 15-20 potential questions
4. **Select best N questions** - Choose based on coverage, difficulty, and variety
5. **Write questions** - Full text with 4 choices, correct answer, explanation
6. **Validate** - Check all required fields, plausible distractors, clear correct answer
7. **Format Excel** - Use helper script to create properly formatted file
8. **Verify** - Check sheet name, column count, data types

## Quality Indicators

A good quiz file has:

- **Coverage** - Questions span the major sections of the lecture
- **Variety** - Mix of identification, application, and problem-solving
- **Clarity** - Each question has one unambiguous correct answer
- **Education** - Explanations teach, not just confirm
- **Technical correctness** - Imports into Vevox without warnings

## Common Pitfalls

### Content Issues
- Questions too easy (just recall definitions)
- Questions too vague (multiple reasonable interpretations)
- Explanations that don't explain ("This is correct because it's the right answer")
- Distractors that are obviously wrong

### Technical Issues
- Wrong sheet name
- Incorrect column order
- Integer instead of float for CorrectAnswer
- Missing CorrectAnswerExplanation
- Too few choices (need at least 2)
- CorrectAnswer out of range (e.g., CorrectAnswer1 = 5 but only 4 choices)

## Future Extensions

This skill currently creates only MCQ (Multiple Choice Questions). The Vevox template supports:

- **WordCloud** - Open-ended text responses shown as word cloud
- **Text** - Free text answers
- **Ranking** - Order items by preference or correctness
- **Numeric** - Numerical answers with range checking
- **RatingScale** - Rate items on a scale (1-10)

These could be added to create more diverse question types.

## See Also

- Vevox_QuestionImportTemplate.xlsx - Official template with examples
- vevox_quiz_creator.py - Helper script for Excel creation
- SKILL.md - Complete skill documentation
