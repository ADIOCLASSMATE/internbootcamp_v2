"""
Container with Most Water Bootcamp

盛最多水的容器问题 - 多模态评测任务

该模块包含:
- reward_calculator.py: 奖励计算器，用于评估模型回答的准确性
- instruction_generator.py: 指令生成器，用于生成多模态数据集
- scripts/eval.sh: 评测脚本
"""

from .reward_calculator import ContainerWithMostWaterRewardCalculator
from .instruction_generator import ContainerWithMostWaterInstructionGenerator

__all__ = [
    'ContainerWithMostWaterRewardCalculator',
    'ContainerWithMostWaterInstructionGenerator',
]
