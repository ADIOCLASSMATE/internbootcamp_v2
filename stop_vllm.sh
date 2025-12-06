#!/bin/bash

###############################################################################
# vLLM 服务器停止脚本 
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   停止 vLLM 服务器 (自动模式)${NC}"
echo -e "${BLUE}========================================${NC}"

# 1. 优先尝试通过 PID 文件停止
if [ -f "vllm_server.pid" ]; then
    PID=$(cat vllm_server.pid)
    
    # 检查进程是否存在
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "\n${YELLOW}正在停止 vLLM 服务器 (PID: $PID)...${NC}"
        kill $PID
        
        # 等待进程结束 (最多等待 20秒)
        WAIT_COUNT=0
        while ps -p $PID > /dev/null 2>&1 && [ $WAIT_COUNT -lt 20 ]; do
            echo -ne "\r${YELLOW}等待进程结束... ${WAIT_COUNT}s${NC}"
            sleep 1
            WAIT_COUNT=$((WAIT_COUNT + 1))
        done
        
        # 如果进程还在运行，强制终止
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "\n${RED}进程未响应，正在强制终止 (kill -9)...${NC}"
            kill -9 $PID
        fi
        
        echo -e "\n${GREEN}✅ vLLM 服务器已停止${NC}"
    else
        echo -e "\n${YELLOW}⚠️  PID $PID 对应的进程不存在，可能已经停止${NC}"
    fi
    # 无论是否找到进程，只要有 pid 文件就删除
    rm -f vllm_server.pid
else
    echo -e "\n${YELLOW}⚠️  未找到 PID 文件，尝试扫描系统进程...${NC}"
fi

# 2. 兜底清理：扫描并清理所有残留的 vllm serve 进程
# 注意：这会杀掉当前用户下所有含 "vllm serve" 的进程，确保不会影响他人
VLLM_PIDS=$(pgrep -f "vllm serve" 2>/dev/null)

if [ -n "$VLLM_PIDS" ]; then
    echo -e "${YELLOW}发现残留的 vLLM 进程，正在清理: $VLLM_PIDS${NC}"
    # 将换行符转换为空格并杀掉进程
    echo "$VLLM_PIDS" | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ 残留 vLLM 进程已清理${NC}"
else
    echo -e "${BLUE}ℹ️  系统无其他 vLLM 进程${NC}"
fi

# 3. 自动删除日志文件
if [ -f "vllm_server.log" ]; then
    rm -f vllm_server.log
    echo -e "${GREEN}✅ 日志文件 vllm_server.log 已自动删除${NC}"
fi

echo -e "\n${GREEN}完成！${NC}"