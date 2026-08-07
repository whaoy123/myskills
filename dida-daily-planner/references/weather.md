# Weather task workflow

1. Use current location and local date; do not infer city from timezone or project names.
2. Obtain a current authoritative or reputable forecast.
3. Summarize low/high temperature, precipitation timing, and umbrella advice.
4. Resolve the recurring weather task and today's occurrence.
5. Inspect CLI help before an instance-only edit.
6. Update title to `今日天气：<low>–<high>℃，<precipitation>, <advice>` and put source/query time in the body.
7. Do not let weather silently alter task status or estimates. Replan around weather only when it materially affects travel/outdoor work or the user requests it.
