# 固定审阅报告模板

报告标题使用：`<文档名> 格式审阅报告`。

## Markdown 固定结构

```markdown
# <文档名> 格式审阅报告

## 1. 审阅范围

| 项目 | 内容 |
|---|---|
| 源文件 | <绝对路径> |
| 修改文件 | <绝对路径或“未修改”> |
| 审阅模式 | 只读检查 / 复制后修改 |
| 规则档 | 通用 / CUGB 硕士开题 / CUGB 博士开题 / 自定义模板 |
| 学校要求来源 | <学校模板、院系指南/通知、官方网页/PDF、用户提供规则；没有则写“未提供”> |
| 要求抽取状态 | <已提取/部分提取/存在冲突/未提供；含版本、生效日期和置信度> |
| 规则依据 | <学校要求证据；通用规范和外部资料另列，不得替代学校要求> |
| 审阅时间 | <YYYY-MM-DD HH:mm> |
| 内容保护项 | <逐项列出；没有则写“无”> |
| 视觉例外 | <逐项列出宽度/缩放/位置例外；没有则写“无”> |

## 2. 总结

| 指标 | 数值 |
|---|---:|
| P0/P1/P2/P3 问题 | <数量> |
| 正文有效字数 | <数量>/<规则门槛或“未配置”> |
| 文献表条目 | <数量> |
| 参考文献数量门槛 | <数量>/<规则门槛或“未配置”> |
| GB/T 7714 版本规则 | <已指定版本/未配置/需确认> |
| 学校内容完整性规则 | <已配置/部分配置/未配置> |
| 未配置的学校检查项 | <项目列表或“无”> |
| 正文文献引用 | <数量> |
| 交叉引用域 | <数量> |
| 题注 | <图数量>/<表数量> |
| 公式/脚注/尾注 | <数量或“未使用”> |
| 已修改对象 | <数量> |
| 新增批注 | <数量> |

结论：<一句话说明是否建议提交，以及保护项/未处理项。>

## 3. 问题表

| ID | 类别 | 严重度 | 位置 | 证据 | 影响 | 修改建议 | 状态 | 保护类型 |
|---|---|---|---|---|---|---|---|---|
| REF-01 | 引用 | P1 | 第 x 页/第 x 段 | <字段或原文证据> | <影响> | <建议> | 未修改/已修改/需确认 | 无/内容保护/视觉例外 |

## 4. 修改建议表

| 关联问题 | 原文/对象 | 建议修改后 | 批注内容 | 是否已修改 | 批注位置 |
|---|---|---|---|---|---|
| ENG-01 | <原文> | <修改后> | <批注文本> | 是/否 | <位置> |

## 5. 已确认正常

| 检查项 | 结果 | 证据 |
|---|---|---|
| 文献编号连续性 | 正常 | <编号范围/数量> |

## 6. 内容保护项、视觉例外与未处理项

| 对象 | 类型 | 发现的问题 | 未处理原因 | 后续动作 |
|---|---|---|---|---|
| <对象> | 内容保护/视觉例外 | <如有> | <只保护内容或只保护视觉几何> | <用户授权或保持布局后处理> |

学校专属规则配置也必须单独记录，不能把“未提供学校要求”写成报告文档本身的格式错误：

| 学校规则项目 | 来源/证据 | 状态 | 未判定原因 | 后续动作 |
|---|---|---|---|---|
| GB/T 7714 版本 | <条款、页码或“未提供”> | 已配置/未配置/需确认 | <版本未指定或来源冲突> | <补充学校要求或确认版本> |
| 字数与参考文献门槛 | <条款、页码或“未提供”> | 已配置/未配置/需确认 | <门槛未指定或适用范围不明> | <补充学校要求或确认学位层次> |
| 开题报告内容完整性 | <条款、页码或“未提供”> | 已配置/部分配置/未配置 | <章节要求缺失或提取置信度不足> | <补充模板/指南并复核> |

## 7. 验证记录

- OOXML 字段检查：通过/未执行（原因）
- 学校要求提取：已提取/部分提取/存在冲突/未提供（来源、版本、生效日期和置信度）
- DOCX 全部可访问部件扫描：通过/未执行（原因）
- `python-docx` 开包检查：通过/未执行（原因）
- 修订/隐藏文字/元数据检查：通过/未执行（原因）
- Word 只读 PDF 复核：通过/未执行（原因）
- 最终文件：<绝对路径>
```

## JSON 固定结构

```json
{
  "schema_version": "1.0",
  "document": {
    "source": "绝对路径",
    "output": "绝对路径或 null",
    "mode": "audit_only",
    "rule_profile": "general_academic_docx",
    "reviewed_at": "YYYY-MM-DDTHH:mm:ss+08:00",
    "rule_sources": [],
    "school_requirements": {
      "provided": false,
      "sources": [],
      "scope": {
        "school": null,
        "department": null,
        "degree_level": null,
        "document_type": null
      },
      "version": null,
      "effective_date": null,
      "extracted_file": null,
      "status": "not_provided",
      "confidence": "not_provided",
      "unconfigured_checks": []
    },
    "content_protected_items": [],
    "visual_exceptions": []
  },
  "summary": {
    "severity_counts": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
    "word_count": 0,
    "required_word_count": null,
    "bibliography_count": 0,
    "required_bibliography_count": null,
    "gbt7714_version_rule": {
      "required_version": null,
      "status": "not_configured",
      "rule_source": null
    },
    "content_completeness_rule": {
      "status": "not_configured",
      "required_sections": [],
      "rule_source": null
    },
    "unconfigured_school_checks": [],
    "in_text_citation_count": 0,
    "cross_reference_field_count": 0,
    "figure_caption_count": 0,
    "table_caption_count": 0,
    "formula_count": 0,
    "footnote_count": 0,
    "endnote_count": 0,
    "modified_object_count": 0,
    "new_comment_count": 0
  },
  "issues": [
    {
      "id": "REF-01",
      "category": "引用",
      "severity": "P1",
      "location": {"page": 0, "paragraph": 0, "text": ""},
      "evidence": {"kind": "literal_text", "value": ""},
      "impact": "",
      "suggestion": "",
      "status": "unmodified",
      "protected": false,
      "protection_type": "none",
      "rule_source": "",
      "requires_school_rule": false,
      "change": null,
      "comment": null
    }
  ],
  "normal_checks": [],
  "verification": {
    "school_requirements_extraction": "not_provided",
    "ooxml_fields": "passed",
    "all_accessible_parts": "passed",
    "python_docx_open": "passed",
    "revisions_hidden_text_metadata": "passed",
    "word_readonly_pdf": "passed"
  }
}
```

## 状态值

`issues[].status` 只使用：

- `found`：已发现，尚未决定是否修改。
- `unmodified`：明确未修改，通常因为保护项或用户未授权。
- `modified`：已在目标副本中修改并复核。
- `needs_confirmation`：需要用户决定，不能自动修改。
- `verified_normal`：检查后正常；一般放入 `normal_checks`，不放入问题表。

## 写作要求

- 证据优先写原文、字段指令、段落/页码和计数，不写泛泛评价。
- 同一根因导致的多个位置可合并为一个问题，但在证据中列出全部位置或数量。
- 保护项即使有问题也必须出现在“问题表”或“保护项与未处理项”中，不能为了得到“无问题”而省略。
- `suggestion` 是建议，不代表已经执行；实际执行情况只写在 `status`、`change` 和 `comment` 中。
