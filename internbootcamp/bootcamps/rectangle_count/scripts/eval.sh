# 查找 easy 与 hard 数据集
EASY_DATASET=$(find data/rectangle_count -maxdepth 1 -name "*easy*train*.jsonl" -o -name "*train*easy*.jsonl" | sort | tail -n 1)

HARD_DATASET=$(find data/rectangle_count -maxdepth 1 -name "*hard*train*.jsonl" -o -name "*train*hard*.jsonl" | sort | tail -n 1)

# 检查是否找到数据集
if [ -z "$EASY_DATASET" ] && [ -z "$HARD_DATASET" ]; then
    echo "错误: 未找到 easy 或 hard 的 train jsonl 文件"
    exit 1
fi

# 评测 easy 数据集
if [ -n "$EASY_DATASET" ]; then
    echo "=========================================="
    echo "开始评测 Easy 数据集: $EASY_DATASET"
    echo "=========================================="
    
    python -m internbootcamp.utils.run_evaluation \
      --dataset-path "$EASY_DATASET" \
      --output-dir outputs/ \
      --api-key "null" \
      --api-url "http://localhost:${PORT}/v1" \
      --api-model ${MODEL_NAME} \
      --reward-calculator-class "internbootcamp.bootcamps.rectangle_count.reward_calculator.RectangleCountRewardCalculator" \
      --max-concurrent 32 \
      --verbose
    
    echo "Easy 数据集评测完成"
    echo ""
else
    echo "警告: 未找到 easy train 数据集，跳过"
fi

# 评测 hard 数据集
if [ -n "$HARD_DATASET" ]; then
    echo "=========================================="
    echo "开始评测 Hard 数据集: $HARD_DATASET"
    echo "=========================================="
    
    python -m internbootcamp.utils.run_evaluation \
      --dataset-path "$HARD_DATASET" \
      --output-dir outputs/ \
      --api-key "null" \
      --api-url "http://localhost:${PORT}/v1" \
      --api-model ${MODEL_NAME} \
      --reward-calculator-class "internbootcamp.bootcamps.rectangle_count.reward_calculator.RectangleCountRewardCalculator" \
      --max-concurrent 32 \
      --verbose
    
    echo "Hard 数据集评测完成"
    echo ""
else
    echo "警告: 未找到 hard train 数据集，跳过"
fi

echo "=========================================="
echo "所有数据集评测完成!"
echo "=========================================="
