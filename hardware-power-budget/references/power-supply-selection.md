# Power Supply Selection

## 1. 先确定真实输入范围

“28 V 输入”不能只检查 datasheet 是否写支持 28 V。必须确认真实：

```text
VIN_nominal
VIN_min
VIN_max
启动/瞬态范围
极性与反接要求
```

若用户只给 nominal，选型结论写成“按 28 V nominal，输入范围仍待确认”。

## 2. 每条输出 rail 的硬条件

至少检查：

```text
Vout nominal/trim
Iout rated >= Idesign_min
Pout rated >= Pdesign_min
温度降额后仍满足
纹波/噪声满足模拟链路
启动到容性负载能力
短路/过流/过温保护
```

## 3. 隔离 DC/DC

额外检查：

- 隔离耐压是生产测试值还是长期工作绝缘额定；
- reinforced/basic/functional isolation 是否符合用途；
- creepage / clearance 与系统要求；
- 输入输出共模/隔离电容；
- 允许的输出电容；
- 最小负载要求；
- 输出纹波与后级滤波；
- 隔离域是否必须彼此独立。

不同 primary high-side rail 如果承担独立隔离屏障，不要仅因为电压相同就合并到一个非隔离公共输出。

## 4. 双路 ± 输出

对 `±15 V` 模块：

- 检查 `+15 V` 单路电流；
- 检查 `-15 V` 单路电流；
- 检查双路合计功率；
- 检查负载不平衡限制；
- 检查空载/轻载时输出是否漂移；
- 若后级是精密模拟，检查 cross regulation。

## 5. 效率与输入电流

实际最坏输入电流：

```text
Iin_worst ≈ Pout_worst / (η_min × Vin_min) + Iq
```

若只知道典型效率：

```text
Iin_est ≈ Pout_worst / (η_typ × Vin) + Iq
```

必须标“估算”，不要称为保证值。

如果用户问“输入电源至少多大”，应使用整个电源树回推后的 root rail 电流，再留输入侧工程余量/保险丝/连接器余量。

## 6. 选型输出格式

推荐型号时每个候选至少列：

| 型号 | 输入范围 | 输出 | 额定功率 | 设计最低需求 | 利用率 | 隔离 | 关键注意点 |
|---|---|---|---:|---:|---:|---|---|

优先官方 datasheet 与厂商产品页，库存/价格若用户要求再查经销商。
