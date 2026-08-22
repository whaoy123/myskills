---
name: altium-schematic-autowire
description: 根据用户已经确定的元件、引脚和网络连接关系，生成可审查的 Altium Designer 原理图批量放置与自动连线方案。优先处理重复通道、连接器扇出、Net Label、端口、总线、跨页连接和模板复制；默认输出规范化连接清单、校验报告和 DelphiScript/CSV，而不是替用户重新设计电路。
version: 1.0.0
---

# Altium Schematic Autowire Skill

## 1. 使用场景

在以下情况调用本 Skill：

- 用户已经知道具体如何连接，只是不想重复放置、编号和连线。
- 需要将 Excel、CSV、Markdown 表格或文字引脚表转换为 Altium 原理图。
- 需要批量生成三相、六路、十六路、四十四路等重复电路。
- 需要对连接器进行扇出，并批量连接到电阻、隔离器、ADC、MCU 等器件。
- 需要复制一个已验证通道并自动替换位号、网络名、通道号。
- 需要生成 DelphiScript、PrjScr、标准化 CSV 和审查报告。

不适用于：

- 用户尚未确定电路拓扑，要求 AI 自主设计高风险电源、保护或模拟电路。
- 用户只提供原理图截图，但无法确认元件位号或引脚含义。
- 用户要求脚本直接覆盖唯一工程且不允许备份。

## 2. 核心原则

1. **连接表是唯一连接真值源**。自然语言只能用于补充说明，不能覆盖结构化连接表。
2. **先校验，后生成**。存在重复位号、未知引脚、网络名冲突或悬空电源时，不直接生成最终脚本。
3. **优先局部短线 + Net Label**，避免跨页面长导线。
4. **重复结构必须模板化**，禁止逐通道手写相同脚本。
5. **默认只生成，不直接执行**。除非用户明确要求并具备可调用的 Altium 自动化接口。
6. **不猜元件库路径、不猜引脚编号、不猜多单元器件 Part ID**。
7. **所有输出必须可回滚、可审查、可重复执行**。
8. **脚本应幂等**：再次运行时不得无条件重复放置相同位号和对象。

## 3. 工作模式

### MODE-A：连接标签模式（默认，最快）

每个待连接引脚拉出 100–300 mil 短线并放置同名 Net Label。适合连接器扇出、ADC 多通道、跨区域连接。

### MODE-B：直连导线模式

仅用于相邻器件和局部功能块。使用正交折线，不允许穿过符号主体和文字。

### MODE-C：模板复制模式

输入一个基准通道和通道映射，批量生成其余通道。网络名、位号和坐标通过规则展开。

### MODE-D：仅生成网络定义

输出规范化 CSV/JSON 和网络审查结果，不生成图形对象。适合首次确认连接关系。

### MODE-E：修改现有原理图

读取已有器件位置和引脚数据，只补充缺失连接。执行前必须创建备份，并输出变更清单。

## 4. 必需输入

用户输入应组织为一个任务目录，至少包含：

```text
input/
├─ task.yaml
├─ components.csv
├─ connections.csv
└─ channel_map.csv        # 仅模板复制时需要
```

### 4.1 task.yaml

```yaml
project_name: AVRplus_Acquisition
eda: Altium Designer
eda_version: "23"
mode: label
source_document: Main.SchDoc
output_directory: generated
units: mil
snap_grid: 10
wire_stub_length: 200
backup_required: true
strict_pin_check: true
allow_unresolved_library: false
layout:
  origin_x: 1000
  origin_y: 7000
  channel_pitch_x: 1800
  channel_pitch_y: 1200
  max_channels_per_row: 4
naming:
  net_case: preserve
  duplicate_net_policy: merge
  designator_policy: fixed
validation:
  require_power_net_review: true
  require_no_duplicate_designator: true
  require_known_pin: true
  require_no_self_connection: true
```

### 4.2 components.csv

必需列：

```csv
Ref,LibraryRef,SourceLibrary,PartID,X,Y,Rotation,Mirror,Value,Footprint,Channel,Place
J1,DB44_FEMALE,MyConnector.SchLib,1,1000,7000,0,false,DB44,L77HDB44SD1CH4F,BASE,true
R1,RES_1M,MyPassive.SchLib,1,2400,7000,0,false,1M,0603,POR_A,true
U1,AMC3330,MyIC.SchLib,1,3800,7000,0,false,AMC3330,SOIC-16,POR_A,true
```

字段规则：

