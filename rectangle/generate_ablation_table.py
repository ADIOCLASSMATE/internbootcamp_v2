import os
import csv
import glob

def parse_csv(file_path):
    data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract Dataset Path (Difficulty) and Overall Average Score
    for line in lines:
        if line.startswith("Dataset Path"):
            path = line.split(",")[1].strip()
            if "easy" in path:
                data['difficulty'] = "Easy"
            elif "hard" in path:
                data['difficulty'] = "Hard"
            else:
                data['difficulty'] = "Unknown"
        
        if line.startswith("Overall Average Score"):
            data['score'] = float(line.split(",")[1].strip())

    # Extract Avg Total Tokens
    # Find the line with "Data Source Summary Statistics"
    start_idx = -1
    for i, line in enumerate(lines):
        if "Data Source Summary Statistics" in line:
            start_idx = i
            break
    
    if start_idx != -1 and start_idx + 2 < len(lines):
        header = lines[start_idx + 1].strip().split(",")
        values = lines[start_idx + 2].strip().split(",")
        
        # Handle potential empty fields in CSV causing index mismatch if splitting by comma blindly
        # But looking at the file content, it seems standard CSV.
        # "Data Source,Total Samples,,Success Count,..."
        # Note the double comma in header "Total Samples,,Success Count"
        
        try:
            # Find index of "Avg Total Tokens"
            token_idx = -1
            for idx, h in enumerate(header):
                if "Avg Total Tokens" in h:
                    token_idx = idx
                    break
            
            if token_idx != -1:
                data['tokens'] = float(values[token_idx])
        except Exception as e:
            print(f"Error parsing tokens in {file_path}: {e}")
            data['tokens'] = 0.0

    return data

def generate_latex_table():
    base_dir = "../outputs"
    grid_sizes = ["20*20", "40*40", "60*60", "80*80"]
    
    results = []

    for size in grid_sizes:
        dir_path = os.path.join(base_dir, f"DeepSeek-R1-{size}")
        if not os.path.exists(dir_path):
            print(f"Directory not found: {dir_path}")
            continue
            
        csv_files = glob.glob(os.path.join(dir_path, "*.csv"))
        
        for csv_file in csv_files:
            file_data = parse_csv(csv_file)
            if 'difficulty' in file_data and 'score' in file_data:
                results.append({
                    'grid_size': size,
                    'difficulty': file_data['difficulty'],
                    'score': file_data['score'],
                    'tokens': file_data.get('tokens', 0.0)
                })

    # Sort results: Grid Size (numerical order of first dim), then Difficulty
    # 20*20 -> 20
    results.sort(key=lambda x: (int(x['grid_size'].split('*')[0]), x['difficulty']))

    latex_code = []
    latex_code.append("\\begin{table}[htbp]")
    latex_code.append("    \\centering")
    latex_code.append("    \\caption{DeepSeek-R1 Ablation Study Results}")
    latex_code.append("    \\label{tab:deepseek-ablation}")
    latex_code.append("    \\begin{tabular}{lccc}")
    latex_code.append("    \\toprule")
    latex_code.append("    Grid Size & Difficulty & Average Score & Avg Total Tokens \\\\")
    latex_code.append("    \\midrule")
    
    for row in results:
        latex_code.append(f"    {row['grid_size']} & {row['difficulty']} & {row['score']:.4f} & {row['tokens']:.2f} \\\\")
        
    latex_code.append("    \\bottomrule")
    latex_code.append("    \\end{tabular}")
    latex_code.append("\\end{table}")
    
    with open("ablation_table.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(latex_code))
    
    print("LaTeX table generated in report1/ablation_table.tex")

if __name__ == "__main__":
    # Change working directory to report1 so relative paths work as expected if run from there
    # But the script assumes it's in report1 and outputs are in ../outputs
    # Let's ensure we are in the right place or handle paths correctly.
    # The user is in /Users/wjx/博士/作业/MM
    # So if I run this script from there, I need to adjust paths.
    
    # Adjusting paths to be absolute or relative to workspace root
    workspace_root = "/Users/wjx/博士/作业/MM"
    output_dir = os.path.join(workspace_root, "outputs")
    report_dir = os.path.join(workspace_root, "rectangle")
    
    # Redefine function to use absolute paths
    def generate_latex_table_abs():
        grid_sizes = ["20*20", "40*40", "60*60", "80*80"]
        results = []

        for size in grid_sizes:
            dir_path = os.path.join(output_dir, f"DeepSeek-R1-{size}")
            if not os.path.exists(dir_path):
                print(f"Directory not found: {dir_path}")
                continue
                
            csv_files = glob.glob(os.path.join(dir_path, "*.csv"))
            
            for csv_file in csv_files:
                file_data = parse_csv(csv_file)
                if 'difficulty' in file_data and 'score' in file_data:
                    results.append({
                        'grid_size': size,
                        'difficulty': file_data['difficulty'],
                        'score': file_data['score'],
                        'tokens': file_data.get('tokens', 0.0)
                    })

        results.sort(key=lambda x: (int(x['grid_size'].split('*')[0]), x['difficulty']))

        latex_code = []
        # latex_code.append("\\begin{table}[htbp]") # User asked for just the table code to be input, usually \input includes the content. 
        # But the user's example showed \input{mytable.tex} inside a table environment in the main file.
        # Wait, the user said: "latex中在表格处只需要写：\begin{table} ... \input{mytable.tex} \end{table}".
        # So the input file should probably ONLY contain the tabular environment or the content of the table?
        # Let's look at the user's request again: "把每个网格大小的每个难度的score与平均token数绘制成一个tex表格代码"
        # And "希望能够读取python代码生成的.tex"。
        # Usually \input inserts the content directly. If the main file has \begin{table}, the input should have \begin{tabular}.
        # Let's check the main file again.
        # The main file has:
        # \begin{figure}[H]
        #     \centering
        #     \includegraphics[width=0.95\textwidth]{evaluation_results.png}
        #     \caption{DeepSeek-R1 模型在不同网格大小下的消融实验结果}
        #     \label{fig:deep-r1-ablation}
        # \end{figure}
        # The user wants to REPLACE this image with the table.
        # So I should generate the full table environment or just the tabular?
        # If I generate the full table environment, I can just \input it.
        # Let's generate the tabular part mostly, but maybe wrapped in table if it replaces the figure.
        # Actually, a table is better suited for this data than a figure.
        
        latex_code = []
        # Use booktabs style with grouping for better academic look
        latex_code.append("\\begin{tabular}{llcc}")
        latex_code.append("\\toprule")
        latex_code.append("\\textbf{Grid Size} & \\textbf{Difficulty} & \\textbf{Avg. Score} & \\textbf{Avg. Tokens} \\\\")
        latex_code.append("\\midrule")
        
        current_grid_size = None
        for row in results:
            grid_size = row['grid_size']
            difficulty = row['difficulty']
            score = row['score']
            tokens = row['tokens']
            
            if grid_size != current_grid_size:
                if current_grid_size is not None:
                    latex_code.append("\\addlinespace")
                display_grid_size = grid_size
                current_grid_size = grid_size
            else:
                display_grid_size = ""
                
            latex_code.append(f"{display_grid_size} & {difficulty} & {score:.4f} & {tokens:.2f} \\\\")
            
        latex_code.append("\\bottomrule")
        latex_code.append("\\end{tabular}")
        
        output_file = os.path.join(report_dir, "ablation_table.tex")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(latex_code))
        
        print(f"LaTeX table generated in {output_file}")

    generate_latex_table_abs()
