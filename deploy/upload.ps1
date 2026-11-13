# 从 Windows 本机打包上传 + 部署到 Linux 服务器
#
# 用法（在项目根目录）：
#     powershell -ExecutionPolicy Bypass -File deploy\upload.ps1 -Server 1.2.3.4 -User root
#
# 带域名（顺便配 nginx）：
#     powershell -ExecutionPolicy Bypass -File deploy\upload.ps1 -Server 1.2.3.4 -User root -Domain sms.example.com
#
# 说明：本机到 GitHub 的 443 不通也没关系，这个脚本直接把当前目录打包，
#      用 scp 传到服务器再解压，不依赖服务器能不能访问 GitHub。

param(
    [Parameter(Mandatory = $true)][string]$Server,
    [string]$User = "root",
    [int]$Port = 22,
    [string]$AppDir = "/opt/text-message-Bombing",
    [string]$Domain = "",
    [string]$KeyFile = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$tarFile = Join-Path $env:TEMP "text-message-Bombing.tar.gz"

Write-Host "[*] 打包 $projectRoot" -ForegroundColor Cyan
if (Test-Path $tarFile) { Remove-Item $tarFile -Force }

# 只打包跑起来需要的东西
Push-Location $projectRoot
try {
    tar -czf $tarFile `
        --exclude=.git --exclude=__pycache__ --exclude=.venv `
        --exclude=.ruff_cache --exclude=backup --exclude=docs .
    if ($LASTEXITCODE -ne 0) { throw "打包失败" }
} finally {
    Pop-Location
}
Write-Host ("[+] 包大小 {0:N1} KB" -f ((Get-Item $tarFile).Length / 1KB)) -ForegroundColor Green

$sshArgs = @("-p", "$Port")
$scpArgs = @("-P", "$Port")
if ($KeyFile) {
    $sshArgs += @("-i", $KeyFile)
    $scpArgs += @("-i", $KeyFile)
}

Write-Host "[*] 上传到 ${User}@${Server}:/tmp/" -ForegroundColor Cyan
& scp @scpArgs $tarFile "${User}@${Server}:/tmp/text-message-Bombing.tar.gz"
if ($LASTEXITCODE -ne 0) { throw "scp 失败，检查地址、端口、密钥" }

Write-Host "[*] 在服务器上解压并部署" -ForegroundColor Cyan
$remote = @"
set -e
rm -rf /tmp/tmb-src && mkdir -p /tmp/tmb-src
tar -xzf /tmp/text-message-Bombing.tar.gz -C /tmp/tmb-src
SRC_DIR=/tmp/tmb-src APP_DIR=$AppDir DOMAIN=$Domain bash /tmp/tmb-src/deploy/deploy.sh
"@

& ssh @sshArgs "${User}@${Server}" $remote
if ($LASTEXITCODE -ne 0) { throw "远端部署失败，看上面的输出" }

Write-Host ""
Write-Host "[+] 搞定" -ForegroundColor Green
if ($Domain) {
    Write-Host "    打开 http://$Domain"
} else {
    Write-Host "    用 SSH 隧道访问：ssh -L 5000:127.0.0.1:5000 -p $Port $User@$Server"
    Write-Host "    然后浏览器打开 http://127.0.0.1:5000"
}
