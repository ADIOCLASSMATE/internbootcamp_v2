import os
import csv
import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configuration
OUTPUTS_DIR = "outputs"
CONTAINER_DIR = "container"
os.makedirs(CONTAINER_DIR, exist_ok=True)

# Model mapping and order
MODELS = [
    "Qwen2.5-VL-7B-Instruct",
    "Qwen2.5-VL-32B-Instruct",
    "Qwen2.5-VL-72B-Instruct",
    "Qwen3-VL-8B-Instruct",
    "Qwen3-VL-32B-Instruct",
    "Qwen3-VL-235B-A22B-Instruct"
]

# Paper benchmarks (percentages)
PAPER_BENCHMARKS = {
    "Qwen2.5-VL-7B-Instruct": 6.7,
    "Qwen2.5-VL-32B-Instruct": 16.7,
    "Qwen2.5-VL-72B-Instruct": 26.7
}

def parse_csv(file_path):
    data = {
        "overall": 0.0,
        "levels": {}
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find sections
    overall_start = -1
    detailed_start = -1
    
    for i, line in enumerate(lines):
        if "Overall Statistics" in line:
            overall_start = i
        if "Generator Detailed Statistics" in line:
            detailed_start = i
            
    # Parse Overall
    if overall_start != -1:
        # Assuming header is next line, data is line after
        # Metric,Value
        # ...
        # Overall Average Score,0.1160
        for i in range(overall_start + 1, detailed_start if detailed_start != -1 else len(lines)):
            parts = lines[i].strip().split(',')
            if len(parts) >= 2 and parts[0] == "Overall Average Score":
                try:
                    data["overall"] = float(parts[1]) * 100 # Convert to percentage
                except:
                    pass
                break
                
    # Parse Detailed
    if detailed_start != -1:
        # Header: Data Source,Generator Name,...,Average Score,...
        header_line = lines[detailed_start + 1].strip().split(',')
        try:
            gen_name_idx = header_line.index("Generator Name")
            score_idx = header_line.index("Average Score")
        except ValueError:
            return data

        for i in range(detailed_start + 2, len(lines)):
            parts = lines[i].strip().split(',')
            if len(parts) <= max(gen_name_idx, score_idx):
                continue
            
            gen_name = parts[gen_name_idx]
            if "level_" in gen_name:
                try:
                    score = float(parts[score_idx]) * 100
                    data["levels"][gen_name] = score
                except:
                    pass
                    
    return data

results = {}

for model in MODELS:
    model_dir = os.path.join(OUTPUTS_DIR, model)
    if not os.path.exists(model_dir):
        print(f"Warning: {model_dir} not found")
        continue
        
    csv_files = glob.glob(os.path.join(model_dir, "*.csv"))
    if not csv_files:
        print(f"Warning: No CSV found in {model_dir}")
        continue
        
    # Take the latest one
    latest_csv = max(csv_files, key=os.path.getmtime)
    print(f"Processing {model}: {latest_csv}")
    results[model] = parse_csv(latest_csv)

# --- Generate Table ---
table_content = r"""\begin{tabular}{lcccccc}
\toprule
\textbf{Model} & \textbf{Overall} & \textbf{Level 1} & \textbf{Level 2} & \textbf{Level 3} & \textbf{Level 4} & \textbf{Level 5} \\
\midrule
"""

for model in MODELS:
    if model in results:
        res = results[model]
        model_name = model.replace('_', r'\_')
        row = f"{model_name}"
        row += f" & {res['overall']:.2f}"
        for i in range(1, 6):
            level_key = f"level_{i}"
            val = res['levels'].get(level_key, 0.0)
            row += f" & {val:.2f}"
        row += r" \\" + "\n"
        table_content += row

table_content += r"\bottomrule" + "\n" + r"\end{tabular}"

with open(os.path.join(CONTAINER_DIR, "model_comparison_table.tex"), "w") as f:
    f.write(table_content)

# --- Generate Plots ---

# Set global font size
plt.rcParams.update({'font.size': 12})

# 1. Overall Comparison Bar Chart
plt.figure(figsize=(12, 6))
models_found = [m for m in MODELS if m in results]
scores = [results[m]['overall'] for m in models_found]
# Scientific colors: Soft Blue for Qwen2.5, Soft Red for Qwen3
colors = ['#7293CB' if 'Qwen2.5' in m else '#D35E60' for m in models_found]

bars = plt.bar(range(len(models_found)), scores, color=colors, alpha=0.9, edgecolor='grey', linewidth=0.5)
plt.xticks(range(len(models_found)), [m.replace("-Instruct", "").replace("Qwen", "Q") for m in models_found], rotation=45, ha='right', fontsize=10)
plt.ylabel('Average Score (%)', fontsize=12)
plt.title('Overall Performance Comparison', fontsize=14, fontweight='bold')
plt.grid(axis='y', linestyle='--', alpha=0.4)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{height:.1f}',
             ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(CONTAINER_DIR, "overall_comparison.png"), dpi=300)
