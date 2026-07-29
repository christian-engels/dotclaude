---
name: create-quiz
description: Generate Vevox-compatible quiz questions from lecture materials. Creates properly formatted Excel files ready for import into Vevox polling system. Supports both review quizzes (longer, covering previous week) and recap quizzes (shorter, covering current lecture).
allowed-tools: Read, Write, Bash(uv*), Bash(python*)
argument-hint: [lecture-files] [quiz-type] [num-questions]
---

# Create-Quiz: Generate Vevox Quiz Questions from Lectures

This skill creates Vevox-compatible Excel quiz files from LaTeX lecture materials for FI5614 Behavioural Finance.

## When This Skill Is Invoked

The user wants to create interactive quiz questions from lecture slides. Typical usage:

- `/create-quiz "Week 2 Heuristics and Biases.tex" review 10` — Create a 10-question review quiz
- `/create-quiz "Week 3 Expected Utility Theory.tex" recap 6` — Create a 6-question recap quiz
- `/create-quiz` — Interactive mode (will prompt for details)

## Quiz Types

**Review Quiz (longer):**
- Tests understanding of **previous week's** material
- Shown at the **start** of the next lecture
- Typically **8-12 questions**
- Comprehensive coverage of key concepts
- Used to activate prior knowledge

**Recap Quiz (shorter):**
- Tests understanding of **current lecture** material
- Shown at the **end** of the lecture
- Typically **5-7 questions**
- Focuses on main takeaways
- Used to check comprehension

## Step 1: Parse Arguments

If the user provides arguments, parse them:
```
lecture_file = arg1 (e.g., "Week 2 Heuristics and Biases.tex")
quiz_type = arg2 (either "review" or "recap")
num_questions = arg3 (integer, typically 6-12)
```

If no arguments or insufficient arguments:
1. Ask which lecture file to use (show available `.tex` files)
2. Ask quiz type (review or recap)
3. Ask number of questions (suggest 10 for review, 6 for recap)

## Step 2: Read and Analyze Lecture Content

Read the specified lecture file(s):

**For Review Quiz:**
- Read the **previous week's** lecture file
- Example: Creating Week 2 review → read Week 1 material

**For Recap Quiz:**
- Read the **current week's** lecture file
- Example: Creating Week 2 recap → read Week 2 material

Extract key concepts:
- Section headings (`\section{}`, `\subsection{}`)
- Key terms in `\alert{}` or `\textbf{}`
- Examples and studies mentioned
- Problem statements and solutions
- Main theories and frameworks

## Step 3: Design Questions

Create pedagogically sound MCQ questions that:

1. **Test understanding, not memorization**
   - Avoid "define this term" questions
   - Ask "which example demonstrates X?" instead of "what is X?"
   - Include application and analysis questions

2. **Use specific examples from lectures**
   - Reference actual studies (e.g., "Cohn et al. 2015")
   - Use problem scenarios (e.g., "bat and ball problem")
   - Include data from slides (e.g., "41% in cab problem")

3. **Have clear correct answers**
   - Only one obviously correct answer
   - Distractors should be plausible but incorrect
   - Avoid "all of the above" or "none of the above"

4. **Include educational explanations**
   - Each question needs a `CorrectAnswerExplanation`
   - Explain WHY the answer is correct
   - Reference the concept or formula

### Question Distribution Guidelines

**Review Quiz (10 questions) example breakdown:**
- 2-3 definition/identification questions
- 3-4 application questions (using examples from lecture)
- 2-3 problem-solving questions (with numerical answers)
- 1-2 higher-order questions (comparing concepts, evaluating claims)

**Recap Quiz (6 questions) example breakdown:**
- 1-2 key concept identification
- 2-3 application of main theories
- 1-2 problem examples from lecture

## Step 4: Create Excel File

