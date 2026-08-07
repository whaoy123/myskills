---
name: connector-wiring-table-generator
summary: 从原理图、连接器针脚定义、旧接线表和用户说明生成可直接用于做线/验线的标准接线表 Excel。
description: Use this skill when the user provides schematics, connector pin tables, wiring examples, PDFs, screenshots, or verbal background and needs a polished xlsx wiring table for an adapter cable or harness. The skill emphasizes physical cable endpoints, mating direction, connector naming, pin numbering, multi-pin parallel nets, NC pins, wire type, concise styling, connector-description sheets, and electrical characteristics sourced from authoritative connector documentation such as the AVRplus connector pin definition PDF.
---

# 通用线缆接线表生成 Skill

## 1. 目标

将原理图、连接器定义、旧接线表、用户说明整理为可直接交给做线/焊线/验线人员使用的 `.xlsx` 接线表。

核心流程：

> 先确认物理线缆两端与对接关系 → 提取 pin/net 映射 → 确认公母与线型 → 生成接线 Sheet → 生成连接器说明 Sheet → 补充电气属性 → 自检。

禁止仅凭原理图器件名猜线缆端公母、镜像关系或最终连接器型号。

## 2. 输入资料优先级

1. **用户当前明确说明**：优先级最高。
2. **用户给出的旧接线表**：用于沿用线型、命名和映射习惯。
3. **当前原理图 / PCB 图**：用于确认板端接口、pin-to-net、左右方向、IN/OUT、多针并联。
4. **连接器/设备官方 PDF**：用于补充 Pin、AWG、Description、Electrical Characteristics。
5. **旧项目资料**：仅作辅助，不能覆盖当前用户明确说明。

例如 AVRplus 项目中，电气属性优先取自 `AVRplus CONNECTOR PIN DEFINITION` 表，而不是自行估算。

## 3. 生成前必须确认的物理关系

正式生成前要确认：

- 线缆一端是什么连接器；
- 线缆另一端是什么连接器；
- 哪一端接设备，哪一端接测试板；
- 板上 J/U 编号与线缆端 L 编号之间的关系；
- 公头/母头；
- 节点号按标准 pin number 还是特殊视角编号；
- 多针并联是否展开；
- NC/Reserved 是否保留；
- 线型是否沿用已有接线表。

如果用户已明确给出示意图，例如：

`UTG62448SN → L1/U1、L2/J1、L3/J4、L4/U3 → 测试板 → U2/L5、J2/L6、J3/L7、U4/L8 → UTG02448P`

则直接按该关系生成，不再自行改解释。

## 4. Sheet 结构标准

默认按用户实际方向/线缆分 Sheet。

典型结构：

1. `AVRplus方向`
2. `发电机方向`
3. `连接器型号`

如果用户有其他数量要求，按用户要求。

### 4.1 连接器型号 Sheet 必须保留

只要接线表中使用了 L1/L2/L3... 这类线缆端编号，默认必须生成 `连接器型号` Sheet。

推荐列：

| 线缆端编号 | 连接器型号/规格 | 公母/端接形式 | 对接板端 | 对接对象 | 说明 |
|---|---|---|---|---|---|

要求：

- L1/L2... 与板上 U1/J1/J4 等明确对应；
- 型号已知则写具体型号；
- 型号未知但只知道类别时，不要只写笼统的“连接器”，应尽可能写准确类别，例如 `7.62mm栅栏式接线端子`、`5.0mm螺钉式接线端子`、`DB44公头`；
- 公母关系必须以用户确认或实际对接关系为准。

### 4.2 已确认的端子类别命名

对于当前 SPB / AVRplus 项目，以下名称作为标准写法，后续接线表与连接器型号页统一使用：

| 板端位号 | 型号 | 标准类别名称 |
|---|---|---|
| U1 / U2 | `DBT10-7.62-6P-GN` | `7.62mm栅栏式接线端子` |
| J1 / J2 | `DB127V-5.0-3P-GN-S` | `5.0mm螺钉式接线端子` |

例如 `L1` 对接 `U1` 时，连接器型号页说明应写成“对接 U1（7.62mm栅栏式接线端子）”；`L2` 对接 `J1` 时，应写成“对接 J1（5.0mm螺钉式接线端子）”。

已知类别时不要退化成“6P连接器”“3P连接器”或“普通连接器”。

## 5. 接线 Sheet 固定列结构

以后默认采用下面的简洁格式：

| 序号 | 连接点1代号 | 节点号1 |  | 连接点2代号 | 节点号2 | 线型 | 信号定义 | 电气属性/备注 |
|---:|---|---|---|---|---|---|---|---|

### 5.1 中间空白分隔列

**节点号1 与连接点2代号之间必须插入 1 个空白列**，用于视觉分隔两端连接关系。

也就是：

- A：序号
- B：连接点1代号
- C：节点号1
- D：空白分隔列
- E：连接点2代号
- F：节点号2
- G：线型
- H：信号定义
- I：电气属性/备注

