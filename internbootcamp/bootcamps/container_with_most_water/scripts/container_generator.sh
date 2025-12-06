#!/bin/bash

# Container with Most Water 数据生成脚本
# 用于生成多模态数据集（图像 + 文本）

python -m internbootcamp.utils.batch_data_generation \
    --bootcamp-registry internbootcamp/bootcamps/container_with_most_water/configs/bootcamp_registry_container.jsonl \
    --output-dir data/container_with_most_water \
    --split-samples train:100,test:10 \
    --max-workers 64 \
    --log-level DEBUG \
    --continue-on-error \
    --no-tool \
    --no-interaction
