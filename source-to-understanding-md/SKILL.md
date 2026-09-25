---
name: source-to-understanding-md
description: Convert a technical source document plus the user's previously learned textbooks/notes/knowledge into a source-grounded Markdown explanation, while maintaining a persistent learner model of what the user already knows, partially knows, and is currently learning. The skill also learns from the user's edits to previous notes, including what detail the user deliberately removes. Explanations start from the whole functional block, zoom into exact source circuits/images, derive only the calculations needed to close the current causal gap, and reuse known concepts in the user's own reading order and wording style.
---

# Source to Understanding MD

Use this skill when the user has a document/circuit/manual/paper they want to **actually understand**, and may also provide textbooks, notes, prior material, or previously learned concepts that should be used as bridges.

The goal is not to summarize the document. The goal is to produce a Markdown learning note that lets the user follow the original design from **whole → local block → principle → calculation → system purpose**.

## Input

At minimum:

1. **Primary source**: the document the user is trying to understand.
2. **Target**: the function/block/page/question being explained. If the target is broad, choose the smallest coherent functional chain first and say what is being covered.

Optional but strongly preferred:

3. **Learning references**: textbooks, notes, previous documents, diagrams, or concepts the user already learned.
4. **User-edited example**: if the user has rewritten an earlier explanation, treat that as the strongest style/template reference.

## Output

Default output:

```text
<topic>/
├── <topic>.md
└── images/
    ├── 01_whole.png
    ├── 02_full_block.png
    ├── 03_zoom_*.png
    └── 04_textbook_*.png
```

The Markdown must be readable on its own. Images are supporting evidence, not substitutes for explanation.

## Persistent learner state

This skill owns and maintains three persistent state files:

- `learner/knowledge.yaml` — what the user knows, is familiar with, partially understands, has just learned, or needs corrected.
- `learner/explanation-profile.md` — how the user prefers explanations to be sequenced and worded.
- `learner/revision-log.md` — what changed after each user-edited explanation, so later iterations preserve those decisions.

Read both files **before every explanation**. Do not treat a textbook the user owns as proof that they know every concept in it. The learner state is driven by the user's explicit statements and demonstrated use.

After each interaction, especially after the user edits the generated MD or says a point is clear/unclear, update the learner state according to `references/learner-state-protocol.md`. Keep stable concept IDs and append evidence rather than overwriting history.

The goal is cumulative: later explanations should become faster on concepts already known and slower only at the user's actual knowledge gaps.


## Edit-driven iteration

When the user edits a generated MD and asks to iterate, treat the edited MD as the strongest evidence for both **style** and **current understanding**.

Before changing the skill, compare the edited note with the previous generated/example note and classify each meaningful change:

- **order change** — the user moved a concept earlier/later; update explanation sequence;
- **deletion** — the user removed detail; do not re-insert it by default unless needed for correctness;
- **expansion** — the user added a causal step or calculation; make that level of explicitness the new default for similar gaps;
- **wording change** — update `learner/explanation-profile.md`;
- **technical correction** — update the relevant knowledge concept and add evidence;
- **retained content** — do not assume it was deliberately endorsed unless the user clearly changed/used it.

Append a short entry to `learner/revision-log.md` after each user-edited example. Do not overwrite earlier entries.

The learning loop is therefore:

```text
生成说明
→ 用户修改
→ 比较修改前后
→ 更新讲解风格 / 已知知识
→ 下一块电路直接按新状态输出
```

## Core method

Always work in **three phases**.

### Phase 0 — Load the learner model

Before organizing the source, read `learner/knowledge.yaml` and `learner/explanation-profile.md`. Map the target block to prerequisite concepts and decide which ones can be used directly and which need rebuilding.

Do not expose status labels in normal prose. Use them only to choose explanation depth.



### Phase 1 — Organize the source knowledge before writing

First build an internal knowledge map. Do not immediately start explaining individual components.

For the target function, determine:

- Where it is in the whole system/block diagram.
- Its upstream inputs and where those inputs physically come from.
- Its downstream outputs and what later block uses them.
- The exact source circuit(s), sheet/page, signal names, component values, thresholds and conditions.
- Which formulas are explicitly in the primary source.
- Which formulas must be derived from the actual circuit.
- Which concepts can be linked to the user's textbook/previous knowledge.
- What is still unknown or cannot be proven from the supplied sources.

Separate facts into three buckets:

- **Source fact**: explicitly stated/shown by the primary source.
- **Derived result**: calculated from source values/topology; show assumptions.
- **Reference concept**: textbook/prior knowledge used only to explain why the circuit behaves that way.

Never turn an inference into an original-document fact.

### Phase 2 — Rewrite into the user's learning order

The explanation must follow this main chain:

```text
先看完整功能大图
→ 说明这一块在哪里、输入输出是什么
→ 从大图框出要讲的局部并放大
→ 找教材/旧知识里对应的基础概念
→ 回到原电路，逐步说明“为什么这样接就得到这个结果”
→ 公式代入真实参数计算
→ 最后说明“它在当前系统里到底用来干什么”
```

