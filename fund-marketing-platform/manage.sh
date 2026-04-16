#!/bin/bash
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'
PD="$(dirname "$(realpath "$0")")"
PORT=5002

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
ok() { echo -e "${GREEN}[OK]${NC} $1"; }

case "$1" in
    start)
        log "启动服务..."
        cd "$PD/backend"
        source ../venv/bin/activate 2>/dev/null || true
        python3 app.py &
        sleep 2
        if curl -s http://localhost:$PORT/api/health > /dev/null; then
            ok "服务已启动!"
            echo -e "前端: ${BLUE}http://localhost:$PORT/${NC}"
        fi
        ;;
    stop)
        log "停止服务..."
        pkill -f "python.*app.py" 2>/dev/null
        ok "服务已停止"
        ;;
    test)
        log "测试API..."
        curl -s http://localhost:$PORT/api/health | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'✅ {d}')" 2>/dev/null || echo "❌ 服务未运行"
        ;;
    *) echo "用法: $0 {start|stop|test}";;
esac
