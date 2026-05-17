---
name: compiletex
description: Compile LaTeX and report errors/warnings. Use after editing any .tex file.
allowed-tools: Bash(pdflatex*), Bash(latexmk*), Bash(ls*), Read, Glob
argument-hint: [tex-file-path]
---

# Compile LaTeX

Compile the specified .tex file and report all errors and warnings.

## Usage

The user provides a path to a .tex file (or you infer it from context).

## Steps

1. **Identify the .tex file**
   - If argument provided, use that path
   - If no argument, look for .tex files in current directory
   - If multiple .tex files exist, ask user which one

2. **Compile with pdflatex**
   ```bash
   cd [directory containing .tex file]
   pdflatex -interaction=nonstopmode [filename].tex
   ```

3. **Parse the output**
   - Report any errors (lines starting with `!`)
   - Report overfull/underfull hbox warnings
   - Report missing packages or fonts
   - Report undefined references

4. **If errors exist:**
   - Show the specific error messages
   - Identify the line numbers
   - Suggest fixes if obvious

5. **If warnings exist:**
   - Show overfull hbox warnings (these affect appearance)
   - Suggest fixes (e.g., rephrase text, adjust figure width)

6. **If clean:**
   - Report success
   - Note the output PDF path

## Example Output

```
✓ Compiled successfully: insights_deck.pdf

Warnings (2):
- Line 245: Overfull \hbox (15.2pt too wide) in paragraph
- Line 312: Underfull \hbox (badness 10000)

No errors.
```

## After Compilation

If there were warnings or errors, offer to fix them. The goal is a clean compile with zero warnings.