- `Ref`：全工程唯一。
- `LibraryRef`：Altium 符号名称。
- `SourceLibrary`：明确的 SchLib/IntLib 路径或项目库名称。
- `PartID`：多单元器件的单元编号；普通器件填 1。
- `X/Y`：可留空，由布局规则自动生成。
- `Place=false`：表示器件已存在，只用于连接。
- `Channel`：用于重复通道展开和审查。

### 4.3 connections.csv

推荐采用“一行一个网络端点”格式，而非一行一条两端连接。这样一个网络可以自然连接多个引脚。

```csv
NetName,Ref,Pin,PinName,EndpointType,Direction,WireMode,LabelSide,Channel,Comment
POR_A,J1,1,POR_A,pin,passive,label,right,POR_A,Connector input
POR_A,R1,1,,pin,passive,label,left,POR_A,
POR_A_DIV,R1,2,,pin,passive,label,right,POR_A,
POR_A_DIV,U1,2,INP,pin,input,label,left,POR_A,
AGND,U1,3,INN,pin,power,label,left,POR_A,
```

字段规则：

- `NetName`：不能为空，不允许首尾空格。
- `Ref + Pin`：必须能唯一定位引脚。
- `PinName`：可选，用于二次校验。
- `EndpointType`：`pin|port|power_port|sheet_entry|harness_entry|no_connect`。
- `Direction`：`input|output|bidirectional|passive|power`。
- `WireMode`：`label|direct|bus|harness|none`。
- `LabelSide`：`left|right|up|down|auto`。

### 4.4 channel_map.csv

```csv
TemplateChannel,NewChannel,RefMap,NetReplace,OffsetX,OffsetY
A,B,"R1:R2;U1:U2","POR_A:POR_B;POR_A_DIV:POR_B_DIV",0,-1200
A,C,"R1:R3;U1:U3","POR_A:POR_C;POR_A_DIV:POR_C_DIV",0,-2400
```

## 5. 可接受的简化输入

若用户只提供 Markdown 表格，应先转换为上述标准格式。例如：

```text
J1.1 -> R1.1 : POR_A
R1.2 -> U1.2 : POR_A_DIV
U1.3 -> AGND
```

必须先输出 `normalized_connections.csv`，待校验通过后才生成脚本。

## 6. 输入校验流程

按顺序执行：

1. 检查文件和必需列。
2. 去除单元格首尾空格，但不得改变网络名大小写，除非 task.yaml 指定。
3. 检查位号重复。
4. 检查同一位号的库符号是否冲突。
5. 检查每个连接端点的位号是否存在。
6. 检查引脚编号是否存在；无法读取库时标记 `UNVERIFIED_PIN`，不得伪装成已通过。
7. 检查同一引脚是否被分配到多个不同网络。
8. 检查同名网络方向冲突，例如多个强输出直接相连。
9. 检查 `no_connect` 引脚是否同时出现在其他网络。
10. 检查网络名中非法字符、空网络名和近似拼写。
11. 检查电源网、地网和隔离侧地是否被误合并。
12. 检查模板展开后位号、坐标和网络名是否冲突。
13. 生成摘要：元件数、网络数、端点数、悬空引脚数、未验证引脚数、错误数、警告数。

### 严格阻断错误

以下错误必须停止最终脚本生成：

- 重复位号。
- 同一引脚属于多个网络。
- 目标 SchDoc 不明确。
- 模板替换后产生重复位号。
- 已知库中不存在指定引脚。
- 输入要求覆盖源文件但未允许备份。

## 7. 原理图布局规则

1. 信号流默认从左到右。
2. 输入连接器在左，ADC/MCU 在右，保护和调理器件居中。
3. 电源在上，地在下。
4. 同类通道纵向排列，通道间距由 task.yaml 指定。
5. 所有对象坐标吸附到网格。
6. 直接导线仅走正交线。
7. 每个引脚短线长度统一，默认 200 mil。
8. Net Label 不覆盖元件、位号、参数或引脚名称。
9. 不通过导线交叉表达连接；连接必须有结点或同名网络标签。
10. 跨页连接使用 Port/Sheet Entry，不依靠普通 Net Label 隐式跨层级。
11. 隔离器两侧的 GND 网络必须保持不同名称，例如 `AGND_PRI`、`AGND_SEC`。
12. 高压和低压功能块在页面上保留明显间隔，并可放置文字分区标记。

## 8. DelphiScript 生成要求

输出脚本必须：

