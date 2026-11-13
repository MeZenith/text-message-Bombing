#!/usr/bin/env bash
# text-message-Bombing 一键部署脚本（Linux）
#
# 在服务器上跑：
#     sudo bash deploy/deploy.sh
#
# 想改参数就用环境变量，例如：
#     sudo APP_DIR=/srv/sms APP_USER=www-data DOMAIN=sms.example.com bash deploy/deploy.sh
#     sudo SRC_DIR=/tmp/text-message-Bombing bash deploy/deploy.sh     # 用已经上传到服务器的代码
#
# 脚本是幂等的：重复跑不会出问题，只会更新代码、重装依赖、重启服务。

set -euo pipefail

# ----------------------------- 可改的参数 -----------------------------
APP_DIR="${APP_DIR:-/opt/text-message-Bombing}"      # 装到哪个目录
APP_USER="${APP_USER:-}"                             # 跑服务的系统用户，留空自动判断
APP_PORT="${APP_PORT:-5000}"                         # 应用监听端口（只在本机）
DOMAIN="${DOMAIN:-}"                                 # 域名，留空就不配 nginx
REPO="${REPO:-git@github.com:MeZenith/text-message-Bombing.git}"
SRC_DIR="${SRC_DIR:-}"                               # 已经上传到服务器的代码目录
SERVICE_NAME="text-message-bombing"

# ----------------------------- 小工具 -----------------------------
log()  { printf '\033[36m[*]\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m[+]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[!]\033[0m %s\n' "$*"; }
die()  { printf '\033[31m[-]\033[0m %s\n' "$*" >&2; exit 1; }

# ----------------------------- 0. 检查环境 -----------------------------
[ "$(id -u)" -eq 0 ] || die "请用 root 跑：sudo bash deploy/deploy.sh"
command -v systemctl >/dev/null 2>&1 || die "没有 systemd，这个脚本跑不了（容器里请手动 gunicorn）"

if command -v apt-get >/dev/null 2>&1; then
    PKG="apt-get"
    DEFAULT_USER="www-data"
elif command -v dnf >/dev/null 2>&1; then
    PKG="dnf"
    DEFAULT_USER="nginx"
elif command -v yum >/dev/null 2>&1; then
    PKG="yum"
    DEFAULT_USER="nginx"
else
    die "认不出系统类型（没有 apt-get / dnf / yum）"
fi

APP_USER="${APP_USER:-$DEFAULT_USER}"

log "系统包管理器：$PKG"
log "安装目录：$APP_DIR"
log "运行用户：$APP_USER"
log "应用端口：$APP_PORT"