Use the helper script `vevox_quiz_creator.py` (in this skill's directory) to create the file.
It uses openpyxl directly (not pandas) to avoid the `inlineStr` bug where empty cells get
written as inline strings instead of truly empty cells, which causes Vevox import errors.

```python
# Import the helper
sys.path.insert(0, '/workspaces/behavioural-finance/.claude/skills/create-quiz')
from vevox_quiz_creator import create_vevox_quiz, validate_questions

questions = [
    {
        'Type': 'MCQ',
        'Title': 'Question text here?',
        'Choice1': 'First answer',
        'Choice2': 'Second answer',
        'Choice3': 'Third answer',
        'Choice4': 'Fourth answer',
        'CorrectAnswer1': 1,
        'CorrectAnswerExplanation': 'Explanation of why this is correct.',
        'AllowedSelections': 1
    },
    # ... more questions (omitted fields default to None)
]

if validate_questions(questions):
    create_vevox_quiz(questions, output_filename)
```

## Step 5: File Naming Convention

Use clear, descriptive names:

**For Review Quiz:**
- `Week_N_Review_Quiz.xlsx` where N is the week being reviewed
- Example: `Week_2_Review_Quiz.xlsx` (reviews Week 1, shown at start of Week 2)

**For Recap Quiz:**
- `Week_N_Recap_Quiz.xlsx` where N is the current week
- Example: `Week_2_Recap_Quiz.xlsx` (recaps Week 2, shown at end of Week 2)

## Step 6: Validation

After creating the file, verify:

1. **Correct sheet name:** `Sample Template`
2. **Correct number of columns:** 21
3. **Correct number of questions:** Matches requested count
4. **Data types:** Numeric columns are float64
5. **Required fields populated:**
   - Type (always 'MCQ')
   - Title (question text)
   - Choice1-4 (at least 4 choices)
   - CorrectAnswer1 (1.0, 2.0, 3.0, or 4.0)
   - CorrectAnswerExplanation (non-empty)
   - AllowedSelections (1.0 for single choice)

Print verification summary:
```
✓ Created Week_N_[Type]_Quiz.xlsx
✓ [N] questions
✓ Sheet name: Sample Template
✓ All required fields populated
✓ Ready for Vevox import
```

## Critical Formatting Rules

**MUST follow these exactly or Vevox import will fail:**

1. Sheet name **must** be `Sample Template`
2. CorrectAnswer1 **must** be 1, 2, 3, or 4
3. AllowedSelections **must** be 1 for single-choice MCQ
4. Empty cells **must** be truly empty (not written at all) — do NOT use pandas, which writes None as `inlineStr` type cells that Vevox rejects. Use openpyxl directly via `vevox_quiz_creator.py`.
5. Column order **must** match template exactly (21 columns)
6. Choice columns: populate 1-4 for MCQ, omit 5-8
7. **No Unicode special characters** — replace em dashes, en dashes, curly quotes, and Unicode minus signs with ASCII equivalents. The helper script does this automatically.

## Supported Question Types

Currently only **MCQ (Multiple Choice)** is implemented. The template supports:
- WordCloud
- Text
- Ranking
- Numeric
- RatingScale

These can be added in future versions if needed.

## Example Usage

```bash
# Interactive mode
/create-quiz

# Create review quiz
/create-quiz "Week 2 Heuristics and Biases.tex" review 10

# Create recap quiz
/create-quiz "Week 3 Expected Utility Theory.tex" recap 6

# Create quiz for multiple weeks (review covering weeks 1-2)
/create-quiz "Week 1 Psychology and Behavioural Economics.tex,Week 2 Heuristics and Biases.tex" review 12
```

## Quality Checklist

Before delivering the quiz file, ensure:

- [ ] Questions test understanding, not just recall
- [ ] All questions reference specific lecture content
- [ ] Distractors are plausible but clearly incorrect
- [ ] Explanations teach, not just confirm
- [ ] No typos or formatting issues
- [ ] Correct answer is unambiguous
- [ ] Questions progress from easier to harder
- [ ] Good mix of question types (identification, application, problem-solving)
- [ ] File imports into Vevox without warnings

## Dependencies

Required packages (install via uv):
- openpyxl

Install command:
```bash
uv run --with openpyxl python3 script.py
```

## Template Location

The Vevox template file should be at:
```
./Vevox_QuestionImportTemplate.xlsx
```

If not found, ask the user for the location or download from Vevox documentation.

## Troubleshooting

**"Invalid questions" or "import warnings" in Vevox:**
- Most likely cause: empty cells written as `inlineStr` type instead of truly empty. This happens when pandas writes None values. Fix: rewrite the file using `vevox_quiz_creator.py` or openpyxl directly, only writing cells that have values.
- Check sheet name is exactly `Sample Template`
- Check for Unicode characters (em dashes, curly quotes) — replace with ASCII

**Questions not displaying:**
- Check Title field is populated
- Verify at least 2 choices are provided
- Ensure Type is 'MCQ'

**Formatting issues:**
- Check column order matches template (21 columns)
- Verify no extra/missing columns
