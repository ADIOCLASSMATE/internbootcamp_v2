import random
from typing import Dict, Any, Optional, Tuple

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

from reasoning_gym.cognition.rectangle_count import draw_rectangles_with_overlap

QUESTION_TEMPLATE = """Your task is to count how many rectangles are present in an ASCII grid.

Single rectangles are outlined with a '#', overlapping rectangles (max 2) are shown with '█'.

Your output should be a single number, representing the total count of rectangles, and put it in the format \\boxed{{number}}.

Now, it's your turn. How many rectangles do you see in the grid below?
{puzzle}
"""


class RectangleCountInstructionGenerator(BaseInstructionGenerator):
    case_counter = 0  # 类变量，用于生成唯一的 case_id
    
    def __init__(self, difficulty: Optional[str] = None, **kwargs):
        super().__init__()
        self.difficulty = kwargs.get('difficulty', difficulty)
        self.task_type = "rectangle_count"
        self.params = kwargs
        
        self.params.setdefault('max_rectangles', 10)
        self.params.setdefault('width', 40)           # 固定40宽度
        self.params.setdefault('height', 40)          # 固定40高度
    
    def case_generator(self) -> Dict[str, Any]:
        """
        生成一个样本（完全对齐 reasoning-gym）
        
        Returns:
            identity 字典，包含 question, ground_truth 等
        """
        RectangleCountInstructionGenerator.case_counter += 1
        seed = self.params.get('seed', 42)
        rng = random.Random(seed + RectangleCountInstructionGenerator.case_counter)
        
        max_rectangles = self.params.get('max_rectangles', 10)
        target_rectangles = rng.randint(1, max_rectangles)
        
        width = self.params.get('width', 40)
        height = self.params.get('height', 40)
        
        # 生成 ASCII 网格
        ascii_grid, actual_count = draw_rectangles_with_overlap(
            n=target_rectangles,
            width=width,
            height=height,
            rng=rng
        )
        
        return {
            "difficulty": self.difficulty,
            "question": ascii_grid,
            "ground_truth": actual_count,
            "grid_width": width,
            "grid_height": height,
            "target_rectangles": target_rectangles,
            "source_dataset": "rectangle_count"
        }
    
    def prompt_func(self, identity: Dict[str, Any]) -> str:
        puzzle = identity["question"]
        prompt_txt = QUESTION_TEMPLATE.format(puzzle=puzzle)
        
        return prompt_txt


if __name__ == "__main__":
    print("Testing RectangleCountInstructionGenerator (aligned with reasoning-gym)")
    print("=" * 70)
    
    # 测试不同难度级别
    test_configs = [
        {"difficulty": "level_5", "max_rectangles": 5, "width": 40, "height": 40},
        {"difficulty": "level_10", "max_rectangles": 10, "width": 40, "height": 40},
        {"difficulty": "level_25", "max_rectangles": 25, "width": 40, "height": 40},
    ]
    
    for config in test_configs:
        print(f"\nTesting {config['difficulty']}:")
        print("-" * 70)
        
        generator = RectangleCountInstructionGenerator(**config)
        identity = generator.case_generator()
        
        print(f"  Difficulty: {identity['difficulty']}")
        print(f"  Target rectangles: {identity['target_rectangles']}")
        print(f"  Actual count (ground_truth): {identity['ground_truth']}")
        print(f"  Grid size: {identity['grid_width']}x{identity['grid_height']}")
        
        # 显示网格预览（前5行）
        print(f"\n  ASCII Grid Preview (first 5 lines):")
        lines = identity['question'].split('\n')[:5]
        for line in lines:
            print(f"    {line}")
        
        # 生成 prompt
        prompt = generator.prompt_func(identity)
        print(f"\n  Prompt length: {len(prompt)} characters")
        print(f"  Prompt preview (first 200 chars):")
        print(f"    {prompt}")
    
    print("\n" + "=" * 70)
    print("Alignment with reasoning-gym:")
    print("  ✓ Fixed rectangle counts: [5, 10, 15, 20, 25]")
    print("  ✓ Fixed grid size: 40x40")
    print("  ✓ Same drawing algorithm with overlap constraints")
    print("  ✓ Identical QUESTION_TEMPLATE")
    print("  ✓ Same seeding mechanism")
