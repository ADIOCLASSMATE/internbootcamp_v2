#!/bin/bash

# 容器盛水问题评测脚本
PORT=${PORT:-8000}
MODEL_NAME=${MODEL_NAME:-"deepseek-ai/DeepSeek-V3"}

# 查找数据集 - 支持多种命名模式
DATASET=$(find data/container_with_most_water -maxdepth 1 -name "train*.jsonl" -o -name "*train.jsonl" | sort | tail -n 1)

# 评测 easy 数据集
if [ -n "$DATASET" ]; then
    echo "=========================================="
    echo "开始评测数据集: $DATASET"
    echo "=========================================="
    
    python -m internbootcamp.utils.run_evaluation \
      --dataset-path "$DATASET" \
      --output-dir outputs/ \
      --api-key "null" \
      --api-url "http://localhost:${PORT}/v1" \
      --api-model ${MODEL_NAME} \
      --reward-calculator-class "internbootcamp.bootcamps.container_with_most_water.reward_calculator.ContainerWithMostWaterRewardCalculator" \
      --max-concurrent 32 \
      --verbose
    
    echo "评测完成"
    echo ""
else
    echo "警告: 未找到数据集，跳过"
fi

echo "结果保存在 outputs/ 目录下"
echo "可以使用以下命令查看结果:"
echo "  ls -lh outputs/"
