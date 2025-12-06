#!/bin/bash

###############################################################################
# vLLM API 测试脚本
# 测试 vLLM 服务器是否正常工作，使用与 NP_MM 相同的 API 调用方式
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 默认配置
API_URL="${API_URL:-http://localhost:8000/v1}"
API_KEY="${API_KEY:-EMPTY}"
API_MODEL="${API_MODEL:-public/deepseek-ai/DeepSeek-R1}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   vLLM API 测试脚本${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${GREEN}配置信息:${NC}"
echo -e "  API URL:  ${YELLOW}$API_URL${NC}"
echo -e "  API Key:  ${YELLOW}$API_KEY${NC}"
echo -e "  Model:    ${YELLOW}$API_MODEL${NC}"

# 1. 测试服务器连接
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}测试 1: 服务器连接${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if curl -s "${API_URL}/models" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 服务器连接成功${NC}"
else
    echo -e "${RED}❌ 服务器连接失败${NC}"
    echo -e "${YELLOW}请确保 vLLM 服务器正在运行${NC}"
    echo -e "${YELLOW}运行: bash scripts/deploy_vllm.sh${NC}"
    exit 1
fi

# 2. 获取模型列表
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}测试 2: 获取模型列表${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

MODELS_RESPONSE=$(curl -s "${API_URL}/models")
echo "$MODELS_RESPONSE" | python3 -m json.tool
echo -e "${GREEN}✅ 模型列表获取成功${NC}"

# 3. 测试简单文本对话 (与 NP_MM 相同的格式)
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}测试 3: 简单对话 (纯文本)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

CHAT_PAYLOAD=$(cat <<EOF
{
  "model": "$API_MODEL",
  "messages": [
    {
      "role": "user",
      "content": "你好！请用一句话介绍你自己。"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 512
}
EOF
)

echo -e "${YELLOW}发送请求:${NC}"
echo "$CHAT_PAYLOAD" | python3 -m json.tool

CHAT_RESPONSE=$(curl -s "${API_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "$CHAT_PAYLOAD")

echo -e "\n${YELLOW}响应:${NC}"
echo "$CHAT_RESPONSE" | python3 -m json.tool

# 提取回复内容
REPLY=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['choices'][0]['message']['content'])" 2>/dev/null)

if [ -n "$REPLY" ]; then
    echo -e "\n${GREEN}✅ 对话测试成功${NC}"
    echo -e "${BLUE}模型回复: ${NC}${YELLOW}$REPLY${NC}"
else
    echo -e "\n${RED}❌ 对话测试失败${NC}"
    exit 1
fi

# 4. 测试数学问题 (模拟 Rectangle Count 任务)
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}测试 4: 数学推理 (模拟 Rectangle Count)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

MATH_PAYLOAD=$(cat <<'EOF'
{
  "model": "$API_MODEL",
  "messages": [
    {
      "role": "user",
      "content": "请数一下这个 ASCII 网格中有多少个矩形：\n\n    ######\n    #    #\n    #    #\n    ######\n\n    ########\n    #      #\n    #      #\n    ########\n\n请直接回答数字，格式为: Answer: <数字>"
    }
  ],
  "temperature": 0.0,
  "max_tokens": 256
}
EOF
)

MATH_PAYLOAD=$(echo "$MATH_PAYLOAD" | sed "s#\$API_MODEL#$API_MODEL#g")

echo -e "${YELLOW}发送数学推理请求...${NC}"

MATH_RESPONSE=$(curl -s "${API_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "$MATH_PAYLOAD")

MATH_REPLY=$(echo "$MATH_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['choices'][0]['message']['content'])" 2>/dev/null)

if [ -n "$MATH_REPLY" ]; then
    echo -e "\n${GREEN}✅ 数学推理测试成功${NC}"
    echo -e "${BLUE}模型回复:${NC}\n${YELLOW}$MATH_REPLY${NC}"
else
    echo -e "\n${RED}❌ 数学推理测试失败${NC}"
fi

# 5. 测试多轮对话
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}测试 5: 多轮对话${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

MULTITURN_PAYLOAD=$(cat <<EOF
{
  "model": "$API_MODEL",
  "messages": [
    {
      "role": "user",
      "content": "请记住这个数字: 42"
    },
    {
      "role": "assistant",
      "content": "好的，我记住了数字 42。"
    },
    {
      "role": "user",
      "content": "我刚才让你记住的数字是多少？"
    }
  ],
  "temperature": 0.0,
  "max_tokens": 128
}
EOF
)

echo -e "${YELLOW}发送多轮对话请求...${NC}"

MULTITURN_RESPONSE=$(curl -s "${API_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "$MULTITURN_PAYLOAD")

MULTITURN_REPLY=$(echo "$MULTITURN_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['choices'][0]['message']['content'])" 2>/dev/null)

if [ -n "$MULTITURN_REPLY" ]; then
    echo -e "\n${GREEN}✅ 多轮对话测试成功${NC}"
    echo -e "${BLUE}模型回复:${NC} ${YELLOW}$MULTITURN_REPLY${NC}"
else
    echo -e "\n${RED}❌ 多轮对话测试失败${NC}"
fi

# 6. 测试 token 统计
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}测试 6: Token 使用统计${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

USAGE=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); usage = data.get('usage', {}); print(f\"Prompt: {usage.get('prompt_tokens', 0)}, Completion: {usage.get('completion_tokens', 0)}, Total: {usage.get('total_tokens', 0)}\")" 2>/dev/null)

if [ -n "$USAGE" ]; then
    echo -e "${GREEN}✅ Token 统计:${NC} ${YELLOW}$USAGE${NC}"
else
    echo -e "${YELLOW}⚠️  无法获取 token 统计信息${NC}"
fi

# 最终总结
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 所有测试完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${BLUE}下一步:${NC}"
echo -e "  1. 设置环境变量:"
echo -e "     ${YELLOW}export API_KEY='EMPTY'${NC}"
echo -e "     ${YELLOW}export API_URL='$API_URL'${NC}"
echo -e "     ${YELLOW}export API_MODEL='$API_MODEL'${NC}"
echo -e "\n  2. 运行完整评测:"
echo -e "     ${YELLOW}bash scripts/eval_qwen3vl.sh${NC}"

echo -e "\n${BLUE}API 使用示例 (Python):${NC}"
cat << 'PYEOF'
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

response = client.chat.completions.create(
    model="Qwen2-VL-7B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
PYEOF
