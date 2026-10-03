# Code formatting standard

Document state: 2026-10-03

Status: ready - full content. The full description of this standard's position relative to the others is in `docs/standards/README.md`.

## Why this document exists

Formatting is what review sees first, before it gets to the logic of the change - a line that breaks in a different place than the rest of the file, a quotation mark of a different kind than the neighboring ones, a character that looks like a dash but is not one. None of these details changes the behavior of the program, but each of them costs the reviewer attention that should go to the logic diff itself, not to its visual wrapping. This standard sets one shape for these details, so that review can skip them instead of judging them anew with every change.

Most of the rules below are already enforced automatically today by `ruff format` based on the settings in `pyproject.toml` - unlike most standards in this repository, aligning existing code with the rules of this standard does not require rewriting anything by hand. It is enough to run the formatter on the touched module.

## Scope and boundaries

This standard is responsible for code formatting: line length and the moment a call is broken into multiple lines, forbidden characters, quotation marks and emphasis - in Python code and in documentation prose. It is also responsible for formatting markdown files with prettier: which tool, with which configuration and which `make` target runs it.

Forbidden characters currently have two versions: a shortened one in `CLAUDE.md`/`AGENTS.md` (hard bans applicable without context) and a full one, with rationale, here - this is the intended architecture described in `docs/standards/README.md`, not duplication to be fixed. The shortened version in `CLAUDE.md`/`AGENTS.md` differs numerically from the full list below - this mismatch is known and remains unfixed.

What is not here: line comments and docstrings - those are in `standard_code_quality.md`.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that takes effect on its own.

A clarification specific to this standard: for rules enforced automatically by `ruff format` (line length, quotation marks in code) and by prettier (layout of a markdown file), the duty to align comes down to running `make format`, not to manual work. For rules not enforced automatically - forbidden characters in documentation, quotation marks in prose - the duty to align is an ordinary review of the changed text, as in every other standard.

## Line length and breaking calls

The line length limit is 200 characters, set in `pyproject.toml` (`[tool.ruff] line-length = 200`) and enforced by `ruff format`. A function call and a function definition whose parameters fit within this limit, separated by spaces after commas, stay on one line. Once the limit is exceeded, each parameter goes on a separate line, with a comma at the end, and the closing parenthesis returns to the indentation of the line in which the call started.

This split is not a decision made by hand while writing code - it is the effect of running `ruff format` on the file. Writing code with the thought "this will surely be too long, so I break the line right away" is unnecessary: the formatter will break it itself if needed, and join it back if not.

The 200-character limit is higher than the default 79 or 88 adopted elsewhere in the Python ecosystem. Rationale: functions in this repository often have several named parameters (`timeout`, `autocommit`, `limit`), and with a shorter limit the function signature alone, with type annotations and default values, would break into multiple lines already at a moderate number of parameters, even though it is just as readable on one line. A higher limit means fewer artificial line breaks without loss of readability on a modern, wide screen.

The magic trailing comma is respected (`[tool.ruff.format] skip-magic-trailing-comma = false`): a comma left after the last element of a list or after the last argument forces a multi-line layout, even if the whole would fit on one line. This is a deliberate exception to the rule "the formatter decides on breaking solely based on length" - available when the author of the code decides that the argument list is more readable split, even though it would fit within the limit, for example because each argument deserves a separate look during review.

## Quotation marks

In Python code the quotation mark is always double (`[tool.ruff.format] quote-style = "double"`), enforced automatically by `ruff format`. The choice between `'` and `"` is not a decision to be made while writing - the only case in which the formatter itself uses a single one is a string containing a literal `"` character, to avoid escaping it.

In prose - docstrings, comments, the content of standards, communication - quotation marks are used only when they are needed for something: a literal quote, the name of a field or a code fragment pasted into the text. A quotation mark placed around a word without any of these functions, only for emphasis, is noise: it blurs the difference between a place where the quotation mark actually means "this is a literal quote of something" and a place where it is only decoration. Regardless of context, the only allowed character is the plain ASCII `"` - never a curly one, see the section below.

## Emphasis in prose

Prose does not use bold: neither inside a sentence, nor as a label opening a paragraph or a list item. This applies to the standards, the documentation in `docs/`, the `agent_docs/` layer and all task artifacts in `plans/` - SEED, SHAPE, PRD, PLAN and REVIEW. Bold remains allowed only where it is an element of the document structure, not emphasis of content: in a heading and in a table cell.

