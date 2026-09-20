# Configuration ownership

Runtime NOTE content wins over templates. Initialize missing notes only, reuse equivalent existing notes, and read back all changes.

- Estimation policy: dida-task-estimator and dida-task-progress.
- Task/body protocol: capture, breakdown, progress and weekly-delivery.
- Dependency protocol: breakdown and manager.
- Weekly deliverable/effort policy: weekly-delivery and weekly-review.
- Schema/version and actual IDs: all modules when needed.

No work-calendar/availability/time-block configuration is initialized. Existing removed calendar configuration is not deleted remotely merely by installing this package; migration requires user authorization.

Do not create a local editable current-task store. Project background belongs to memory; weekly commitments belong to owner tasks, not profile.
