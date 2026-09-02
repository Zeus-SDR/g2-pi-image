# Agent workflow — KB2UKA software factory

This file is rendered from the software factory (`Kb2uka/software-factory`,
installed at the path in `~/.config/software-factory/root`). Do not edit it in
place: change `repos/g2-pi-image.md` or `AGENTS.md.template` in the factory and
re-run `scripts/install.sh`. It applies to every agent and every harness working
in this repository. `CLAUDE.md`, where present, is the deeper project brief and
this file never overrides it.

## The four beats

Every feature, fix, refactor or task runs these in order. Each is a skill; when
a harness cannot load skills, the skill text lives in the factory under
`skills/<name>/SKILL.md` and is read from there.

1. **Isolate — `/isolate`.** Fresh git worktree branched from `origin/main`,
   sibling to the checkout, after a scope check against every open PR. Never
   build in the shared checkout, never on `main` or `main`.
2. **Shape — `/shape`.** Grep the seams first and model the change on the
   nearest existing pattern in this repo. DRY, tests mandatory, engineered
   enough, explicit over clever. Self-review through the four lenses
   (architecture, code, tests, performance) before and after writing.
3. **Prove — `/evidence`.** Bug fixes ship a test recorded failing before the
   fix and passing after. Visible changes ship before/after captures. Backend
   changes ship the wire log or measured numbers. Everything lands in
   `.artifacts/<task>/` with an `assertions.md`. Automation never keys a
   transmitter.
4. **Ship — `/proof`, `/review-loop`, then `/ship` reports.** Draft PR against
   `main` with the Proof section filled, gates listed as actually run, then
   the review loop until every judge seat scores 5/5 with nothing open (max 5
   rounds). End by presenting the PR URL and the "Needs a human" list.

The PR body has these headings in this order: Summary, Root cause (fixes),
Proof, Gates, Review rounds, Needs a human, then the `factory:` footer line.

## Multi-agent rules

- One worktree and one branch per task per agent. Never reuse or touch another
  agent's worktree, branch, or uncommitted work.
- Never `checkout`, `reset`, `stash` or `clean` in the shared primary checkout.
  Other sessions are sitting in it.
- Scope check before starting: `gh pr list`, then `gh pr diff <n> --name-only`
  for each. On overlap with your files, stop and report.
- `--force-with-lease` only, only on your own task branch. Never force-push a
  shared branch.
- Lockfile conflicts are regenerated, never hand-merged.
- Worktrees do not isolate ports or databases: confirm a port answers your
  process before trusting it, and use a throwaway data path where the repo
  offers one.
- If a conflict cannot be resolved with confidence, stop and report.

## Inside an orchestrated pipeline

When another agent or a pipeline is driving you (the autofix fleet, a `/trio`
run, a `/ship --swarm` coder brief), the orchestrator owns beats 1 and 4: it
created your worktree, it owns git, it opens the PR, and it runs the review.
You do beats 2 and 3 only: shape, implement, test, and leave the evidence in
`.artifacts/<task>/`. Never commit, push, open a PR, or trigger a review from
inside a brief unless the brief says so explicitly. The brief overrides the
"Completing a task" list below.

## Hard rules that never vary

- Never mention any AI assistant, model or vendor in commits, PR bodies, code
  comments, or any repo-visible artifact. Credit is KB2UKA.
- Never merge, publish, release, or send anything outward without a human
  maintainer's explicit go. End at a draft PR.
- Never change the power state of any machine on the 10.70.x.x network.
- Never claim a gate passed that did not run. Never cite a source not opened.
- Red-light surfaces (visual design, UX behaviour, architecture and new
  dependencies, operator-felt defaults) are implemented minimally and listed
  under "Needs a human", never decided silently.

## Completing a task

1. Keep the change to the assigned task.
2. Run every command under "Gates" below and record the result.
3. Assemble the evidence into the Proof section.
4. Rebase onto the latest `origin/main`, rerun the gates.
5. Push (`git push -u origin <branch>`; `--force-with-lease` after a rebase).
6. Open the draft PR against `main` with the required headings.
7. Run the review loop to 5/5.
8. Present the PR URL. Keep the worktree until the PR is merged or closed.

---

## G2 Pi image — repo section

Raspberry Pi image manifest and patches for the ANAN G2 internal Compute
Module. A 1 GB CM4 cannot run the desktop appliance; keep that in mind when
touching first-boot behaviour.

### Gates

```bash
bash -n $(git ls-files '*.sh')
```

Run `shellcheck` on changed scripts when it is installed.

### Evidence tiers here

D: the exact first-boot log or `dmesg` excerpt from a flashed card. Flashing
and booting a card is a human step; label `bench-required`.
