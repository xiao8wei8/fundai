#!/bin/bash

# 日志轮转
find /var/log -name "fund-marketing-platform*.log" -type f -exec truncate -s 0 {} 

# 清理缓存
rm -rf /opt/fund-marketing-platform/backend/__pycache__/

# 重启服务
supervisorctl restart fund-marketing-platform

echo "Maintenance completed at $(date)"
