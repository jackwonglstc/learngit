#!/bin/bash

# 脚本功能：卸载 acme.sh 及其相关文件、证书和 cron 作业
# 系统要求：Ubuntu 22.04
# 作者：Grok，生成于 2025-07-08

# 检查是否以 root 权限运行
if [ "$(id -u)" != "0" ]; then
    echo "错误：请以 root 权限运行此脚本！"
    echo "使用：sudo bash $0"
    exit 1
fi

# 读取配置日志文件
CONFIG_LOG="/root/acme_install_config.log"
if [ ! -f "$CONFIG_LOG" ]; then
    echo "警告：未找到配置日志文件 $CONFIG_LOG，尝试直接清理默认路径..."
    CERT_DIR="/etc/letsencrypt"
    ACME_DIR="$HOME/.acme.sh"
else
    CERT_DIR=$(grep "证书目录" "$CONFIG_LOG" | cut -d "：" -f 2)
    ACME_DIR=$(grep "acme.sh 安装目录" "$CONFIG_LOG" | cut -d "：" -f 2)
fi

# 停止并移除 acme.sh cron 作业
echo "移除自动续期 cron 作业..."
crontab -l 2>/dev/null | grep -v "acme.sh --cron" | crontab -
if [ $? -eq 0 ]; then
    echo "cron 作业已移除。"
else
    echo "警告：移除 cron 作业失败，可能不存在。"
fi

# 撤销所有证书（如果存在）
if [ -d "$ACME_DIR" ]; then
    echo "撤销所有证书..."
    "$ACME_DIR/acme.sh" --revoke-all
fi

# 删除 acme.sh 及其配置文件
if [ -d "$ACME_DIR" ]; then
    echo "删除 acme.sh 目录：$ACME_DIR..."
    rm -rf "$ACME_DIR"
    echo "移除 acme.sh 别名..."
    sed -i '/alias acme.sh=/d' ~/.bashrc
    source ~/.bashrc
fi

# 删除证书文件
if [ -d "$CERT_DIR" ]; then
    echo "删除证书目录：$CERT_DIR..."
    rm -rf "$CERT_DIR"
fi

# 删除配置日志文件
if [ -f "$CONFIG_LOG" ]; then
    echo "删除配置日志：$CONFIG_LOG..."
    rm -f "$CONFIG_LOG"
fi

# 提示完成
echo "卸载完成！"
echo "已清理："
echo "- acme.sh 及其配置文件"
echo "- 证书文件"
echo "- 自动续期 cron 作业"
echo "- 配置日志"
echo "请检查 Web 服务器配置，确保已移除对已删除证书的引用。"