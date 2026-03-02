# ADR 0001: Enforce Branch Protection for All Contributors on `main`

## Status

Accepted

## Date

2026-03-03

## Context

The `main` branch is the single production-ready branch for MapsAroundYou. Early in the project, branch protection was configured to require pull request reviews before merging, but the **Enforce for administrators** option was left disabled. This meant repository owners and admins could bypass the PR requirement and push directly to `main`, which undermines code review practices and can introduce unreviewed changes into the codebase.

As the team grows and the codebase matures, it is important that all changes — regardless of who makes them — go through the same review process to maintain code quality, shared ownership, and an auditable history.

## Decision

Enable **Enforce for administrators** on the `main` branch protection rule. The full ruleset is:

- Direct pushes to `main` are blocked for all contributors, including repository admins and owners.
- All changes must be introduced via a pull request.
- At least **1 approving review** is required before a PR can be merged.
- Force pushes to `main` are disabled.

## Consequences

- **Positive:** Every change to `main` is reviewed, providing a safety net against bugs and unintended changes.
- **Positive:** Admins can no longer accidentally (or intentionally) bypass the review process, keeping the team accountable.
- **Positive:** A clear audit trail exists for all changes via PR history.
- **Negative:** Hotfixes or urgent changes will require at least one review, which may slow down emergency responses. In such cases, a team member should be available to perform an expedited review.
- **Negative:** To modify or temporarily disable branch protection (e.g., for repository maintenance), an admin must do so explicitly via GitHub settings, making the bypass intentional and visible.
 
