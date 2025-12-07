import re
from typing import Dict, Any, Optional
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class RectangleCountRewardCalculator(BaseRewardCalculator):
    """
    归一化的奖励计算器
    
    - format_score: 0.1 (有格式) / 0.0 (无格式)
    - answer_score: 最高 0.9
      - 完全正确: 0.9
    """
    
    FORMAT_REWARD = 0.1      # 格式正确的奖励
    MAX_ANSWER_REWARD = 0.9  # 答案的最大奖励
    
    @classmethod
    def _check_format(cls, response: str) -> bool:
        """检查回答是否包含标准格式 (\boxed{数字})        
        """
        if not response or not isinstance(response, str):
            return False
        
        # 匹配 \boxed{数字} 格式
        pattern = r"\\boxed\{\s*\d+\s*\}"
        
        return bool(re.search(pattern, response, re.IGNORECASE))
    
    @classmethod
    def extract_output(cls, response: str) -> Dict[str, Any]:
        """从模型响应中提取数字和格式信息"""
        result = {"value": None, "has_format": False}
        
        if not response or not isinstance(response, str):
            return result
        
        # 检查格式
        result["has_format"] = cls._check_format(response)
        
        # 1. 优先匹配 oxed{数字} 格式
        match = re.search(r"\\boxed\{\s*(\d+)\s*\}", response, re.IGNORECASE)
        if match:
            try:
                result["value"] = int(match.group(1))
                return result
            except ValueError:
                pass
        
        # 2. 备选模式（兼容性考虑）
        patterns = [
            r"Answer:\s*(\d+)",
            r"答案[：:]\s*(\d+)",
            r"The answer is[：:\s]*(\d+)",
            r"total[：:\s]*(\d+)", 
            r"count[：:\s]*(\d+)",
            r"(\d+)\s*rectangles?",
            r"there are\s*(\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    result["value"] = int(match.group(1))
                    return result
                except ValueError:
                    continue
        
        # 3. 兜底策略：取最后一个数字
        numbers = re.findall(r'\b(\d+)\b', response)
        if numbers:
            try:
                result["value"] = int(numbers[-1])
            except ValueError:
                pass
        
        return result
    
    @classmethod
    def _calculate_score(cls, extracted_output: Dict[str, Any], identity: Dict[str, Any]) -> float:
        """
        核心计算逻辑：format_score + answer_score
        
        Returns:
            float: 总分 [0.0, 1.0]
        """
        # 1. 计算 format_score
        has_format = extracted_output.get('has_format', False)
        format_score = cls.FORMAT_REWARD if has_format else 0.0
        
        # 2. 获取真实标签
        ground_truth = identity.get('ground_truth')
        if ground_truth is None:
            ground_truth = identity.get('answer')
        
        # 确保 ground_truth 转为 int
        try:
            if ground_truth is not None:
                ground_truth = int(ground_truth)
        except (ValueError, TypeError):
            ground_truth = None

        # 3. 获取预测值
        user_value = extracted_output.get('value')

        # 4. 如果任一数值缺失，只返回 format_score
        if ground_truth is None or user_value is None:
            return format_score
        
        # 5. 计算 answer_score
        if user_value == ground_truth:
            answer_score = cls.MAX_ANSWER_REWARD
        else:
            answer_score = 0.0
        
        # 6. 总分 = format_score + answer_score
        total_score = format_score + answer_score
        
        return min(total_score, 1.0)  # 确保不超过 1.0
    
    @classmethod
    def _verify_correction(cls, extracted_output: Dict[str, Any], identity: Dict[str, Any], **kwargs) -> float:
        """BaseRewardCalculator 接口"""
        return cls._calculate_score(extracted_output, identity)
