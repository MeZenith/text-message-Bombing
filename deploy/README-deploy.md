# 部署到服务器

两种方式，挑一种。脚本都在 `deploy/` 目录里，是幂等的，重复跑只会更新代码和重启服务。

## 方式一：在服务器上跑（推荐）

SSH 登录服务器，然后：

```bash
git clone git@github.com:MeZenith/text-message-Bombing.git
cd text-message-Bombing
sudo bash deploy/deploy.sh
```

没配域名、只用 IP 访问：

```bash
sudo DOMAIN=<你的域名或IP> bash deploy/deploy.sh
```

想换目录 / 换用户：

```bash
sudo APP_DIR=/srv/sms APP_USER=www-data DOMAIN=sms.example.com bash deploy/deploy.sh
```

脚本会自动做完这些：

1. `apt` / `dnf` 装 python3、venv、git、nginx
2. 把代码放到 `/opt/text-message-Bombing`（已有就 `git pull`）
3. 建 `.venv` 装依赖
4. 写 systemd 服务、开机自启、启动
5. 自检 `http://127.0.0.1:5000/healthz`
6. `DOMAIN` 有值才配 nginx 反代（80 端口）
7. 顺便尝试放行 ufw 的 80/443

## 方式二：从 Windows 打包上传（服务器上不用能访问 GitHub）

在项目根目录：

```powershell
powershell -ExecutionPolicy Bypass -File deploy\upload.ps1 -Server <服务器IP> -User root
```

带域名：

```powershell
powershell -ExecutionPolicy Bypass -File deploy\upload.ps1 -Server <服务器IP> -User root -Domain sms.example.com
```

换端口、用密钥：

```powershell
powershell -ExecutionPolicy Bypass -File deploy\upload.ps1 -Server <IP> -User root -Port 2222 -KeyFile C:\keys\id_ed25519
```

它会打包 → `scp` 上传 → SSH 里执行同一套 `deploy.sh`。

## 部署后的样子

```
你的电脑 ── 80/443 ──> nginx ── 127.0.0.1:5000 ──> gunicorn（单进程 16 线程） ──> Flask
```

- Flask 前面是 gunicorn，**不是** `app.run()`（那是开发用的）
- gunicorn **只开 1 个 worker**、16 条线程 —— 这个必须保持，原因见下一节
- 前端静态文件（`static/`）由 nginx 直接发，不经过 Python

## 为什么必须是单 worker

任务（进度、日志、结果）都存在内存的字典 `task.TASKS` 里。如果 gunicorn 开 4 个 worker：

```
浏览器 POST /api/tasks  →  worker #1 建了任务（存在 #1 的内存里）
浏览器 GET  /api/tasks/x →  worker #3  找不到这个任务，返回 404
```

所以 `deploy/gunicorn.conf.py` 里写死了 `workers = 1, threads = 16`。要真做多进程，得把任务挪到 Redis 里，那是另一个工程。

## 常用运维命令

```bash
systemctl status text-message-bombing     # 看状态
journalctl -u text-message-bombing -f     # 实时日志
systemctl restart text-message-bombing    # 重启
sudo bash deploy/deploy.sh                # 更新代码 + 重启
curl http://127.0.0.1:5000/healthz        # 健康检查
```

改端口、默认轮数、并发这些参数：编辑 `/opt/text-message-Bombing/settings.py`，然后 `systemctl restart text-message-bombing`。

## 加 HTTPS

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d sms.example.com
```

certbot 会自动改 nginx 配置并配好续期。

## 建议给页面加个密码

这个页面能直接发短信，别裸奔在公网上。nginx 加一层基础认证：

```bash
apt install -y apache2-utils
htpasswd -c /etc/nginx/.htpasswd admin     # 按提示设密码

# 然后在 nginx 的 server 块里（location / 之前）加：
#   auth_basic "restricted";
#   auth_basic_user_file /etc/nginx/.htpasswd;
nginx -t && systemctl reload nginx
```

或者只绑内网 / 用 SSH 隧道，不开公网：

```bash
# 不设 DOMAIN 部署，然后本机：
ssh -L 5000:127.0.0.1:5000 root@<服务器IP>
# 浏览器开 http://127.0.0.1:5000
```

## 防火墙

云服务器光在系统里放行不够，**控制台的安全组**也要放 80/443：

```bash
# Ubuntu
ufw allow 80/tcp && ufw allow 443/tcp
# CentOS / Rocky
firewall-cmd --permanent --add-service=http --add-service=https && firewall-cmd --reload
```

只走 SSH 隧道的话，5000 端口不用对外开。

## 排错

| 现象 | 原因 / 处理 |
| --- | --- |
| `服务没起来` | `journalctl -u text-message-bombing -n 50 --no-pager`，常见是依赖没装上 |
| 5000 端口没响应 | 看 `gunicorn.conf.py` 的 bind 是不是 `127.0.0.1:5000`，被别的东西占了就改端口 |
| 打开域名 502 | nginx 连不上后端：`systemctl status text-message-bombing`，再 `curl 127.0.0.1:5000/healthz` |
| 页面能开但点开始没反应 | 多半是前端请求被 nginx 拦了，看浏览器 F12 的 Network，再看 nginx 的 error.log |
| 任务查不到（404） | gunicorn 被改成了多 worker，改回 `workers = 1` |
| 服务重启后任务没了 | 正常，任务存在内存里，没有数据库 |

## Windows 服务器

这个项目在 Windows 上也能跑，只是 gunicorn 不支持 Windows，换成 waitress：

```powershell
pip install -r requirements.txt
pip install waitress

# 注意 --call 后面写 app:create_app，不要带括号（waitress 的写法）
waitress-serve --threads=16 --listen=127.0.0.1:5000 --call app:create_app
```

想开机自启可以用 NSSM：

```powershell
nssm install text-message-Bombing "C:\Python\python.exe" "-m waitress --threads=16 --listen=127.0.0.1:5000 --call app:create_app"
nssm start text-message-Bombing
```

前面再用 IIS 的 ARR 或者 nginx for Windows 反代 80。
