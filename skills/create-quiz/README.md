# Create-Quiz Skill

Generate Vevox-compatible quiz questions from lecture materials.

## Quick Start

```bash
# Interactive mode - will prompt for details
/create-quiz

# Create a review quiz (10 questions, covering previous week)
/create-quiz "Week 2 Heuristics and Biases.tex" review 10

# Create a recap quiz (6 questions, covering current lecture)
/create-quiz "Week 3 Expected Utility Theory.tex" recap 6
```

## What It Does

This skill:
1. Reads LaTeX lecture slides
2. Extracts key concepts, examples, and studies
3. Generates pedagogically sound MCQ questions
4. Creates properly formatted Excel files ready for Vevox import

## Output

Creates Excel files like:
- `Week_2_Review_Quiz.xlsx` - Review of Week 1 content, shown at start of Week 2
- `Week_2_Recap_Quiz.xlsx` - Recap of Week 2 content, shown at end of Week 2

Each file contains:
- Multiple choice questions with 4 answer options
- One correct answer per question
- Educational explanations for each correct answer
- Proper Vevox formatting (sheet name, column order, data types)

## Quiz Types

### Review Quiz (longer)
- **When:** Start of next week's lecture
- **Coverage:** Previous week's material
- **Length:** 8-12 questions
- **Purpose:** Activate prior knowledge, check retention

### Recap Quiz (shorter)
- **When:** End of current lecture
- **Coverage:** Current week's material
- **Length:** 5-7 questions
- **Purpose:** Check comprehension, reinforce key points

## File Structure

```
.claude/skills/create-quiz/
├── README.md                    # This file
├── SKILL.md                     # Detailed skill documentation
├── methodology.md               # Design principles and approach
└── vevox_quiz_creator.py       # Helper script for Excel creation
```

## Requirements

- pandas
- openpyxl

Both are automatically installed via `uv` when the skill runs.

## Usage Examples

### Example 1: Create Week 3 Review Quiz
```bash
/create-quiz "Week 2 Heuristics and Biases.tex" review 10
```

This will:
- Read Week 2 lecture content
- Generate 10 questions reviewing Week 2 material
- Create `Week_3_Review_Quiz.xlsx` (to be shown at start of Week 3)

### Example 2: Create Week 4 Recap Quiz
```bash
/create-quiz "Week 4 Prospect Theory, Framing and Mental Accounting.tex" recap 6
```

This will:
- Read Week 4 lecture content
- Generate 6 questions recapping Week 4 material
- Create `Week_4_Recap_Quiz.xlsx` (to be shown at end of Week 4)

### Example 3: Interactive Mode
```bash
/create-quiz
```

The skill will prompt you for:
1. Which lecture file to use
2. Quiz type (review or recap)
3. Number of questions

## Question Design

Questions are designed to:
- ✓ Test understanding, not memorization
- ✓ Reference specific examples from lectures
- ✓ Include plausible but incorrect distractors
- ✓ Provide educational explanations

Example question:
```
Q: In the cab problem (85% Green cabs, 15% Blue cabs, witness 80% accurate),
   what is the probability the cab was actually Blue?

   A. 80%
   B. 41%  ← Correct
   C. 15%
   D. 50%

Explanation: Using Bayes' rule: P(Blue|Witness says Blue) =
(0.80 × 0.15) / (0.80 × 0.15 + 0.20 × 0.85) = 0.12/0.29 = 41%.
The base rate of 15% pulls the answer far below the intuitive 80%.
```

## Troubleshooting

### Vevox Import Warnings

If you get warnings when importing:

1. **Check sheet name** - Must be "Sample Template" (not "Sheet1")
2. **Check numeric format** - CorrectAnswer must be 1.0, 2.0 (not 1, 2)
3. **Check columns** - Must have exactly 21 columns in correct order

### Questions Not Displaying

If questions don't appear in Vevox:

1. **Check Title field** - Must be populated
2. **Check choices** - Must have at least 2 choices (Choice1, Choice2)
3. **Check Type** - Must be "MCQ"

### Poor Question Quality

If questions are too easy, too hard, or unclear:

1. Review the methodology.md file for question design principles
2. Manually edit the generated questions before import
3. Provide feedback to improve future generations

## Technical Details

The skill creates Excel files matching the Vevox template structure:

- **Sheet name:** `Sample Template`
- **Columns (21 total):** Type, Title, Choice1-8, CorrectAnswer1-4, CorrectAnswerExplanation, AllowedSelections, Minimum, Maximum, NumberOfDecimals, LowerLabel, UpperLabel
- **Question type:** MCQ (Multiple Choice Questions)
- **Data types:** Numeric columns are float64, text columns are strings
- **Format:** AllowedSelections = 1.0 (single choice), CorrectAnswer1 = 1.0-4.0

## See Also

- **SKILL.md** - Complete skill documentation
- **methodology.md** - Design principles and pedagogical approach
- **vevox_quiz_creator.py** - Python helper for Excel creation
- **Vevox_QuestionImportTemplate.xlsx** - Official Vevox template

## License

Part of the FI5614 Behavioural Finance course materials.
