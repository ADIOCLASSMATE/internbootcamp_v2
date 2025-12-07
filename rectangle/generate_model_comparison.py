import os
import csv
import re
import matplotlib.pyplot as plt
import pandas as pd

OUTPUTS_DIR = "./outputs"
REPORT_DIR = "rectangle"

def parse_size(model_name):
    # Extract size in billions
    match = re.search(r'(\d+\.?\d*)B', model_name, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 0

def get_model_series(model_name):
    if "VL" in model_name:
        return "VL"
    if "DeepSeek" in model_name:
        return "DeepSeek"
    if "QwQ" in model_name:
        return "QwQ"
    if "Qwen2.5" in model_name:
        return "Qwen2.5"
    if "Qwen3" in model_name:
        return "Qwen3"
    return "Other"

def is_vl(model_name):
    return "VL" in model_name

def get_results():
    results = {} # Key: Model Name, Value: {Easy: score, Hard: score}
    
    # Walk through outputs directory
    for root, dirs, files in os.walk(OUTPUTS_DIR):
        # We only care about the immediate subdirectories of outputs
        if os.path.dirname(root) != OUTPUTS_DIR:
            continue
            
        model_name = os.path.basename(root)
        
        # Filter models based on user request
        # DeepSeek-R1, DeepSeek-V3, Qwen2.5 (no VL), Qwen3 (no VL), QwQ
        if model_name.startswith("DeepSeek-R1-") and "*" in model_name: # Skip ablation folders
            continue
        
        if is_vl(model_name):
            continue
            
        csv_files = [f for f in files if f.endswith('.csv')]
        csv_files.sort() # Sort by timestamp (filename)
        
        model_results = {}
        
        for csv_file in csv_files:
            file_path = os.path.join(root, csv_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                dataset_path = ""
                score = 0.0
                
                for line in lines:
                    if line.startswith("Dataset Path"):
                        parts = line.split(",")
                        if len(parts) > 1:
                            dataset_path = parts[1].strip()
                    if line.startswith("Overall Average Score"):
                        parts = line.split(",")
                        if len(parts) > 1:
                            score = float(parts[1].strip())
                
                difficulty = "Unknown"
                if "easy" in dataset_path.lower():
                    difficulty = "Easy"
                elif "hard" in dataset_path.lower():
                    difficulty = "Hard"
                
                if difficulty != "Unknown":
                    # Update with latest result (since we sorted files)
                    model_results[difficulty] = score
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        if model_results:
            results[model_name] = model_results

    return results

def generate_table(results):
    # Sort models: DeepSeek first, then QwQ, then Qwen2.5 (by size), then Qwen3 (by size)
    
    def sort_key(item):
        name = item[0]
        series = get_model_series(name)
        size = parse_size(name)
        
        series_order = {"DeepSeek": 0, "QwQ": 1, "Qwen2.5": 2, "Qwen3": 3, "Other": 4}
        return (series_order.get(series, 4), size)

    sorted_models = sorted(results.items(), key=sort_key)
    
    latex_content = r"""\begin{tabular}{lccc}
\toprule
\textbf{Model} & \textbf{Size} & \textbf{Easy Score} & \textbf{Hard Score} \\
\midrule
"""
    
    for model, scores in sorted_models:
        size = parse_size(model)
        size_str = f"{size}B" if size > 0 else "-"
        if "DeepSeek" in model:
             size_str = "-" # DeepSeek size might not be in name or irrelevant for this comparison style
        
        easy_score = scores.get("Easy", "-")
        hard_score = scores.get("Hard", "-")
        
        # Format scores
        easy_str = f"{easy_score:.4f}" if isinstance(easy_score, float) else "-"
        hard_str = f"{hard_score:.4f}" if isinstance(hard_score, float) else "-"
        
        model_escaped = model.replace('_', '\\_')
        latex_content += f"{model_escaped} & {size_str} & {easy_str} & {hard_str} \\\\\n"
        
    latex_content += r"""\bottomrule
\end{tabular}
"""
    
    with open(os.path.join(REPORT_DIR, "model_comparison_table.tex"), "w", encoding="utf-8") as f:
        f.write(latex_content)
    print("Table generated: model_comparison_table.tex")

def generate_charts(results):
    # Filter for Qwen2.5 and Qwen3
    data = []
    for model, scores in results.items():
        series = get_model_series(model)
        if series in ["Qwen2.5", "Qwen3"]:
            size = parse_size(model)
            if size > 0:
                data.append({
                    "Model": model,
                    "Series": series,
                    "Size": size,
                    "Easy": scores.get("Easy", None),
                    "Hard": scores.get("Hard", None)
                })
    
    df = pd.DataFrame(data)
    if df.empty:
        print("No data for charts")
        return

    df = df.sort_values("Size")
    
    # Set academic style settings
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.5
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12
    
    # Scientific colors
    # Muted Blue for Easy, Muted Red for Hard (Academic style)
    color_easy = '#1F4E79' 
    color_hard = '#C0504D'

    # Generate charts for each series separately
    for series in ["Qwen2.5", "Qwen3"]:
        series_df = df[df["Series"] == series]
        if series_df.empty:
            continue
            
        plt.figure(figsize=(8, 6))
        
        # Plot Easy
        subset_easy = series_df.dropna(subset=["Easy"])
        if not subset_easy.empty:
            plt.plot(subset_easy["Size"], subset_easy["Easy"], 
                     marker='o', linestyle='-', linewidth=2, markersize=8,
                     color=color_easy, label='Easy Difficulty')
            
        # Plot Hard
        subset_hard = series_df.dropna(subset=["Hard"])
        if not subset_hard.empty:
            plt.plot(subset_hard["Size"], subset_hard["Hard"], 
                     marker='s', linestyle='--', linewidth=2, markersize=8,
                     color=color_hard, label='Hard Difficulty')
            
        plt.title(f"{series} Performance Scaling", fontsize=16, fontweight='bold')
        plt.xlabel("Parameter Size (Billions)")
        plt.ylabel("Score")
        plt.legend(frameon=True, fancybox=False, edgecolor='black')
        
        # Save with high DPI for academic papers
        output_path = os.path.join(REPORT_DIR, f"{series.lower()}_performance_comparison.png")
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Chart generated: {output_path}")
    
    print("Charts generated.")

if __name__ == "__main__":
    results = get_results()
    generate_table(results)
    generate_charts(results)
