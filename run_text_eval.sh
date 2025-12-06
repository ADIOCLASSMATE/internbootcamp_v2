cd /inspire/hdd/project/high-dimensionaldata/wanjiaxin-253108030048/internbootcamp_v2
source .venv/bin/activate

# bash internbootcamp/bootcamps/rectangle_count/scripts/rectangle_count_generator.sh

BASE_URL=public
MODEL_LIST=(
    # "Qwen/Qwen3-0.6B"
    # "Qwen/Qwen3-1.7B"
    # "Qwen/Qwen3-4B"
    # "Qwen/Qwen3-8B"
    # "Qwen/Qwen3-14B"
    # "Qwen/Qwen3-32B"
    # "Qwen/Qwen3-235B-A22B-Instruct-2507"
    # "Qwen/Qwen3-235B-Thinking"
    # "Qwen/Qwen2.5-0.5B-Instruct"
    # "Qwen/Qwen2.5-1.5B-Instruct"
    # "Qwen/Qwen2.5-3B-Instruct"
    # "Qwen/Qwen2.5-7B-Instruct"
    # "Qwen/Qwen2.5-14B-Instruct"
    # "Qwen/Qwen2.5-32B-Instruct"
    # "Qwen/Qwen2.5-72B-Instruct"
    # "deepseek-ai/DeepSeek-V3"
    # "deepseek-ai/DeepSeek-V3.2-Speciale"
    "Qwen/QwQ-32B"
)
export NUM_GPUS=8
export PORT=8000

for MODEL in "${MODEL_LIST[@]}"; do
    export MODEL_PATH=${BASE_URL}/${MODEL}
    export PORT=8000
    # 从路径名称提取模型名称(DeepSeek-R1)
    export MODEL_NAME=$(basename ${MODEL})
    echo "Evaluating Model: ${MODEL_NAME}"

    bash deploy_vllm.sh

    bash internbootcamp/bootcamps/rectangle_count/scripts/eval.sh

    bash stop_vllm.sh
done