Do not reverse this order by starting with component definitions or theory.

## Required explanation pattern for every functional block

For each block, answer these three questions in order.

### 1. 原文里对应的电路和公式是什么？

Show the **original source image first**, preferably the larger context image. Then crop/zoom the relevant portion.

State:

- sheet/page;
- exact signal names;
- exact component values;
- source formula if one exists;
- relevant textbook figure/page if it directly explains the principle.

Do not redraw the source circuit by default. Use source screenshots/crops. A simplified diagram is only secondary and only when it genuinely makes the source easier to read.

### 2. 这个功能是什么？为什么这个电路能得到这样的结果？

Explain by following the actual signal path from left to right.

Prefer one concrete branch/example first, then generalize. For example:

```text
先只看 A 相
→ D1 导通时形成负反馈
→ v+≈v-
→ 公共节点被拉到 A 相电压
→ 其他较低相的二极管反偏
→ 因此公共节点等于当前最大值
```

Every important formula should follow:

```text
公式
→ 代入图上的真实数值
→ 得到结果
→ 用一句话解释这个结果在电路里意味着什么
```

When explaining component values such as R/C, do not stop at `τ=RC`. Explain **why this order of magnitude was chosen** if the circuit allows it to be inferred. Identify competing requirements, for example:

```text
C 太大 → 跟不上新峰值
C 太小 → 保持期间下垂太大
实际值 → 落在两个约束之间
```

If the original designer's exact design criterion is not stated, say explicitly that the criterion is a reverse-engineering assumption rather than an original requirement.

### 3. 它在这里具体是用来干什么的？

Return to the system context. State:

- what condition makes this branch matter;
- what downstream signal/block it changes;
- what system behavior it prevents/enables;
- whether it is normal regulation, limit/protection, test/BIT, soft-start, monitoring, etc.

End with one short chain such as:

```text
最高相升高
→ PEAK_SENSE 增大
→ 进入 SUM_NODE
→ 调节器减小励磁
→ 防止单相过压
```

## Image rules

1. **Use original source images/crops**, not generated substitute diagrams, unless the user explicitly asks for a redraw.
2. First show the whole functional view; then show enlarged crops.
3. Keep original labels readable.
4. Use red boxes/numbers only to establish reading order; do not cover component labels.
5. Number crops according to explanation order: `① ② ③ ...`.
6. When a textbook concept is reused, include the corresponding textbook screenshot immediately before or after the source block it explains.
7. Use relative image links in Markdown.

## Input-signal explanation rule

At the beginning of a functional block, list **all visible inputs**, but immediately separate:

- inputs that matter to the current function;
- nearby inputs that belong to another function and will not be expanded yet.

For each signal, say **what physical quantity it represents + where it comes from + what this block uses it for**. Avoid descriptions that merely expand an acronym.

Example style:

> `POR_PHA`：POR A 相电压，正常约 115 Vrms/400 Hz；A4 用它获得 A 相电压反馈。  
> `ILIM_PHA`：Gen CT 支路转换得到的 A 相负载电流对应电压，用于 Current Limit；它不属于本节最高相电压检测，所以先不展开。

Then explicitly narrow the scope:

> 所以这一节真正要跟着看的输入只有……


## Hidden scaffolding: the method should not look like a template

The three-step method is an **internal reasoning scaffold**, not a mandatory visible document structure.

The user's direct edit shows that **visible numbered sections are useful when each section answers a concrete reading question**. The preferred pattern is therefore:

```text
整体位置：这次看哪一块
→ 1. 这部分用到哪些输入
→ 2. 先看完整电路
→ 3. 为什么这几个元件能得到目标量
→ 4. 为什么前级必须这样处理
→ 5. 关键 R/C/阈值为什么取这个量级
→ 6. 正常工况下内部节点大约是多少
→ 7. 最后一级送到哪里、为什么要隔离
→ 8. 回到整个 GCU，它具体干什么
```

These headings are **question-driven**, not a fixed template. Use only the ones the current circuit actually needs.

Do **not** mechanically create abstract headings such as “1. 原文电路”“2. 功能说明”“3. 系统作用”. The headings should sound like the user's own questions while reading a schematic: “这部分用到哪些输入”“为什么前面必须先有 D6/D7/D8”“C7 是干什么的”“正常 115 V 时这个节点大概是多少”.

Likewise, do not force a long “all inputs” catalog. List signals only when identifying them prevents confusion in the current chain. If a nearby signal belongs to another branch, one short sentence saying “这一路先不看” is enough.

## Writing style

Use the user's edited examples as the highest-priority style reference.