# ----------------------------- 1. 装系统依赖 -----------------------------
log "安装系统依赖（python3、venv、git、nginx）"
if [ "$PKG" = "apt-get" ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq python3 python3-venv python3-pip git nginx curl >/dev/null
else
    $PKG install -y -q python3 python3-pip git nginx curl >/dev/null
    # RHEL 系的 python3 自带 venv
fi
ok "系统依赖就绪"

# ----------------------------- 2. 放代码 -----------------------------
if [ -n "$SRC_DIR" ]; then
    log "从本地目录复制代码：$SRC_DIR"
    mkdir -p "$APP_DIR"
    tar -C "$SRC_DIR" \
        --exclude=.git --exclude=__pycache__ --exclude=.venv --exclude=.ruff_cache \
        -cf - . | tar -C "$APP_DIR" -xf -
elif [ -d "$APP_DIR/.git" ]; then
    log "目录已存在，拉取最新代码"
    git -C "$APP_DIR" pull --ff-only || warn "git pull 失败，继续用现有代码"
else
    log "克隆仓库：$REPO"
    git clone "$REPO" "$APP_DIR"
fi

[ -f "$APP_DIR/main.py" ] || die "$APP_DIR 里没找到 main.py，代码没放对"
ok "代码就位：$(git -C "$APP_DIR" log --oneline -1 2>/dev/null || echo '（非 git 目录）')"

# ----------------------------- 3. Python 虚拟环境 -----------------------------
log "创建虚拟环境并安装依赖"
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -q --upgrade pip
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/deploy/requirements-server.txt"
ok "依赖装好了：$("$APP_DIR/.venv/bin/python" -V)"

# ----------------------------- 4. systemd 服务 -----------------------------
log "写入 systemd 服务：/etc/systemd/system/$SERVICE_NAME.service"
sed -e "s|__APP_USER__|$APP_USER|g" \
    -e "s|__APP_DIR__|$APP_DIR|g" \
    "$APP_DIR/deploy/$SERVICE_NAME.service" > "/etc/systemd/system/$SERVICE_NAME.service"

chown -R "$APP_USER:$APP_USER" "$APP_DIR"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME" >/dev/null 2>&1
systemctl restart "$SERVICE_NAME"

sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    ok "服务已启动（systemctl status $SERVICE_NAME 看状态）"
else
    die "服务没起来，看日志：journalctl -u $SERVICE_NAME -n 50 --no-pager"
fi

# ----------------------------- 5. 自检 -----------------------------
log "本机自检 http://127.0.0.1:$APP_PORT/healthz"
for i in 1 2 3 4 5; do
    if curl -fsS --max-time 3 "http://127.0.0.1:$APP_PORT/healthz" >/dev/null 2>&1; then
        ok "自检通过：$(curl -fsS "http://127.0.0.1:$APP_PORT/healthz")"
        break
    fi
    [ "$i" = "5" ] && die "自检失败，服务在跑但 5000 端口没响应，看 journalctl -u $SERVICE_NAME"
    sleep 1
done

# ----------------------------- 6. nginx 反向代理 -----------------------------
if [ -n "$DOMAIN" ]; then
    log "配置 nginx 反向代理：$DOMAIN"

    NGINX_CONF="$(sed -e "s|__DOMAIN__|$DOMAIN|g" -e "s|__APP_DIR__|$APP_DIR|g" \
        "$APP_DIR/deploy/nginx.conf.example")"

    if [ -d /etc/nginx/sites-available ]; then
        # Debian / Ubuntu
        printf '%s\n' "$NGINX_CONF" > /etc/nginx/sites-available/"$SERVICE_NAME"
        ln -sf /etc/nginx/sites-available/"$SERVICE_NAME" /etc/nginx/sites-enabled/"$SERVICE_NAME"
        rm -f /etc/nginx/sites-enabled/default
    else
        # RHEL / CentOS / Rocky
        printf '%s\n' "$NGINX_CONF" > /etc/nginx/conf.d/"$SERVICE_NAME".conf
    fi

    nginx -t >/dev/null 2>&1 || die "nginx 配置有错，检查 /etc/nginx 下生成的 $SERVICE_NAME 配置"
    systemctl enable nginx >/dev/null 2>&1 || true
    systemctl reload nginx
    ok "nginx 已生效"
fi

# ----------------------------- 7. 防火墙提示 -----------------------------
if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
    ufw allow 80/tcp >/dev/null 2>&1 || true
    ufw allow 443/tcp >/dev/null 2>&1 || true
    warn "已尝试放行 ufw 的 80/443"
fi

# ----------------------------- 收尾 -----------------------------
printf '\n'
ok "部署完成"
if [ -n "$DOMAIN" ]; then
    printf '    访问地址：http://%s\n' "$DOMAIN"
    printf '    上 HTTPS：apt install -y certbot python3-certbot-nginx && certbot --nginx -d %s\n' "$DOMAIN"
else
    warn "没配 nginx（没设 DOMAIN），只能用 SSH 隧道访问："
    printf '    在你自己的电脑上执行：ssh -L %s:127.0.0.1:%s root@<服务器IP>\n' "$APP_PORT" "$APP_PORT"
    printf '    然后浏览器打开：http://127.0.0.1:%s\n' "$APP_PORT"
    printf '    想直接开公网：sudo DOMAIN=<你的域名或IP> bash deploy/deploy.sh\n'
fi
printf '    看日志：journalctl -u %s -f\n' "$SERVICE_NAME"
printf '    改配置：%s/settings.py，改完 systemctl restart %s\n' "$APP_DIR" "$SERVICE_NAME"
printf '\n'
