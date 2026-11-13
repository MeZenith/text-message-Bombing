// text-message-Bombing —— 前端逻辑
// 干的事很简单：收表单 -> 调 /api/tasks 建任务 -> 每 0.6 秒问一次进度 -> 画到页面上。

const $ = (id) => document.getElementById(id);

let currentTaskId = null;   // 当前正在看的任务
let timer = null;           // 轮询的定时器
let lastRecentJson = "";    // 上次画的表格内容，没变就不重画
const seenLogs = new Set(); // 已经显示过的日志，避免重复

// ---------------------------------------------------------------- 小工具
async function api(path, options) {
  const res = await fetch(path, options);
  let data = {};
  try {
    data = await res.json();
  } catch (err) {
    data = {};
  }
  if (!res.ok) {
    throw new Error(data.error || "请求失败：" + res.status);
  }
  return data;
}

function setHint(text, isError) {
  const hint = $("hint");
  hint.textContent = text;
  hint.className = isError ? "hint err" : "hint";
}

function statusClass(status) {
  if (status === "发送中" || status === "等待中") return "running";
  if (status === "已完成") return "done";
  if (status === "已停止") return "stopped";
  if (status === "出错了") return "error";
  return "idle";
}

// ---------------------------------------------------------------- 日志
function addLog(text, level) {
  const box = $("log");
  const line = document.createElement("div");
  line.className = "log-line " + (level || "info");
  line.textContent = text;
  box.appendChild(line);

  while (box.childElementCount > 300) {
    box.removeChild(box.firstChild);
  }
  box.scrollTop = box.scrollHeight;
}

function showLogs(logs) {
  for (const item of logs) {
    const key = item.time + "|" + item.text;
    if (seenLogs.has(key)) continue;
    seenLogs.add(key);
    addLog(item.time + "  " + item.text, item.level);
  }
  // 日志太多时清一下记录，防止它无限变大
  if (seenLogs.size > 800) {
    seenLogs.clear();
  }
}

// ---------------------------------------------------------------- 表格
function renderTable(recent) {
  const json = JSON.stringify(recent);
  if (json === lastRecentJson) return;
  lastRecentJson = json;

  const body = $("recent");
  body.innerHTML = "";

  if (!recent || recent.length === 0) {
    body.innerHTML = '<tr class="empty"><td colspan="3">还没有开始</td></tr>';
    return;
  }

  // 新的一行放最上面，看起来像"最新的在顶上"
  for (let i = recent.length - 1; i >= 0; i--) {
    const item = recent[i];
    const tr = document.createElement("tr");

    const name = document.createElement("td");
    name.textContent = item.name;
    name.title = item.error || "";

    const state = document.createElement("td");
    if (!item.ok) {
      state.textContent = "失败";
      state.className = "bad";
    } else if (item.status >= 400) {
      // 请求发出去了，但对方返回 4xx/5xx，大概率是被限流/拦了
      state.textContent = item.status;
      state.className = "warn";
    } else {
      state.textContent = item.status;
      state.className = "ok";
    }

    const cost = document.createElement("td");
    cost.textContent = item.cost + "s";

    tr.appendChild(name);
    tr.appendChild(state);
    tr.appendChild(cost);
    body.appendChild(tr);
  }
}

// ---------------------------------------------------------------- 进度
function render(data) {
  const badge = $("status");
  badge.textContent = data.status;
  badge.className = "badge " + statusClass(data.status);

  $("bar").style.width = data.percent + "%";
  $("done").textContent = data.done;
  $("total").textContent = data.total;
  $("success").textContent = data.success;
  $("failed").textContent = data.failed;
  $("elapsed").textContent = data.elapsed.toFixed(1) + "s";
  $("roundInfo").textContent = "第 " + data.round + "/" + data.rounds + " 轮";

  renderTable(data.recent);
  showLogs(data.logs);
}

function isFinished(status) {
  return status === "已完成" || status === "已停止" || status === "出错了";
}

