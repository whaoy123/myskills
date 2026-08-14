# material_reimbursement_table_skill

发票自动解析与科研/办公材料验收单自动生成 Skill。

## 特性
- 自动解析增值税普通发票/专用发票（PDF）
- 支持立创商城、嘉立创 PCB、博信发、京东工业品等主流采购发票
- 自动处理多行明细、折扣行（负数扣减）、包装费与配送费
- 自动生成符合规范的材料验收单 Excel（支持含税与不含税模式）
- 自动写入 Excel 动态求和公式 `=SUM(E5:E...)`
- 严格保持原表格式排版（SimSun 宋体、边框、列宽、行高），保护历史 Sheet 数据

## 目录结构
```text
material_reimbursement_table_skill/
├── SKILL.md                          # 技能规范定义
├── README.md                         # 说明文档
├── scripts/
│   └── fill_reimbursement_table.py   # 执行脚本
├── templates/
│   └── 材料报销-原模板.xls          # 验收单原模板
├── examples/
│   └── 材料报销-示例(含税填报).xls    # 本批次生成示例
└── tests/
    └── test_fill_reimbursement_table.py # 单元测试
```

## 快速使用
```bash
python scripts/fill_reimbursement_table.py \
  --invoices-dir "发票PDF所在路径" \
  --template-xls "templates/材料报销-原模板.xls" \
  --output-xls "输出路径.xls"
```
