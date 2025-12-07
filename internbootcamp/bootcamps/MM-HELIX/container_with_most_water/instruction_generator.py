import os
import random
import time
from typing import Dict, Any, Optional, List
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator


QUESTION_TEMPLATE = """Given a row of vertical bars where consecutive bars are adjacent with no gaps between them.
Pick any two bars and form the sides of a water container, with the x-axis as the base.
How much water can the biggest possible container hold?

Please analyze the image carefully and provide your answer.

Output Format:
Provide your final answer as an integer enclosed in \\boxed{{}}
"""


class ContainerWithMostWaterInstructionGenerator(BaseInstructionGenerator):
    case_counter = 0  # 类变量，用于生成唯一的 case_id
    
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "container_with_most_water"
        self.params = kwargs
        
        # 获取数据路径配置
        self.data_folder = kwargs.get('data_folder', 'data/container_with_most_water')
        self.output_base_dir = kwargs.get('output_base_dir', self.data_folder)
        
    def _get_difficulty_params(self, difficulty: int) -> Dict[str, tuple]:
        """根据难度级别获取参数配置"""
        if difficulty == 1:
            return {
                'data_range': (1, 20),
                'list_length_range': (5, 10)
            }
        elif difficulty == 2:
            return {
                'data_range': (1, 40),
                'list_length_range': (10, 20)
            }
        elif difficulty == 3:
            return {
                'data_range': (1, 60),
                'list_length_range': (20, 30)
            }
        elif difficulty == 4:
            return {
                'data_range': (1, 80),
                'list_length_range': (30, 40)
            }
        else:  # difficulty 5
            return {
                'data_range': (1, 100),
                'list_length_range': (40, 70)
            }
    
    def max_area_with_indices(self, heights: List[int]) -> int:
        """使用双指针算法计算最大面积"""
        left, right = 0, len(heights) - 1
        max_area_val = 0
        
        while left < right:
            width = right - left
            height = min(heights[left], heights[right])
            area = width * height
            
            if area > max_area_val:
                max_area_val = area
                
            if heights[left] <= heights[right]:
                left += 1
            else:
                right -= 1
        
        return max_area_val
    
    def _generate_plot(self, data: List[int], output_path: str):
        """生成柱状图可视化 - 使用非交互式方式直接保存"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 使用 Agg 后端，不创建窗口
        import matplotlib
        matplotlib.use('Agg')
        
        # 浅蓝色渐变（pastel_sky风格）
        gradient_colors = [(0.8, 0.9, 1.0), (0.5, 0.7, 0.9)]
        custom_cmap = LinearSegmentedColormap.from_list('custom_gradient', gradient_colors)
        
        # 白色背景
        background_color = '#FFFFFF'
        
        # 创建图形（不会打开窗口）
        from matplotlib.figure import Figure
        fig = Figure(figsize=(10, 6), dpi=150, facecolor=background_color)
        ax = fig.add_subplot(111, facecolor=background_color)
        
        base_colors = custom_cmap(np.linspace(0, 1, len(data)))
        
        for i in range(len(data)):
            ax.bar(i, data[i], width=1.0, color=base_colors[i], 
                   edgecolor='white', linewidth=0.5, alpha=0.9, zorder=2, align='center')
            
        # 数据标签
        for i, val in enumerate(data):
            ax.text(i, val + max(data) * 0.03, f'{int(val)}', ha='center', va='bottom',
                    fontsize=7, fontweight='bold', color='#333333', zorder=4)
            
        # 网格和样式
        ax.grid(axis='y', linestyle='-', alpha=0.2, color='#B0C4DE')
        for spine in ax.spines.values(): 
            spine.set_visible(False)
        ax.set_xticks([])
        ax.set_ylim(0, max(data) * 1.15 if data else 10)
        ax.yaxis.set_ticks([])
        
        # 直接保存，不使用 plt
        fig.tight_layout(pad=1.5)
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=background_color)
        
        # 清理
        fig.clf()
        plt.close(fig)
    
    def case_generator(self) -> Dict[str, Any]:
        """
        生成一个样本（支持多模态）
        
        Returns:
            identity 字典，包含 question, image, ground_truth 等
        """
        ContainerWithMostWaterInstructionGenerator.case_counter += 1
        
        # 解析难度级别（例如 "level_2" -> 2）
        difficulty_level = 1
        if self.difficulty and isinstance(self.difficulty, str):
            if self.difficulty.startswith('level_'):
                try:
                    difficulty_level = int(self.difficulty.split('_')[1])
                except (IndexError, ValueError):
                    difficulty_level = 1
            elif self.difficulty.startswith('difficulty'):
                try:
                    difficulty_level = int(self.difficulty.split('difficulty')[1])
                except (IndexError, ValueError):
                    difficulty_level = 1
        
        # 获取难度参数
        params = self._get_difficulty_params(difficulty_level)
        
        # 使用 time.time() 作为随机种子
        seed = self.params.get('seed', 42)
        random.seed(seed + ContainerWithMostWaterInstructionGenerator.case_counter + int(time.time() * 1000))
        
        # 生成随机高度列表
        length = random.randint(*params['list_length_range'])
        heights = [random.randint(*params['data_range']) for _ in range(length)]
        
        # 为高难度增加一些峰值
        if difficulty_level >= 3:
            num_peaks = random.randint(2, 3)
            if length >= num_peaks:
                peak_positions = random.sample(range(length), num_peaks)
                for pos in peak_positions:
                    heights[pos] = random.randint(int(params['data_range'][1] * 0.7), params['data_range'][1])
        
        # 计算答案
        answer = self.max_area_with_indices(heights)
        
        # 生成图像文件名和路径
        image_filename = f"ContainerWithMostWater_{self.difficulty}_{ContainerWithMostWaterInstructionGenerator.case_counter}.png"
        
        # 创建图像目录并生成图像
        images_dir = os.path.join(self.output_base_dir, "images")
        image_full_path = os.path.join(images_dir, image_filename)
        
        # 生成图像
        self._generate_plot(heights, image_full_path)
        
        # 图像的相对路径（相对于数据集根目录）
        image_relative_path = os.path.join("images", image_filename)
        
        # 文本描述（不泄漏具体数值）
        text_description = (
            f"The image shows a bar chart with {len(heights)} vertical bars of different heights. "
            f"Each bar represents a vertical line at position i with height h[i]. "
            f"Two bars can form a container with the x-axis as the base. "
            f"Find the maximum amount of water such a container can hold."
        )
        
        return {
            "difficulty": self.difficulty,
            "question": QUESTION_TEMPLATE,  # 文本问题
            "question_language": text_description,  # 额外的文本描述
            "image": image_relative_path,  # 图像相对路径
            "ground_truth": answer,
            "heights": heights,
            "source_dataset": "container_with_most_water"
        }
    
    def prompt_func(self, identity: Dict[str, Any]) -> Dict[str, str]:
        """
        生成 prompt（多模态格式）
        
        Args:
            identity: case_generator 生成的 identity
        
        Returns:
            包含图像路径和文本的字典
        """
        # 图像路径需要相对于项目根目录（data_folder 已包含正确的相对路径前缀）
        image_path = os.path.join(self.data_folder, identity["image"])
        
        # 返回字典格式以支持多模态
        return {
            "prompt_img": image_path,  # 图像相对路径（相对于项目根目录）
            "prompt_txt": identity["question"],  # 文本问题
            "question": identity["question"]  # 额外的 question 字段
        }


if __name__ == "__main__":
    print("Testing ContainerWithMostWaterInstructionGenerator")
    print("=" * 70)
    
    # 测试不同难度级别
    test_configs = [
        {"difficulty": "level_1", "output_base_dir": "test_output"},
        {"difficulty": "level_3", "output_base_dir": "test_output"},
        {"difficulty": "level_5", "output_base_dir": "test_output"},
    ]
    
    for config in test_configs:
        print(f"\nTesting {config['difficulty']}:")
        print("-" * 70)
        
        generator = ContainerWithMostWaterInstructionGenerator(**config)
        identity = generator.case_generator()
        
        print(f"  Difficulty: {identity['difficulty']}")
        print(f"  Heights: {identity['heights']}")
        print(f"  Ground truth (max area): {identity['ground_truth']}")
        print(f"  Image path: {identity['image']}")
        
        # 生成 prompt
        prompt = generator.prompt_func(identity)
        print(f"\n  Prompt preview (first 150 chars):")
        print(f"    {prompt[:150]}...")
    
    print("\n" + "=" * 70)
    print("Generator test completed!")
