import os

def extract_record(content, record_num):
    start_marker = f"记录 #{record_num}"
    end_marker = f"记录 #{record_num + 1}"
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"Record #{record_num} not found")
        return None, None

    end_idx = content.find(end_marker)
    if end_idx == -1:
        # If next record not found, assume this record goes to the end or look for other markers
        record_content = content[start_idx:]
    else:
        record_content = content[start_idx:end_idx]

    # Extract Prompt
    prompt_start = record_content.find("【输入 PROMPT】")
    prompt_end = record_content.find("【模型 RESPONSE】")
    
    prompt_text = ""
    if prompt_start != -1 and prompt_end != -1:
        prompt_text = record_content[prompt_start:prompt_end].strip()
        # Remove the header line
        prompt_text = prompt_text.replace("【输入 PROMPT】", "").strip()
        prompt_text = prompt_text.replace("-" * 80, "").strip()
    else:
        prompt_text = "Prompt not found"

    # Extract Response
    response_start = prompt_end
    response_end = record_content.find("【评估结果】")
    
    response_text = ""
    if response_start != -1 and response_end != -1:
        response_text = record_content[response_start:response_end].strip()
        # Remove the header line
        response_text = response_text.replace("【模型 RESPONSE】", "").strip()
        response_text = response_text.replace("-" * 80, "").strip()
        
        # Replace literal \n with actual newlines if they exist as escaped characters
        # Also handle the JSON-like string representation if present
        if response_text.startswith('"') and response_text.endswith('"'):
             response_text = response_text[1:-1]
        
        response_text = response_text.replace("\\n", "\n").replace("\\boxed", "\\boxed")
        # Clean up some potential JSON escaping artifacts
        response_text = response_text.replace('\\"', '"')
    else:
        response_text = "Response not found"
        
    return prompt_text, response_text

def process_file():
    input_path = 'outputs/qwen2.5-vl-72B-inst.txt'
    output_dir = 'container'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Record 1
    p1, r1 = extract_record(content, 1)
    if p1 and r1:
        with open(os.path.join(output_dir, 'qwen2.5_vl_72b_prompt_1.txt'), 'w', encoding='utf-8') as f:
            f.write(p1)
        with open(os.path.join(output_dir, 'qwen2.5_vl_72b_response_1.txt'), 'w', encoding='utf-8') as f:
            f.write(r1)
        print("Extracted Record #1 to container/")

    # Extract Record 2
    p2, r2 = extract_record(content, 2)
    if p2 and r2:
        with open(os.path.join(output_dir, 'qwen2.5_vl_72b_prompt_2.txt'), 'w', encoding='utf-8') as f:
            f.write(p2)
        with open(os.path.join(output_dir, 'qwen2.5_vl_72b_response_2.txt'), 'w', encoding='utf-8') as f:
            f.write(r2)
        print("Extracted Record #2 to container/")

if __name__ == "__main__":
    process_file()
