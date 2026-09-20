# Estimation model

## Coarse categories

1. learning
2. writing
3. research_analysis
4. coding_experiment
5. hardware
6. communication_admin
7. route_errand
8. fitness_life

A category is only one feature. Familiarity and work mode often matter more than the category label.

## Familiarity

- familiar: repeated workflow and known tools.
- partial: known domain but some new content or tools.
- unfamiliar: new domain, unclear methods, or likely discovery work.

## Scope clarity

- clear: completion criterion and output size are explicit.
- partial: one or two unresolved decisions.
- unclear: exploration determines the scope.

## AI mode

- none
- assist: user works continuously with AI.
- parallel: AI can run while the user does other work.
- review_only: AI drafts and user mainly reviews.

Estimate human effort only. AI parallel elapsed time is stored separately and must not be double-counted as user effort.

## Base methods

Output scale should normally be represented in components or PERT values. Set `base_is_unit_estimate: true` only when the base is for one unit and the engine must scale it; this prevents double-counting scope.

- small/familiar: direct or analogous estimate.
- decomposable: sum child/component estimates.
- uncertain: Beta-PERT `(O + 4M + P) / 6` before historical correction.
- travel/queue: count the user's active travel/on-site/queue burden as effort where applicable; keep external lead time separate.

## Confidence

Confidence depends on scope clarity, familiarity, number and similarity of samples, and whether actual human effort is reliably separated from overlapping/parallel work.
