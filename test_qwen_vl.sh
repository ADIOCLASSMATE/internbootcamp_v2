cd /inspire/hdd/project/high-dimensionaldata/wanjiaxin-253108030048/internbootcamp_v2
source .venv/bin/activate

export API_KEY="uQ0hcpVo7qUCIwf4LJgPJqnnbEncQe5ACUWeuvSC6Uk="
export MODEL_NAME="Qwen/Qwen2.5-VL-7B-Instruct"
export MODEL_URL="https://q25-vl-7b-inst.openapi-qb-ai.sii.edu.cn/v1"
export NUM_GPUS=8
export PORT=8000

bash internbootcamp/bootcamps/container_with_most_water/scripts/eval.sh