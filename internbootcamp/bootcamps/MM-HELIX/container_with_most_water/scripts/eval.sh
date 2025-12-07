#!/bin/bash

# container_with_most_water问题评测脚本
API_URL=${API_URL:-"http://localhost:8000/v1"}
MODEL_NAME=${MODEL_NAME:-"unknown"}
API_KEY=${API_KEY:-"null"}

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
      --api-key "${API_KEY}" \
      --api-url "${API_URL}" \
      --api-model ${MODEL_NAME} \
      --reward-calculator-class "internbootcamp.bootcamps.MM-HELIX.container_with_most_water.reward_calculator.ContainerWithMostWaterRewardCalculator" \
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
