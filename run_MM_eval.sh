cd /inspire/hdd/project/high-dimensionaldata/wanjiaxin-253108030048/internbootcamp_v2
source .venv/bin/activate

# bash internbootcamp/bootcamps/rectangle_count/scripts/rectangle_count_generator.sh

BASE_URL=public
MODEL_LIST=(
    "Qwen/Qwen2.5-VL-7B-Instruct"
    "Qwen/Qwen2.5-VL-32B-Instruct"
    "Qwen/Qwen2.5-VL-72B-Instruct"
    "Qwen/Qwen3-VL-8B-Instruct"
    "Qwen/Qwen3-VL-32B-Instruct"
    "Qwen/Qwen3-VL-235B-A22B-Instruct"
)
export NUM_GPUS=8
export PORT=8000

for MODEL in "${MODEL_LIST[@]}"; do
    export MODEL_PATH=${BASE_URL}/${MODEL}
    export API_URL="http://localhost:8000/v1"
    export API_KEY="null"
    # 从路径名称提取模型名称
    export MODEL_NAME=$(basename ${MODEL})
    echo "Evaluating Model: ${MODEL_NAME}"

    bash deploy_vllm.sh

    bash internbootcamp/bootcamps/container_with_most_water/scripts/eval.sh

    bash stop_vllm.sh
done