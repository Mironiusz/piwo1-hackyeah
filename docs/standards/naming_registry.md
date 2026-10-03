# Naming registry

Document state: 2026-10-03

## What this file is

A registry of names actually used in the repository. It describes the actual state, not the target one - unlike `standard_naming.md`, which sets the rules. When the registry and the standard diverge, the standard says what should be and the registry says what is; the divergence between them is information, not an error of either of them.

The deviation rule applies here differently than to the standards: the registry describes the actual state by definition, so it is impossible to be non-compliant with it. It can only be outdated - and that is the only way this file can be wrong.

## How to use it

Before you invent a name for a new file, function or constant, check whether the pattern is already here. If it is, use it. If it is not, and the name is likely to repeat, add it here together with its first place of use. This way a second person will not invent a different name for the same thing.

## Current state

The registry is empty, because the project has no code yet. The first entries are created together with the first files, functions and constants of the project, in sections by kind of name: names in the database, file names, function names, names of query constants, `makefile` target names, names in tests. The target rule is in `standard_naming.md`; the actual state goes here.
