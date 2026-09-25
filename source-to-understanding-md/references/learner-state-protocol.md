# Learner State Protocol

## 目的

维护三个相互配合的状态：

- `learner/knowledge.yaml`：用户已经会什么、熟悉什么、部分掌握什么、当前新学什么。
- `learner/explanation-profile.md`：用户更容易怎样理解、怎样组织图/公式/顺序。
- `learner/revision-log.md`：每次用户修改稿带来的稳定变化。

## 更新规则

- 用户明确说“我知道 / 不用讲 / 学过” → 可提升状态。
- 用户能在自己的修改中正确使用或迁移概念 → 至少 `familiar`。
- 用户追问“这是什么 / 为什么 / 没理解” → 对应概念不得标 `known`。
- Assistant 讲过一次 ≠ 用户掌握。
- 用户沉默或保留原文 ≠ 掌握证据。
- 用户只改措辞/顺序 → 更新 explanation profile，不自动更新知识状态。
- 用户删除一段 → 默认视为当前说明不需要；除非删除造成技术错误，否则下一版不要自动补回。

## 用户编辑稿 diff

拿到用户修改版后，比较上一版：

- order change → 更新说明顺序；
- deletion → 记录哪些内容应省略；
- expansion → 记录用户希望哪个因果步骤更明确；
- wording change → 更新 explanation profile；
- technical correction → 更新知识状态并追加证据。

始终追加 evidence / revision，不覆盖历史。