空白列 D 不写数据，宽度保持窄一些即可。

## 6. 线型规则

优先沿用用户已有接线表中的线型，不自行换算 AWG。

例如现有项目中：

- 普通信号：`0.5`
- Field / High Current Field：`1.5/0.2`

如果旧接线表已经给出线型，则按相同信号继承。

若没有依据，必须询问用户，不能凭经验猜死。

## 7. 电气属性/备注标准

### 7.1 来源

优先来自设备/连接器官方针脚定义 PDF。

例如 AVRplus PDF 的 `AVRplus CONNECTOR PIN DEFINITION` 中包含：

- Pin
- AWG
- Description
- Electrical Characteristics

应将其中的 `Electrical Characteristics` 简明写入接线表最后一列 `电气属性/备注`。

### 7.2 写法

只保留对做线和安全有意义的信息，不要整段照搬。

示例：

| 信号 | 电气属性/备注写法示例 |
|---|---|
| POR Phase A/B/C | `300/600Vac，360–2000Hz，10mA，隔离输入` |
| PMG Phase A/B/C | `140Vac，400–5600Hz，5A` |
| Line/Gen CT | `0.85A连续，1A/5s，隔离输入` |
| Cable ID ± | `Cable ID 电阻检测` |
| DC Common | `5A DC Common` |
| +28 VDC | `5A 输入` |
| Field ± | `300V，7A；并联高电流端时最高25A` |
| Servo Drive Com | `0–120mA DC 电流回路` |
| GCU On Input | `28VDC 输入` |
| GCU 28 VDC out | `28VDC，1A 输出` |
| GCR Status Output | `28VDC 状态输出` |
| High Current Field ± | `300V，25A max` |
| ROLS | `ROLS 状态/故障输入` |
| Shield / Chassis Ground | 写清屏蔽或机壳地，不与信号地混淆 |

若官方 PDF 没有给出电气属性，则留空或写 `资料未给出`，不要自行补参数。

### 7.3 表尾说明行

每个接线 Sheet 最后增加 1～2 行说明：

- `节点号按连接器标准引脚号填写，不因公母视图反向而手动镜像；焊接时以实物焊杯/壳体标号为准。`
- `电气属性依据设备官方连接器定义表整理，仅用于做线与验线参考。`

如存在多针并联，再增加：

- `同一信号多针并联已逐针展开。`

## 8. 映射规则

- 每一行表示一个明确连接关系；
- 同一个源脚连接多个目标针脚时，逐行展开；
- 多针并联必须全部展开；
- 目标脚冲突必须报错/询问用户；
- NC/Reserved 是否保留由用户规则决定，默认保留并标记；
- Field + / Field -、High Current Field + / -、IN/OUT 不能因名称相近而混并；
- Shield、PMG Shield、Chassis Ground 不得混淆；
- 原理图网络名保持原始英文命名，必要时只在备注中补中文。

## 9. 公母与编号规则

默认原则：

> 接线表写连接器标准引脚号，不因公头/母头正视图或焊接面视图不同而人为镜像。

焊接时：

> 以厂家针脚图 + 实物壳体/焊杯编号为准。

如果用户明确要求使用焊接面视角编号，才按用户规则修改。

## 10. 样式标准

以后接线表统一使用简洁样式：

- 白底；
- 黑色正文；
- 标题加粗；
- 表头浅灰；
- 少量深灰/黑色边框；
- 不使用蓝/绿/橙等多色分区；
- 中间空白列作为两端连接关系分隔；
- 行高统一；
- 自动换行；
- 节点号、序号、线型居中；
- 冻结表头；
- 不使用渐变和装饰性配色。

推荐视觉：**黑字 + 白底 + 浅灰表头 + 细边框 + 中间窄空白列**。

## 11. 生成后自检

交付前至少检查：

1. Sheet 数量和顺序正确；
2. `连接器型号` Sheet 未遗漏；
3. L1/L2... 与板端 J/U 对应正确；
4. 已确认的端子类别名称已准确写出，不使用笼统“连接器”替代；
5. 连接点1/连接点2方向没有写反；
6. 节点号1 与连接点2之间存在空白分隔列；
7. 多针并联已逐针展开；
8. Field/High Current Field 极性与 IN/OUT 正确；
9. 线型来自用户旧表或明确说明；
10. 电气属性来自官方 PDF 或用户资料；
11. 不存在人为镜像编号；
12. 每个接线 Sheet 底部有标准说明行；
13. Excel 可正常打开，无公式错误；
14. 配色简洁，无多余颜色。

## 12. 标准交付话术

> 已按统一接线表标准生成：简洁黑白/浅灰配色、两端中间增加空白分隔列、保留连接器型号 Sheet、已知端子使用准确类别名称，并在最后一列补充官方资料中的电气属性。  
> [下载接线表](sandbox:/mnt/data/xxx.xlsx)
