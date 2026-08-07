# Weekly review protocol

## Risk checks

- Overdue hard deadline.
- Remaining estimated occupancy exceeds capacity before deadline.
- Hard dependency unresolved near the last viable start date.
- Parent task with no child progress for seven or more days.
- Started task with stale `状态/进行中` and no recent focus/comment evidence.
- Repeated task skipped repeatedly.

## Estimation metrics

For eligible completed samples in chronological backtesting:

- MAE in minutes.
- Median absolute log error or typical factor error.
- Underestimation rate.
- Coverage achieved for 70%, 85%, and 90% target classes.
- Average extra buffer used.
- Comparison with no calibration, category median, and nearest similar-task baselines.

Do not use a completed task to train the estimate that is evaluated for that same task.

## Next-week pool

Recommend a pool larger than the final schedule but constrained by capacity. Identify hard commitments, high-priority unblockers, protected fitness, and movable candidates. Actual dates are applied only through the daily/weekly planning write flow.