The rationale is the same as for quotation marks in the section above, only the cost is higher. A label such as:

```markdown
**What it affects:** `standard_database.md`, repository structure, order of work.
```

pretends to be a heading that it is not. It does not get into the table of contents, it cannot be referenced from another document, and when reading it looks like the skeleton of the document, even though it is an ordinary paragraph. If a fragment really is a separate part of the document, it should get a heading. If it is not, an ordinary sentence is enough:

```markdown
What it affects: `standard_database.md`, repository structure, order of work.
```

Bolding a single word in the middle of a sentence fails in the other direction: the more such emphases, the less each of them means, and the reader starts jumping between the bold fragments and loses the sentence that connects them. The weight of emphasis is carried by order, not by typeface - the most important thing stands at the beginning of the paragraph or at the beginning of the list, not in its middle, wrapped in asterisks.

The rule is guarded by `tests/architecture/test_prose_style.py`, together with the list of forbidden characters. The gate has four properties that are easy to mistake for its bug:

- It scans every `.md` and `.py` file in the tree outside the tool directories and the third-party content described below, including ones not tracked by git, so a red result is sometimes the fault of someone else's file, not of the current change. With a red gate, first check which paths trigger it.
- Third-party content installed by its own installer stays outside the gate, for the same reason as `node_modules`: it is written in someone else's style, and an edit made by hand would be overwritten by its next update. Today this is the `impeccable` skill with its agent roles, named one by one in `tests/architecture/common_vendored_content.py`; the rule and its boundaries are in `standard_agentic_workflow.md` ch. 6.1. A document the team writes never goes on that list.
- A copy of someone else's document in `plans/<INITIATIVE>/attachments/` comes under the gate like any other file. Before copying someone else's document, check it for bold and forbidden characters, and on a hit the user chooses: editing the copy with an explicit note about the divergence, excluding the directory from the gate, or giving up the copy.
- The bold detector does not exclude inline code. Two pairs of asterisks on one line, for example two dictionary unpackings in Python or two masks with a triple asterisk, trigger the gate even inside backticks. A markdown line holds at most one such occurrence, and the second one is described in words.

## Markdown formatting

Markdown files are formatted by prettier, just as Python code is formatted by `ruff format`. A markdown file must pass `prettier --check` without differences before the change is merged; this is checked by `make lint` (and through it by `make check`), and put in order by `make format`. Ruff deliberately does not cover markdown - the reason is in `standard_code_quality.md`, section Static analysis and formatting.

The configuration lives in two tracked files in the repository root. `.prettierrc` carries the options: LF line endings, no prose wrapping (`proseWrap: preserve`), a width of 200 characters consistent with the ruff limit, a two-space indentation for nested lists. `package.json` pins the exact prettier version in `devDependencies`, and `npm ci` installs it into `node_modules`; `node` and `npm` are a prerequisite on the developer's side, listed in the repository's `README.md`. The `make` targets call `npx --no-install` to use only the pinned copy and to abort when it is missing - a bare `npx prettier` would silently download the latest release and check the file with a different version than the editor.

Both files are also read by the prettier extension in VS Code, through which `.vscode/settings.json` formats markdown on save. With the configuration file present, the extension ignores its own `prettier.*` settings in VS Code and picks the copy from `node_modules` over the bundled version, so a save from the editor and `make format` give an identical result. Upgrading the prettier version is a change in `package.json`, not an extension update.

What prettier changes in a file: it aligns table columns to the widest cell, normalizes blank lines around headings and blocks, sets the continuation indentation of a list item, unifies emphasis markers and formats fenced code blocks in a language it knows (`json`, `yaml`) to the same width of 200 characters. What it does not change: the content and wrapping of paragraphs, and `python` and `sql` blocks, which it does not parse. A technical name with an underscore standing in prose without backticks is sometimes read as italics and rewritten into asterisks (`trigger_params` into `trigger*params`), which is why a technical name in prose stands in backticks. The reason is mechanical, not stylistic: the formatter does not touch what is marked as code.

## Table width in documentation

