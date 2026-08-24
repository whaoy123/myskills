# Daily planning rules

This reference contains **method rules only**. Concrete work hours, rest windows, preferred block length, energy pattern, protected activities, and weekly availability belong to the runtime Dida profile.

## Availability

Read `规划偏好｜作息与容量` for:

- normal available work windows;
- recurring unavailable/rest windows;
- preferred focus-block length and break range;
- continuous cognitive-work limit;
- daily important-task cap when configured;
- reserve/buffer preference;
- deadline lead-time preference;
- stable energy pattern.

Do not use repository template values as current user facts after the runtime NOTE exists.

If a field is missing:

- use explicit availability from the current conversation first;
- otherwise infer only what is directly visible from the day's fixed commitments;
- use a conservative one-day assumption when planning can still proceed;
- do not silently persist that assumption as a stable profile preference.

A one-day exception such as extended working hours belongs to the current planning interaction or affected task comment, not the stable profile unless the user explicitly promotes it.

## Work style

- Match high-cognitive work to the user's configured high-energy windows when available.
- Prefer fewer coherent blocks over excessive context switching.
- Keep normal breaks and transition cost; do not fill all free minutes merely because capacity exists.
- Low-confidence estimates require more reserve than high-confidence estimates.
- AI-parallel elapsed time does not consume calendar occupancy when the user can work on something else simultaneously.

## Mobility

Read `规划偏好｜日程移动权限`.

- `fixed`: do not move unless the user explicitly changes it.
- `protected`: move only within its configured permission; do not silently delete or shorten.
- `movable`: may be rearranged within planning constraints.

Do not hard-code a specific activity such as fitness into one mobility class; the runtime profile owns that choice.

## Effective execution deadline

For a hard deadline, work backward over **real future capacity** and remaining estimated occupancy.

The effective execution deadline is the last realistic window in which the work can still finish with required validation and configured reserve. Non-working days or unavailable periods count only when the current runtime profile says they are usable.

When the last viable execution window is close, prefer concrete executable blocks over leaving the task only in a candidate pool.
