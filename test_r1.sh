cd /inspire/hdd/project/high-dimensionaldata/wanjiaxin-253108030048/internbootcamp_v2
source .venv/bin/activate

BASE_URL=public
MODEL=deepseek-ai/DeepSeek-R1
export NUM_GPUS=8
export PORT=8000

export MODEL_PATH=${BASE_URL}/${MODEL}
# 从路径名称提取模型名称(DeepSeek-R1)
export MODEL_NAME=$(basename ${MODEL})
bash deploy_vllm.sh
bash internbootcamp/bootcamps/rectangle_count/scripts/eval.sh