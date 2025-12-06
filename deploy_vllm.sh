cd /inspire/hdd/project/high-dimensionaldata/wanjiaxin-253108030048/internbootcamp_v2
export HF_HUB_OFFLINE=1

# ==========================================
# 1. 自动计算 GPU 数量 (TP Size)
# ==========================================
# 逻辑：0.5B 模型只有 14 个 Head，无法被 8 整除，但可以被 2 整除。
# 其他模型默认使用 8 卡。

if echo "$MODEL_NAME" | grep -iE "0.5B|1.5B|7B"; then
    echo "⚠️  检测到小参数模型 (0.5B/1.5B): ${MODEL_NAME}"
    echo "🔧  强制设置 NUM_GPUS=2 (适配 Attention Heads 整除需求)"
    export NUM_GPUS=2
else
    # 如果外部没有强制指定，且不是小模型，则默认为 8
    export NUM_GPUS=${NUM_GPUS:-8}
    echo "⚡ 使用标准配置: NUM_GPUS=${NUM_GPUS}"
fi


# ==========================================
# 2. 模型特定参数配置
# ==========================================

# 初始化额外参数为空字符串
EXTRA_VLLM_ARGS=""

# --- A. DeepSeek 系列检测 ---
# 使用 grep -i (忽略大小写) 检测 MODEL_NAME 是否包含 "deepseek"
if echo "$MODEL_NAME" | grep -iq "DeepSeek"; then
    echo "=================================================="
    echo "🚀 检测到 DeepSeek 系列模型: ${MODEL_NAME}"
    echo "⚡ 已启用 DeepGEMM 和 DeepEP 优化 (适用于 H800/H100)"
    
    # 导出 DeepSeek 专属环境变量
    export VLLM_USE_DEEP_GEMM=1 
    export VLLM_ALL2ALL_BACKEND="deepep_high_throughput"
    SEQ_LEN=40960
    
    # 基础 DeepSeek 启动参数 (MoE 优化)
    EXTRA_VLLM_ARGS="--enable-expert-parallel --safetensors-load-strategy eager"

    # R1 特殊处理：思维链解析器
    if echo "$MODEL_NAME" | grep -iq "R1"; then
        echo "🧠 检测到 R1 推理模型，已启用 --reasoning-parser deepseek_r1"
        EXTRA_VLLM_ARGS="${EXTRA_VLLM_ARGS} --reasoning-parser deepseek_r1"
    else
        echo "💬 检测到 V3 或其他对话模型，无需 reasoning-parser"
    fi
    echo "=================================================="

# --- B. Qwen / VL / Llama 等通用模型检测 ---
else
    echo "=================================================="
    echo "🤖 检测到通用模型 (非 DeepSeek): ${MODEL_NAME}"
    echo "🛡️ 已禁用 DeepGEMM/DeepEP，使用标准 vLLM 配置"

    # 清除 DeepSeek 环境变量
    unset VLLM_USE_DEEP_GEMM
    unset VLLM_ALL2ALL_BACKEND

    # 1. 上下文长度与 VL 适配逻辑
    if echo "$MODEL_NAME" | grep -iq "VL"; then
        echo "👁️  检测到 Vision-Language (VL) 模型"
        echo "🖼️  已适配多模态输入处理"
        # Qwen2.5-VL 属于 2.5 系列，将在下面设置为 32k
        # VL 模型建议不要设置过大的 batch size，但在 boot camp 场景下默认即可
    fi

    if echo "$MODEL_NAME" | grep -iq "2.5"; then
        # Qwen2.5 和 Qwen2.5-VL 推荐 32k 以内以保证显存安全
        SEQ_LEN=32768
        echo "📏 设置 Max Model Len: $SEQ_LEN (适配 Qwen2.5/VL)"
    else
        # 其他模型默认 40k (如果显存足够)
        SEQ_LEN=40960
    fi

    echo "=================================================="
    EXTRA_VLLM_ARGS=""
fi

# ==========================================
# 3. 启动 vLLM 服务
# ==========================================

echo "启动参数准备完毕："
echo "   Model: $MODEL_NAME"
echo "   GPUs : $NUM_GPUS"
echo "   Len  : $SEQ_LEN"

# 注意: Qwen2.5-VL 等模型必须开启 --trust-remote-code
nohup uv run vllm serve ${MODEL_PATH} \
  --port ${PORT} \
  --trust-remote-code \
  --tensor-parallel-size ${NUM_GPUS} \
  --gpu-memory-utilization=0.9 \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --max-model-len=$SEQ_LEN \
  --served-model-name ${MODEL_NAME} \
  ${EXTRA_VLLM_ARGS} > vllm_${MODEL_NAME}.log 2>&1 &

# 保存进程ID
echo $! > vllm_server.pid

echo "vLLM 服务已启动, PID: $(cat vllm_server.pid)"
echo "日志文件: vllm_${MODEL_NAME}.log"

# ==========================================
# 4. 健康检查
# ==========================================
echo "等待 vLLM 服务启动..."
max_wait=300000  # 最多等待5分钟
waited=0
while [ $waited -lt $max_wait ]; do
    if curl -s http://localhost:${PORT}/v1/models > /dev/null 2>&1; then
        echo "✅ vLLM 服务已就绪!"
        break
    fi
    sleep 5
    waited=$((waited + 5))
    echo "已等待 ${waited} 秒..."
done

if [ $waited -ge $max_wait ]; then
    echo "❌ 警告: vLLM 服务启动超时，请检查日志 vllm_${MODEL_NAME}.log"
    # 不要 exit 1，以免打断外层循环的后续模型测试，但可以打印显眼的错误
    echo "⚠️  跳过当前模型评测..."
    exit 1
fi