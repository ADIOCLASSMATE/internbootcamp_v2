python -m internbootcamp.utils.run_evaluation \
  --dataset-path internbootcamp/bootcamps/NP_MM/data/TSP_20251118152919_train.jsonl \
  --output-dir outputs/ \
  --api-key "null" \
  --api-url "http://localhost:8000/v1" \
  --api-model "public/Qwen/Qwen3-VL-8B-Instruct" \
  --reward-calculator-class "internbootcamp.bootcamps.NP_MM.GCP_D.reward_calculator.NpGcpDRewardCalculator" 