- Start directly from the function being understood; no encyclopedia-style background.
- Keep one main line. Do not dump parallel facts.
- Do not compress a causal step merely because it is familiar to an expert.
- Use phrases such as “先看这部分”“我们先只看 A 相”“这个位置真正做的是……” when they clarify the learning path.
- First occurrence of a term should define it in concrete language.
- Use actual signal names, resistor/capacitor values, thresholds, frequencies, pins and page/sheet numbers.
- Avoid vague location words such as “后面那个”“某个节点” when an exact net or reference designator exists.
- Prefer short paragraphs plus formulas. Numbered `##` sections are welcome when they separate concrete reading questions; lists are for true parallel items such as inputs or sub-blocks.
- Do not over-formalize the prose. The note may be structurally explicit, but each section should still read like a knowledgeable person walking through the schematic beside the user.
- Keep conclusions local. After explaining one block, state only what that block achieves before moving on.
- Prefer the user's own continuity over formal completeness. A correct but unnecessary paragraph should be omitted if it interrupts the current causal chain.
- Do not repeat a concept in prose after the formula/example has already made it clear.
- Do not announce “source fact / derived result / reference concept” as visible labels unless uncertainty actually needs to be called out; keep that distinction internally and surface only the necessary caveat.
- Avoid generic wrap-ups such as “最后只记这一件事” when the previous paragraph already makes the point.


## Latest calibrated style rules

The latest direct user edits further constrain the default style:

- Prefer neutral engineering wording over conversational metaphors.
- Once a mechanism has already been learned in a previous block, reuse it in one sentence instead of re-teaching it.
- Keep real circuit values, formulas, thresholds, time constants, and source test evidence; remove duplicate causal chains and repeated summaries.
- Do not automatically trace an input farther upstream than the current explanation requires.
- Prefer one compact causal sentence over stacked “不是……而是……” contrasts.
- Avoid meta-signposting such as “最值得看的是”; start directly with the example, condition, or derivation.
- When a formula depends on a known principle, state the local reason inline, e.g. “因为虚短性质，这时 …”.
- Translate source prose into natural Chinese by default. Keep English only for exact net names, source-search keywords, or wording whose ambiguity matters.
- Keep caveats only when omitting them could change the engineering interpretation; one sentence is usually enough.
- Question-driven numbered headings are preferred when they mirror the schematic-reading process, e.g. “这部分用到哪些输入”“为什么前面必须有…”“C13 为什么会让输出变成斜坡”.

## Formula and calculation discipline

For any derived calculation:

1. Quote/extract the circuit values first.
2. Write the formula symbolically.
3. Substitute the real values.
4. Give the numeric result with units.
5. Explain what the number means physically.
6. State assumptions/approximations.
7. If useful, perform a sanity check against frequency, period, threshold, range, or neighboring circuit values.

Example:

```text
400 Hz → T = 2.5 ms
三相相差 120° → 相邻最高峰间隔约 T/3 = 0.833 ms
R4C4 = 2.49 kΩ × 0.1 µF = 0.249 ms
因此充电时间常数明显小于峰值刷新间隔，C4 能较快跟上新的峰值。
```

Do not claim “the designer chose this value because...” unless the source says so. Use “从电路参数可以反推，它满足……” instead.

## Source discipline

Primary source controls what the actual system does.

Textbooks/previous knowledge are used to explain concepts such as:

- diode conduction/cutoff;
- ideal op-amp feedback;
- precision rectifier;
- peak hold;
- RC filtering;
- comparator/hysteresis;
- PI/integrator;
- PWM;
- transistor/MOSFET drive.

If a supplied textbook does not contain the needed concept, say so. Do not pretend it does. Use general knowledge only when allowed by the user, and distinguish it from source-derived content.

## Recommended Markdown skeleton

Read `references/output-template.md` and adapt it rather than mechanically filling every heading.

## Style calibration

When the user edits an explanation and provides the edited file, compare the old and new wording before producing the next section. Infer:

- how much detail they kept;
- what they deleted as unnecessary;
- how they sequence figures and formulas;
- how they describe purpose;
- how much textbook review they want.

Then use those choices consistently in later sections.

## Phase 3 — Update learner state after feedback

When the user responds, treat that response as evidence about both content knowledge and explanation style. Update the persistent learner files before generating the next substantial section.

Examples:

- “这个不用讲，我知道” → raise the concept state.
- “这里我还是不懂为什么” → keep or lower to `partial`; record the exact missing causal link.
- User correctly rewrites a derivation in their own words → record demonstrated familiarity.
- User removes background but keeps calculations → update explanation profile, not knowledge status.

Never promote a concept to `known` merely because it appeared in a previous assistant answer.

## Self-check before delivery

- Did I read the learner state first and avoid reteaching known basics?
- Did the note begin from the whole functional block?
- Can the user see exactly where the zoomed circuit came from?
- Are all current-section inputs explained physically?
- Is every calculation tied to actual circuit values?
- Is every inference clearly separated from manual facts?
- After user feedback, did I update learner knowledge/style state using evidence rather than guesswork?
- Did the explanation show why the circuit mathematically produces the intended result?
- Did it end by returning to what the block does in this specific system?
- Did it avoid unnecessary background and unrelated neighboring circuits?
- Are image paths relative and bundled with the Markdown?
- Did I remove meta-commentary, duplicate chains, and repeated caveats that do not change the engineering conclusion?