A table cell in documentation prose carries a short phrase or one short sentence, not several sentences of rationale. The reason is mechanical, not aesthetic: prettier, like every markdown formatter, aligns the whole column to the width of its longest cell, so one long-winded cell stretches every row of the table to the same width, including the rows that are short on their own. The effect is visible in the source as lines of several hundred characters, which cannot be read without scrolling sideways - this is the narrowing of the visible field that this rule is about, not a subjective impression.

A table in which every row is a separate paragraph of rationale anyway - a decision with a reason, a risk with a consequence and a mitigation, a rejected alternative with an explanation - is a table in name only. Such a layout should get the form proper to prose: a heading per row, if the row has a stable identifier used elsewhere in the documentation (for example `D14`, `R7`), or a list item, if it has no identifier. A table stays a table where it actually juxtaposes short, parallel facts for scanning by eye - an HTTP code next to the error name, a field next to who can change it - and in such a case a single row that has grown is worth shortening to a phrase, with the rest of the explanation moved to an ordinary paragraph below the table, instead of leaving it in the cell.

## Forbidden characters

Code and documentation in this repository do not contain the characters below. Some of them are obvious typographic characters of a chat (dashes, curly quotation marks, the ellipsis, arrows, the multiplication sign) - their presence in code or documentation betrays text generated without passing through the repository's style. Some are deliberately chosen homoglyphs: characters visually indistinguishable from ordinary ASCII characters, which a language model could insert without noticing the difference - for these characters the code point is given explicitly, to avoid a mistake when reading this list by eye.

- `—` (U+2014, em dash) - use a plain `-` instead.
- `–` (U+2013, en dash) - use a plain `-` instead.
- `−` (U+2212, minus sign) - use a plain `-` instead.
- `“` (U+201C, left curly double quotation mark) - use a plain `"` instead.
- `”` (U+201D, right curly double quotation mark) - use a plain `"` instead.
- `‘` (U+2018, left curly single quotation mark) - use a plain `'` instead.
- `’` (U+2019, right curly single quotation mark) - use a plain `'` instead.
- `ʼ` (U+02BC, modifier letter apostrophe) - use a plain `'` instead.
- `…` (U+2026, ellipsis) - use three plain dots `...` instead.
- `·` (U+00B7, middle dot) - use a plain period or a dash instead, depending on context.
- `→` (U+2192, rightwards arrow) - use `->` instead.
- `←` (U+2190, leftwards arrow) - use `<-` instead.
- `↔` (U+2194, left right arrow) - use `<->` instead.
- `×` (U+00D7, multiplication sign) - use the letter `x` or `*` instead, depending on context.
- `а` (U+0430, Cyrillic letter "a") - looks identical to the Latin "a" (U+0061), but it is a different code point - use a plain Latin `a` instead.
- `;` (U+037E, Greek question mark) - looks identical to an ordinary semicolon (U+003B), but it is a different code point - when a semicolon is needed, use a plain `;` instead.
- `∕` (U+2215, division slash) - looks similar to an ordinary slash (U+002F), but it is a different code point - use a plain `/` instead.
- Emojis, for example 🙂 🚀 ✅ - are absolutely never used in code or in documentation.

## Checklist

- Has new or changed code gone through `ruff format` before the change is merged, instead of breaking lines and choosing quotation marks by hand?
- Does no line of code exceed 200 characters (except for cases in which `ruff format` itself would leave it longer - e.g. a long string that does not split)?
- Is the magic trailing comma used deliberately, where the author wants a multi-line layout even though it would fit within the limit, and not by accident?
- Does a string in Python code use double quotation marks, except for a string containing a literal `"` character?
- Do quotation marks in prose (docstring, comment, documentation) appear only for a literal quote, the name of a field or a code fragment in the text, and not as decoration?
- Has a new or changed markdown file gone through `make format` before the change is merged, and does `make lint` report no prettier differences for it?
- Is a technical name with an underscore, standing in the prose of a markdown file, in backticks, so that prettier does not rewrite it as emphasis?
- Is the prose free of bold - both in the middle of a sentence and in the form of a label opening a paragraph or a list item - and does bold appear only in headings and table cells?
- Does no table cell carry more than a short phrase or one short sentence, and has a table whose rows are in essence separate paragraphs of rationale been converted into headings or a list?
- Do code and documentation contain no character from the list of forbidden characters, including homoglyphs?
- Does no markdown line have two pairs of asterisks, including in inline code in backticks?
- Does the text contain no emojis?
