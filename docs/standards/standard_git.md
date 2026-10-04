# Git standard

Document state: 2026-10-03

Status: ready - full content. The full description of this standard's position relative to the others is in `docs/standards/README.md`.

## Why this document exists

The set of standards describes how to write code, and this document - how code gets into a branch. The direction in which changes flow, the role of each branch and the boundary of the agent's permissions, if they are not written down, live only in the heads of the people who settled them, and every new person and every longer break in work costs reconstructing the rule from the repository history.

The second reason concerns the agent. An agent working in this repository has access to a terminal and can technically do anything in git: commit someone else's work, push it to the remote repository, rewrite the history of a branch. The `block_dangerous_commands.py` hook blocks commit and push, but it works only on the Claude Code side and does not cover rewriting history. A boundary that is not fully enforced by a mechanism must at least be written down - otherwise it does not exist at all.

## Scope and boundaries

This standard is responsible for the agent's permissions for git, the branch roles of this repository and the directions in which a change passes between them.

What is not here:

- Commands for specific situations (undoing changes, moving commits between branches, recovering lost work) and the configuration of the git environment (the identity of the commit author, SSH keys and client). This is operational knowledge that the project keeps outside the standards. Here are the rules, there are the actions.
- The content of commit messages, including the prefix convention. Deliberately not covered by any rule of this repository - the consequence is a non-uniform history, and nothing unifies it.
- Branch protection settings on the repository hosting side. They live outside the repository, so no document in the tree can enforce or verify them.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - work that does not comply with the standard blocks review regardless of who did it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that takes effect on its own.

A clarification specific to this standard: the rule applies to all work with git in this repository, regardless of the size of the change, and does not act retroactively on already existing history. A commit created before this document was adopted is not a violation and there is no need to rewrite it.

## Agent permissions for git

The assignment of an operation to a level is decided by one criterion: whether the operation touches history. It is not decided by whether the operation is local - a local operation can also rewrite history, and an operation reaching the remote repository can leave it untouched.

Forbidden unconditionally, with no loophole for an explicit user request: `git commit` and `git push`. A commit creates a new object in history and signs it with the identity of a human who did not write it. A push exposes this object to other people, so from that moment undoing it stops being a local action. A user request does not unlock either of these two operations - if a commit is to be created, a human creates it.

Allowed only at the user's explicit request: `git add` and `git rebase`. Staging does not touch history and is reversible with one command, so it does not deserve a permanent ban, but it is the last step before a commit and there is no reason for it to happen on the agent's initiative. Rebase rewrites local history whose author is a human, and the reflog gives a way back from it - that is too little for an unconditional ban and too much for the agent's initiative.

Allowed without asking: everything else. Read operations, including `git status`, `git log`, `git diff`, `git show` and `git blame`. Fetching changes from the remote repository, i.e. `git fetch` and `git pull`. Setting changes aside with `git stash`. Switching and creating branches with `git switch` and `git checkout`. Local merging with `git merge`. Additional working directories with `git worktree`.

An operation that this document does not list is decided by the criterion, not by analogy to the nearest name. The question is whether the operation creates, rewrites or publishes history - not whether it resembles any of the listed ones.

## Branch roles and merge directions

The repository has three branch roles. `main` is the release branch, `dev` is the integration branch, into which finished work goes before the release, and both are protected on the repository hosting side so that a direct push and a force-push are not possible on either of them. The rest are permanent working branches, one per person on the team.

A working branch is personal and long-lived. It is not created per task and it does not disappear after merging - the same branch serves successive tasks of the same person.

A change enters `main` and `dev` only through a Merge Request, MR for short. In the other direction, i.e. from `main` or `dev` to a working branch, a change comes down through an ordinary merge performed locally - an MR is not needed there, because nobody except the branch owner looks at that change.

Every Merge Request to `dev` and to `main` runs the CI pipeline, `.github/workflows/ci.yml`, which mechanically mirrors the gates of the Definition of Done that need no real database; the critical tests stay with the person and the review (`docs/setup/github_actions.md`). Merging requires a green pipeline. That requirement is a setting of the branch protection on the repository hosting side, like the protection against a direct push, and nothing in this tree sets or verifies it.

The pipeline checks the branch at the time of the run, not at the time of merging: an MR that has gone stale after its last run, because another change entered `dev`, keeps its last green result. A soft rule for the person merging closes this gap: before merging, run the pipeline again if another change has entered `dev` since its last run - nothing enforces this mechanically.

When the target environment rolls out a deployment in response to a merge into the release branch, without human involvement, the Merge Request to that branch is the last moment at which the change can be seen before it reaches the environment with real data.

A Merge Request is created after every finished task, not after several at once. This is a soft rule and nothing guards it, but it is the only place where the model of personal branches differs in practice from the model of task branches: a branch that collects several unrelated changes stops fitting into one MR, review gets a grab bag instead of one change, and withdrawing a single thing requires untangling the rest.

## What this standard does not enforce

A mechanism enforces one rule from this document, and only on the Claude Code side: the `block_dangerous_commands.py` hook blocks `git commit` and `git push`, also with the `-C` or `-c` option before the command, alongside commands that destroy files and local changes. It does not cover `git add` or `git rebase`. The hook has no counterpart on the Codex side, so there the ban on commit and push is a written rule, not an enforced one. This is written down explicitly, because a soft rule described as soft still works, while a soft rule that looks hard lulls vigilance.

Violations of the non-enforced rules are detected after the fact, through `git log` and the commit author. There is no signal at the moment the violation happens.

The protection of the `dev` and `main` branches against direct push and force-push lives outside the repository, on the hosting side, and nothing in this tree verifies it or replaces it.

## Checklist

- Does the operation that the agent intends to perform create, rewrite or publish history?
- Was the user's request for `git add` or `git rebase` explicit, and not inferred from the context of the conversation?
- Was the commit created by a human hand?
- Does the change enter `main` or `dev` through a Merge Request, and not through a merge performed locally?
- Does the Merge Request contain one finished task, and not several collected along the way?
- Does a change coming down from `main` or `dev` to a working branch go through an ordinary merge, without opening an unnecessary Merge Request?
