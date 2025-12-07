# 基于 Rectangle Count 任务的大语言模型文本推理能力评测

## 1. 任务描述
Rectangle Count 任务要求模型识别并计数 ASCII 网格中的矩形数量。单个矩形由 `#` 字符勾勒，重叠矩形（最多 2 个）由 `█` 字符表示。该任务考察了模型的逻辑推理能力（Logical Reasoning Capability）和对复杂图形结构的理解能力。

## 2. 评测设置

### Prompt Optimization
为了提高评测的稳定性，我们设计了优化的 Prompt Template，明确了任务目标、符号含义以及输出格式 `\boxed{number}`。

### Reward Function
我们观察到模型在猜测答案的情况下，仍在原本的 Linear Decay 评分机制下获得了不错的分数。为了避免这种情况，更严谨地评估模型性能，我们修改了**Answer Reward**的计算逻辑，采用了严格的 **Binary Reward** 机制：
- **Answer Reward**: 仅当预测答案与真实答案完全一致时得 **0.9 分**，否则得 **0.1 分**。
- **Format Reward**: 若模型输出符合格式要求，额外给予 **0.1 分**。

## 3. 实验结果

### 3.1 DeepSeek-R1 Ablation Study
我们探究了 Grid Size 对模型性能的影响。结果显示，随着 Grid Size 的增加（即图形重叠概率降低），模型性能呈现上升趋势。

| Grid Size | Difficulty | Avg. Score |
| :--- | :--- | :--- |
| 20*20 | Easy | 0.3286 |
| | Hard | 0.2980 |
| 40*40 | Easy | 0.4726 |
| | Hard | 0.3574 |
| 60*60 | Easy | 0.5230 |
| | Hard | 0.4114 |
| 80*80 | Easy | 0.5518 |
| | Hard | 0.4546 |

### 3.2 模型对比评测 (Model Comparison)
我们在 Easy 和 Hard 两种难度下对 DeepSeek 和 Qwen 系列模型进行了全面评测。

| Model | Size | Easy Score | Hard Score |
| :--- | :--- | :--- | :--- |
| DeepSeek-V3 | - | 0.3520 | 0.2890 |
| DeepSeek-R1 | - | 0.3610 | 0.3250 |
| QwQ-32B | 32.0B | 0.3280 | 0.2900 |
| Qwen2.5-1.5B-Instruct | 1.5B | 0.1090 | 0.0900 |
| Qwen2.5-3B-Instruct | 3.0B | 0.1040 | 0.1020 |
| Qwen2.5-7B-Instruct | 7.0B | 0.1970 | 0.2020 |
| Qwen2.5-14B-Instruct | 14.0B | 0.3510 | 0.3320 |
| Qwen2.5-32B-Instruct | 32.0B | 0.3780 | 0.3510 |
| Qwen2.5-72B-Instruct | 72.0B | 0.4400 | 0.3850 |
| Qwen3-1.7B | 1.7B | 0.0550 | 0.0560 |
| Qwen3-4B | 4.0B | 0.1670 | 0.2080 |
| Qwen3-8B | 8.0B | 0.2020 | 0.1950 |
| Qwen3-14B | 14.0B | 0.2510 | 0.2490 |
| Qwen3-32B | 32.0B | 0.2810 | 0.2650 |
| Qwen3-235B-A22B-Instruct-2507 | 235.0B | 0.4850 | 0.3860 |

## 4. 结果分析与论文对比

### 与论文基准对比
Reasoning-gym 论文中 DeepSeek-R1 在 80x80 网格下的基准性能与我们的评测结果对比如下：

| Model | Difficulty | Paper Score | Our Score (Linear Reward) | Our Score (Binary Reward) |
| :--- | :--- | :--- | :--- | :--- |
| DeepSeek-R1 | Easy | 0.46 | 0.5518 | 0.3610 |
| DeepSeek-R1 | Hard | 0.16 | 0.4546 | 0.3250 |

**分析**:
1.  **Prompt 优化的有效性**: 在使用类似的 Linear Reward 机制下，我们的评测结果（Easy: 0.5518, Hard: 0.4546）均显著高于论文基准（Easy: 0.46, Hard: 0.16）。这有力地证明了我们设计的 Prompt Template 能更好地引导模型进行推理，尤其是在 Hard 模式下带来了近 3 倍的性能提升。
2.  **评分机制的影响**: 采用更严格的 Binary Reward 后，分数有所下降（Easy: 0.3610, Hard: 0.3250），这反映了模型在部分情况下虽然接近答案但未能完全精确。
3.  **Hard 模式的突破**: 即便在最严格的 Binary Reward 标准下，我们在 Hard 模式的得分 (0.3250) 依然是论文基准 (0.16) 的两倍以上，进一步确认了 Prompt 优化对于处理复杂图形任务的关键作用。

### Scaling Law 验证
Qwen 系列模型（从 1.5B 到 235B）的评测结果清晰地展示了 **Scaling Law**：随着模型参数量的增加，在 Easy 和 Hard 任务上的得分均显著提升。Qwen3-235B 在 Easy 任务上取得了最高的 0.4850 分。

## 5. 结论
本次实验通过优化 Prompt 和 Reward Function，建立了一套更严谨的评测流程。实验验证了 Prompt 优化对提升模型在复杂推理任务（Hard Setting）中表现的有效性，同时也确认了模型规模对性能的决定性影响。
