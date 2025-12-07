#!/bin/bash

# rectangle_count问题评测脚本
API_URL=${API_URL:-"http://localhost:8000/v1"}
MODEL_NAME=${MODEL_NAME:-"unknown"}
API_KEY=${API_KEY:-"null"}

# 定义要遍历的难度列表
DIFFICULTIES=("easy" "hard")
HAS_RUN=false

for DIFF in "${DIFFICULTIES[@]}"; do
    # 动态查找对应难度的数据集
    DATASET=$(find data/rectangle_count -maxdepth 1 -name "*${DIFF}*train*.jsonl" -o -name "*train*${DIFF}*.jsonl" | sort | tail -n 1)
    
    DIFF_DISPLAY="$(tr '[:lower:]' '[:upper:]' <<< ${DIFF:0:1})${DIFF:1}"

    if [ -n "$DATASET" ]; then
        HAS_RUN=true
        echo "=========================================="
        echo "开始评测 ${DIFF_DISPLAY} 数据集: $DATASET"
        echo "=========================================="
        
        python -m internbootcamp.utils.run_evaluation \
          --dataset-path "$DATASET" \
          --output-dir outputs/ \
          --api-key "${API_KEY}" \
          --api-url "${API_URL}" \
          --api-model "${MODEL_NAME}" \
          --reward-calculator-class "internbootcamp.bootcamps.reasoning-gym.rectangle_count.reward_calculator.RectangleCountRewardCalculator" \
          --max-concurrent 32 \
          --verbose
        
        echo "${DIFF_DISPLAY} 数据集评测完成"
        echo ""
    else
        echo "警告: 未找到 ${DIFF} train 数据集，跳过"
    fi
done

# 如果两次循环都没有找到文件，则报错退出
if [ "$HAS_RUN" = false ]; then
    echo "错误: 未找到 easy 或 hard 的 train jsonl 文件"
    exit 1
fi

echo "=========================================="
echo "所有数据集评测完成!"
echo "=========================================="