- 使用 Altium 官方脚本对象模型常见模式。
- 获取当前工程和目标 SchDoc，并检查为空情况。
- 在单次修改事务中创建对象，结束后刷新文档。
- 每个关键 API 调用都要检查对象是否成功创建。
- 用独立函数封装：查找器件、查找引脚、放置器件、创建短线、创建 Net Label、创建 Port、记录日志。
- 不使用无法确认存在的 API 名称；若 API 不确定，标记 TODO 并输出引用来源。
- 不将 CSV 解析逻辑与图形创建逻辑混在一个超长过程里。
- 支持 `DRY_RUN`。
- 支持 `SKIP_EXISTING`。
- 支持失败回滚或至少停止后不继续创建剩余对象。
- 输出详细日志到 `logs/run_YYYYMMDD_HHMMSS.log`。
- 保留 Altium 的一次 Undo 能力，尽量在单个事务完成。

推荐过程结构：

```pascal
procedure Main;
begin
    LoadTaskConfig;
    LoadComponents;
    LoadConnections;
    ValidateInput;
    if HasFatalErrors then Exit;
    OpenOrSelectTargetSchDoc;
    BeginSchematicTransaction;
    try
        PlaceMissingComponents;
        CreateConnections;
        AddAnnotations;
        CommitSchematicTransaction;
    except
        AbortSchematicTransaction;
        WriteFatalLog;
    end;
    RefreshDocument;
    WriteSummary;
end;
```

## 9. 固定输出格式

每次执行必须生成：

```text
output/
├─ 00_request_summary.md
├─ 01_normalized_components.csv
├─ 02_normalized_connections.csv
├─ 03_validation_report.md
├─ 04_change_plan.md
├─ 05_generation_manifest.json
├─ AltiumSchematicAutowire.PrjScr
├─ AltiumSchematicAutowire.pas
├─ run_instructions.md
└─ examples/
   └─ expected_result_description.md
```

### 9.1 03_validation_report.md 固定结构

```markdown
# Validation Report

## Result
PASS | PASS_WITH_WARNINGS | FAIL

## Summary
- Components: N
- Nets: N
- Endpoints: N
- Fatal errors: N
- Warnings: N
- Unverified pins: N

## Fatal Errors
| ID | Location | Problem | Required Fix |

## Warnings
| ID | Location | Problem | Recommendation |

## Net Review
| Net | Endpoints | Drivers | Loads | Status |

## Assumptions
- ...
```

### 9.2 04_change_plan.md 固定结构

```markdown
# Change Plan

## Target
- Project:
- Document:
- Mode:

## Objects to Create
| Type | Count | Notes |

## Objects to Modify
| Object | Existing State | New State |

## Objects Skipped
| Object | Reason |

## Rollback
- Backup file:
- Undo strategy:
```

### 9.3 generation_manifest.json

```json
{
  "skill": "altium-schematic-autowire",
  "version": "1.0.0",
  "status": "PASS",
  "target_document": "Main.SchDoc",
  "mode": "label",
  "counts": {
    "components": 3,
    "nets": 4,
    "endpoints": 8,
    "wires": 8,
    "labels": 8
  },
  "unresolved": [],
  "generated_files": []
}
```

## 10. 用户可见的最终答复格式

最终只按以下顺序给用户：

1. 一句话说明采用的模式。
2. 校验结论：PASS / PASS_WITH_WARNINGS / FAIL。
3. 三项以内的关键统计。
4. 需要用户人工确认的内容；没有则写“无”。
5. 输出文件链接或路径。
6. 在存在风险时明确写：**脚本必须先在工程副本运行。**

不得只回复“已生成”，不得隐藏未验证引脚和假设。

## 11. 决策规则

- 用户强调“最快”：选择 MODE-A。
- 用户要求图面像人工绘制：局部使用 MODE-B，其余使用 MODE-A。
- 用户有大量同构通道：选择 MODE-C。
- 用户的连接关系尚未最终确认：选择 MODE-D。
- 用户已有完整 SchDoc：优先 MODE-E，不重新放置全部器件。
- 用户没有库路径或引脚表：先生成连接清单和待补信息，不生成声称可直接运行的最终脚本。

## 12. 安全与工程边界

- 自动连线不等于电路设计验证。
- ERC 通过不代表模拟性能、隔离安全、耐压或 EMC 合格。
- 对高压、隔离、励磁、电流采样和航空接口，必须保留人工审查。
- 不自动合并名称相似的地网、电源网和屏蔽网。
- 不自动修改原理图库符号引脚编号。
- 不自动删除现有连接，除非用户在变更表中逐项授权。

## 13. 参考实现选择

默认优先级：

1. Altium DelphiScript 离线批量生成。
2. 已部署 Altium MCP 时，调用 MCP 完成读取、放置和校验。
3. 需要跨平台或代码化重建时，考虑 KiCad + SKiDL/Circuit-Synth/atopile。
4. 不建议用屏幕坐标宏作为主要实现；只能作为没有 API 时的临时方案。