// ---------------------------------------------------------------- 开始 / 停止
async function startTask() {
  const phone = $("phone").value.trim();

  if (!/^1[3-9]\d{9}$/.test(phone)) {
    $("phone").classList.add("bad");
    setHint("手机号要 11 位、1 开头，比如 13800000000", true);
    return;
  }
  $("phone").classList.remove("bad");

  const body = {
    phone: phone,
    rounds: Number($("rounds").value),
    workers: Number($("workers").value),
    timeout: Number($("timeout").value),
    filter: $("filter").value.trim(),
    limit: Number($("limit").value),
    voice: $("voice").checked,
    voice_times: Number($("voiceTimes").value),
    voice_gap: Number($("voiceGap").value),
  };

  $("start").disabled = true;
  setHint("正在创建任务……");

  try {
    const data = await api("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    currentTaskId = data.id;
    lastRecentJson = "";
    $("log").innerHTML = "";
    seenLogs.clear();
    addLog("任务 " + data.id + " 已创建，共 " + data.total + " 次请求", "warn");

    $("stop").disabled = false;
    setHint("任务 " + data.id + " 运行中，关掉页面也不会停（服务还在跑）。");

    render(data);
    poll();
  } catch (err) {
    $("start").disabled = false;
    setHint(err.message, true);
  }
}

async function stopTask() {
  if (!currentTaskId) return;
  $("stop").disabled = true;
  try {
    await api("/api/tasks/" + currentTaskId + "/stop", { method: "POST" });
    setHint("已发出停止指令，等当前这批发完。");
  } catch (err) {
    setHint(err.message, true);
  }
}

// ---------------------------------------------------------------- 轮询
async function poll() {
  if (!currentTaskId) return;

  try {
    const data = await api("/api/tasks/" + currentTaskId);
    render(data);

    if (isFinished(data.status)) {
      timer = null;
      $("start").disabled = false;
      $("stop").disabled = true;
      setHint("任务结束：" + data.status + "，共发出 " + data.done + " 次。");
      return;
    }
  } catch (err) {
    addLog("刷新进度失败：" + err.message, "fail");
  }

  timer = setTimeout(poll, 600);
}

// ---------------------------------------------------------------- 接口清单
async function loadEndpoints() {
  const box = $("endpointList");
  box.innerHTML = '<p class="muted">加载中……</p>';

  try {
    const data = await api("/api/endpoints");
    box.innerHTML = "";
    for (const item of data.items) {
      const row = document.createElement("div");
      row.className = "endline";

      const method = document.createElement("span");
      method.className = "m";
      method.textContent = item.method;

      const name = document.createElement("span");
      name.textContent = item.name;

      const url = document.createElement("span");
      url.className = "u";
      url.textContent = item.url;

      row.appendChild(method);
      row.appendChild(name);
      row.appendChild(url);
      box.appendChild(row);
    }
    $("listCount").textContent = data.total;
  } catch (err) {
    box.innerHTML = '<p class="muted">加载失败：' + err.message + "</p>";
  }
}

// ---------------------------------------------------------------- 初始化
async function loadOptions() {
  try {
    const data = await api("/api/options");
    $("rounds").value = data.rounds;
    $("workers").value = data.workers;
    $("timeout").value = data.timeout;
    $("voiceTimes").value = data.voice_times;
    $("voiceGap").value = data.voice_gap;
    $("endpointTotal").textContent = data.total_endpoints;
    $("listCount").textContent = data.total_endpoints;
  } catch (err) {
    setHint("连不上服务：" + err.message, true);
  }
}

// 页面刷新后，如果后台还有任务在跑，就直接接到它上面，不用重新点开始
async function restoreTask() {
  try {
    const data = await api("/api/tasks");
    const last = data.items[0];
    if (!last || isFinished(last.status)) return;

    currentTaskId = last.id;
    $("start").disabled = true;
    $("stop").disabled = false;
    setHint("接上后台正在跑的任务 " + last.id + "。");
    poll();
  } catch (err) {
    // 拿不到就算了，页面上不提示，别打扰用户
  }
}

$("start").addEventListener("click", startTask);
$("stop").addEventListener("click", stopTask);

$("phone").addEventListener("input", () => {
  $("phone").classList.remove("bad");
});

$("phone").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !$("start").disabled) {
    startTask();
  }
});

$("clearLog").addEventListener("click", () => {
  $("log").innerHTML = "";
  seenLogs.clear();
});

$("listBox").addEventListener("toggle", () => {
  if ($("listBox").open && $("endpointList").dataset.loaded !== "1") {
    $("endpointList").dataset.loaded = "1";
    loadEndpoints();
  }
});

loadOptions();
restoreTask();