plt.close()

# 2. Difficulty Level Analysis (Grouped Bar Chart)
plt.figure(figsize=(14, 7))
x = np.arange(5)  # 5 levels
width = 0.13  # width of bars

# Soft Professional color palette
model_colors = ['#7293CB', '#E1974C', '#84BA5B', '#D35E60', '#808585', '#9067A7']

for i, model in enumerate(models_found):
    level_scores = [results[model]['levels'].get(f"level_{j}", 0) for j in range(1, 6)]
    color = model_colors[i % len(model_colors)]
    plt.bar(x + i*width, level_scores, width, label=model.replace("-Instruct", ""), color=color, alpha=0.9, edgecolor='grey', linewidth=0.5)

plt.xlabel('Difficulty Level', fontsize=12)
plt.ylabel('Score (%)', fontsize=12)
plt.title('Performance by Difficulty Level', fontsize=14, fontweight='bold')
plt.xticks(x + width * (len(models_found) - 1) / 2, ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'], fontsize=10)
plt.legend(fontsize=10, frameon=True, fancybox=True, framealpha=0.9)
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(CONTAINER_DIR, "difficulty_analysis.png"), dpi=300)
plt.close()

# 3. Scaling Law (Qwen2.5-VL)
qwen25_models = [m for m in MODELS if "Qwen2.5-VL" in m]
qwen25_params = [7, 32, 72] # Billions
qwen25_scores = [results[m]['overall'] for m in qwen25_models if m in results]
paper_scores = [PAPER_BENCHMARKS[m] for m in qwen25_models if m in PAPER_BENCHMARKS]

if len(qwen25_scores) == len(qwen25_params):
    plt.figure(figsize=(8, 6))
    plt.plot(qwen25_params, qwen25_scores, 'o-', label='Our Evaluation', linewidth=2, markersize=8, color='#7293CB')
    plt.plot(qwen25_params, paper_scores, 's--', label='Paper Benchmark', linewidth=2, markersize=8, color='#E1974C')
    
    plt.xlabel('Model Parameters (Billions)', fontsize=12)
    plt.ylabel('Score (%)', fontsize=12)
    plt.title('Scaling Law: Qwen2.5-VL Series', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.4)
    
    # Annotate points
    for i, txt in enumerate(qwen25_scores):
        plt.annotate(f'{txt:.1f}', (qwen25_params[i], qwen25_scores[i]), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=10)
    
    for i, txt in enumerate(paper_scores):
        plt.annotate(f'{txt:.1f}', (qwen25_params[i], paper_scores[i]), xytext=(0, -15), textcoords='offset points', ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(CONTAINER_DIR, "scaling_law_qwen25.png"), dpi=300)
    plt.close()

# 4. Scaling Law (Qwen3-VL) - Assuming params
qwen3_models = [m for m in MODELS if "Qwen3-VL" in m]
# Mapping approximate params: 8B, 32B, 235B
qwen3_params = [8, 32, 235]
qwen3_scores = []
valid_params = []

for m, p in zip(qwen3_models, qwen3_params):
    if m in results:
        qwen3_scores.append(results[m]['overall'])
        valid_params.append(p)

if valid_params:
    plt.figure(figsize=(8, 6))
    plt.plot(valid_params, qwen3_scores, 'o-', color='#D35E60', label='Qwen3-VL', linewidth=2, markersize=8)
    
    plt.xlabel('Model Parameters (Billions)', fontsize=12)
    plt.ylabel('Score (%)', fontsize=12)
    plt.title('Scaling Law: Qwen3-VL Series', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.xticks(valid_params, [str(p) for p in valid_params])
    
    # Annotate points
    for i, txt in enumerate(qwen3_scores):
        plt.annotate(f'{txt:.1f}', (valid_params[i], qwen3_scores[i]), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(CONTAINER_DIR, "scaling_law_qwen3.png"), dpi=300)
    plt.close()

print("Data extraction and plotting complete.")
