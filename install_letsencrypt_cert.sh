#!/bin/bash

# 脚本功能：使用 acme.sh 申请 Let's Encrypt 证书，设置自动更新
# 系统要求：Ubuntu 22.04
# 作者：Grok，生成于 2025-07-08

# 检查是否以 root 权限运行
if [ "$(id -u)" != "0" ]; then
    echo "错误：请以 root 权限运行此脚本！"
    echo "使用：sudo bash $0"
    exit 1
fi

# 检查依赖
for cmd in curl git; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "安装依赖：$cmd"
        apt-get update && apt-get install -y "$cmd"
    fi
done

# 检查端口 80 是否被占用
if lsof -i :80 > /dev/null 2>&1; then
    echo "错误：端口 80 已被占用！"
    exit 1
fi

# 提示输入域名
read -p "请输入要申请证书的域名（例如 example.com）：" DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "错误：域名不能为空！"
    exit 1
fi

# 提示输入证书安装目录
read -p "请输入证书安装目录（默认 /etc/letsencrypt）：" CERT_DIR
CERT_DIR=${CERT_DIR:-/etc/letsencrypt}
if [ ! -d "$CERT_DIR" ]; then
    echo "创建证书目录：$CERT_DIR"
    mkdir -p "$CERT_DIR"
fi

# 提示输入通知邮箱
read -p "请输入用于接收续期通知的邮箱（可选）：" EMAIL

# 下载并安装 acme.sh
if [ ! -d "$HOME/.acme.sh" ]; then
    echo "安装 acme.sh..."
    curl https://get.acme.sh | sh -s email="$EMAIL"
    if [ $? -ne 0 ]; then
        echo "错误：acme.sh 安装失败！"
        exit 1
    fi
fi

# 确保 acme.sh 命令可用
source ~/.bashrc
if ! command -v acme.sh &> /dev/null; then
    echo "错误：acme.sh 命令不可用！"
    exit 1
fi

# 设置 Let's Encrypt 为默认 CA
echo "切换到 Let's Encrypt..."
acme.sh --set-default-ca --server letsencrypt

# 申请证书（standalone 模式）
echo "申请证书：$DOMAIN..."
acme.sh --issue --standalone -d "$DOMAIN" -d "www.$DOMAIN" \
    --cert-file "$CERT_DIR/cert.pem" \
    --key-file "$CERT_DIR/privkey.pem" \
    --fullchain-file "$CERT_DIR/fullchain.pem" \
    --reloadcmd "systemctl reload apache2 || systemctl reload nginx || true"
if [ $? -ne 0 ]; then
    echo "错误：证书申请失败！请检查域名解析或网络连接。"
    exit 1
fi

# 确保证书文件权限安全
chmod 600 "$CERT_DIR"/*.pem

# 检查自动续期 cron 作业
if ! crontab -l 2>/dev/null | grep -q "acme.sh --cron"; then
    echo "设置自动续期 cron 作业..."
    acme.sh --install-cronjob
fi

# 保存配置信息到日志文件
CONFIG_LOG="/root/acme_install_config.log"
echo "域名：$DOMAIN" > "$CONFIG_LOG"
echo "证书目录：$CERT_DIR" >> "$CONFIG_LOG"
echo "邮箱：${EMAIL:-未设置}" >> "$CONFIG_LOG"
echo "acme.sh 安装目录：$HOME/.acme.sh" >> "$CONFIG_LOG"

# 提示完成
echo "证书申请成功！"
echo "证书已安装到：$CERT_DIR"
echo "自动续期已启用，每 60 天检查一次。"
echo "配置信息已保存到：$CONFIG_LOG"
echo "请配置 Web 服务器（Apache/Nginx）使用这些证书。"
echo "示例 Nginx 配置："
echo "  ssl_certificate $CERT_DIR/fullchain.pem;"
echo "  ssl_certificate_key $CERT_DIR/privkey.pem;"