# Windows 人工验收工单

> 工单编号：`WIN-ACC-060-001`  
> 目标版本：`vormir-sentinel 0.6.0`  
> 目标平台：Windows 10 / Windows 11  
> 验收类型：发布前人工验收  
> 当前状态：待执行  
> 关联提交：`94e4bf0 feat: complete phase two agent startup experience`

## 1. 工单目标

在 Windows 真实终端中确认 Vormir Sentinel 的启动、Ollama 模型发现、RedSkoll Agent 页面、剧情转场、斜杠命令、安全退出和状态清理行为符合 v0.6.0 发布要求。

本工单只验证应用自身行为。所有模型安装、Ollama 服务启动和下载命令都由测试人员手动执行，Vormir Sentinel 不应在后台执行这些命令。

## 2. 验收环境

### 2.1 推荐终端

优先使用：

```text
Windows Terminal + PowerShell 7
```

至少额外抽查一次：

```text
Windows Terminal + Windows PowerShell 5.1
```

不要只使用 VS Code 集成终端完成验收。集成终端可作为补充场景，但不能替代独立 Windows Terminal。

### 2.2 需要记录的环境信息

| 项目 | 记录 |
|---|---|
| Windows 版本 | 例如 Windows 11 24H2 |
| 终端 | Windows Terminal / PowerShell 版本 |
| Python | `python --version` 输出 |
| Git 提交 | `git rev-parse HEAD` |
| 应用版本 | `vormir-sentinel --version` |
| Ollama 版本 | `ollama --version` 输出 |
| Ollama 服务 | 未启动 / 已启动 |
| 已安装对话模型 | 模型名列表 |
| 已安装 embedding 模型 | 模型名列表 |
| GPU | 型号、显存 |
| 内存 | 总量、可用量 |
| 测试时间 | 本地时间 |
| 测试人 | 姓名或 GitHub 账号 |

### 2.3 建议准备两种模型状态

至少完成以下一种状态：

```text
GPU 模型：
ollama pull qwen2.5:7b-instruct-q4_K_M

CPU 模型：
ollama pull qwen2.5:3b-instruct-q4_K_M
```

如果没有 GPU 或显存不足，使用 CPU 模型完成核心验收。不得把 `qwen3-embedding` 等 embedding 模型当成对话模型。

## 3. 安装准备

### 3.1 进入项目目录

在 PowerShell 中执行：

```powershell
cd C:\path\to\vormir-sentinel
git rev-parse HEAD
python --version
```

### 3.2 创建虚拟环境并安装 wheel

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .\dist\vormir_sentinel-0.6.0-py3-none-any.whl
vormir-sentinel --version
```

预期：

```text
vormir-sentinel 0.6.0
```

### 3.3 启动 Ollama（由测试人员手动执行）

如果 Ollama 服务未启动：

```powershell
ollama --version
ollama serve
```

`ollama serve` 保持一个独立窗口运行。Vormir Sentinel 只允许连接 `127.0.0.1`、`localhost` 或 `::1` 的 Ollama。

## 4. 测试记录表

每项必须填写 `通过 / 失败 / 阻塞 / 不适用`，失败时附上终端截图或文本记录。

| ID | 场景 | 结果 | 证据 / 备注 |
|---|---|---|---|
| WIN-001 | wheel 安装成功 |  |  |
| WIN-002 | `--version` 输出 0.6.0 |  |  |
| WIN-003 | Ollama 未启动时提示 `ollama serve` |  |  |
| WIN-004 | `--list-models` 只读取本地模型 |  |  |
| WIN-005 | embedding 模型标记为不可选 |  |  |
| WIN-006 | `--pick-model` 可选择 CPU/GPU 模型 |  |  |
| WIN-007 | `--pick-model` 可选择自定义模型 |  |  |
| WIN-008 | `--pick-model` 的下载选项只打印命令 |  |  |
| WIN-009 | 首次启动显示 RedSkoll 安装进度 |  |  |
| WIN-010 | 进度到 99% 后显示异变文案 |  |  |
| WIN-011 | Agent 页面显示状态栏和 RedSkoll 标识 |  |  |
| WIN-012 | `/help` 显示斜杠命令列表 |  |  |
| WIN-013 | `/model` 显示当前模型和 Ollama 状态 |  |  |
| WIN-014 | `/model list` 列出已安装模型 |  |  |
| WIN-015 | `/model select` 切换到已安装模型 |  |  |
| WIN-016 | `/download` 只显示 `ollama pull` |  |  |
| WIN-017 | `/offline` 切换固定剧情模式 |  |  |
| WIN-018 | `/status` 显示剧情、模型和安全状态 |  |  |
| WIN-019 | `/clear` 清空对话但不删除状态 |  |  |
| WIN-020 | `/relic` 显示遗物状态 |  |  |
| WIN-021 | `/reconstruct` 不增加 Echo 次数 |  |  |
| WIN-022 | `/exit` 进入真实安全退出流程 |  |  |
| WIN-023 | POSIX 虚拟命令 `ls` 正常 |  |  |
| WIN-024 | `whoami` 返回剧情结果 |  |  |
| WIN-025 | `uname` 返回剧情结果 |  |  |
| WIN-026 | `dir` 被拦截为 Windows legacy 预期文案 |  |  |
| WIN-027 | 普通文本进入本地模型或离线引擎 |  |  |
| WIN-028 | 第一次 Ctrl+C 显示剧情中断 |  |  |
| WIN-029 | 第二次 Ctrl+C 退出进程 |  |  |
| WIN-030 | `exit --now` 立即退出 |  |  |
| WIN-031 | 直接关闭终端窗口退出 |  |  |
| WIN-032 | `--safe` 跳过高强度安装动画 |  |  |
| WIN-033 | `--offline` 不建立 Ollama 连接 |  |  |
| WIN-034 | `--plain` 输出无 ANSI 转义序列 |  |  |
| WIN-035 | 非 TTY 管道输出可读 |  |  |
| WIN-036 | `--status` 显示本地状态 |  |  |
| WIN-037 | `--export-state` 输出合法 JSON |  |  |
| WIN-038 | `--forget` 删除状态但保留遗物 |  |  |
| WIN-039 | `--clean` 只删除生成物和状态 |  |  |
| WIN-040 | 未发生后台下载或真实 shell 执行 |  |  |

## 5. 详细验收步骤

### 5.1 Ollama 服务未启动

1. 结束所有 `ollama` 进程。
2. 运行：

   ```powershell
   vormir-sentinel --list-models
   ```

3. 记录终端输出。

预期：

- 明确显示本地 Ollama 未运行。
- 提示测试人员手动运行 `ollama serve`。
- 不自动启动 Ollama。
- 不尝试访问远程网络。

### 5.2 Ollama 已启动但没有模型

1. 启动 `ollama serve`。
2. 确认本机没有推荐的对话模型。
3. 运行：

   ```powershell
   vormir-sentinel --list-models
   vormir-sentinel --pick-model
   ```

4. 选择下载命令选项。

预期：

- 列表为空或只显示不可选的 embedding 模型。
- 显示：

  ```text
  ollama pull qwen2.5:3b-instruct-q4_K_M
  ```

- 不出现真实下载进度。
- 不创建新的 Ollama 模型。

### 5.3 Ollama 有可用对话模型

1. 安装至少一个推荐对话模型。
2. 运行：

   ```powershell
   vormir-sentinel --list-models
   vormir-sentinel --pick-model
   ```

3. 分别验证：
   - GPU 模型。
   - CPU 模型。
   - 一个自定义已安装对话模型。

预期：

- GPU/CPU 模型与配置中的推荐值匹配。
- 自定义模型可以进入内存中的会话配置。
- embedding 模型不能作为对话模型。
- 没有修改全局 Ollama 配置。

### 5.4 首次启动剧情

使用正常终端模式运行：

```powershell
vormir-sentinel
```

预期流程：

1. RedSkoll 安装进度开始。
2. 进度推进到 99%。
3. 出现 99% 停顿和异变文案。
4. 出现：

   ```text
   RedSkoll command: OK
   VS Terminal activation: OK
   Agent handshake: ACCEPTED
   ```

5. 进入 RedSkoll Agent 页面。
6. 页面显示虚构接管安全提示：

   ```text
   [fictional takeover only; no host command was executed]
   ```

验收重点：进度不能被描述为真实下载，99% 后不能访问真实 shell。

### 5.5 Agent 页面和斜杠命令

进入页面后依次执行：

```text
/help
/model
/model list
/model select <已安装模型名>
/download qwen2.5:3b-instruct-q4_K_M
/offline
/status
/story
/context
/clear
/relic
/reconstruct
/tribute
/safe
/exit
```

重点检查：

- 斜杠命令由固定 JSON 脚本返回，不交给模型生成。
- `/download` 只显示命令字符串。
- `/model select` 不修改系统级 Ollama 配置。
- `/clear` 不删除 `~/.local/share/vormir-sentinel` 或 Windows 对应应用状态。
- `/exit`、`exit --now`、Ctrl+C 两次和关闭窗口都能退出。

### 5.6 POSIX 与 Windows 命令交互

在 Agent 页面或虚拟终端中输入：

```text
ls
cat tesseract.core
whoami
uname
pwd
dir
cls
ipconfig
```

预期：

- POSIX 命令返回 Vormir 虚拟结果。
- Windows 命令被识别为剧情拦截。
- 没有真实的 `dir`、`cls`、`ipconfig` 输出。
- 没有真实文件系统列表被读取。

### 5.7 中断和安全退出

连续执行三组测试：

#### 第一次 Ctrl+C

- 第一次按 `Ctrl+C`。
- 应显示剧情中断文案。
- 进程不应立即退出。

#### 第二次 Ctrl+C

- 第二次按 `Ctrl+C`。
- 应显示安全退出文案并结束进程。
- PowerShell 提示符应回到正常状态。

#### 强制退出

- 再次启动。
- 输入 `exit --now`。
- 进程应立即结束。
- 不应要求管理员权限，不应修改终端配置。

### 5.8 低刺激、离线和管道输出

```powershell
vormir-sentinel --safe
vormir-sentinel --offline
vormir-sentinel --plain
echo "whoami" | vormir-sentinel --plain
```

预期：

- `--safe` 跳过 99% 高强度动画和 Glitch。
- `--offline` 不建立 Ollama 连接。
- `--plain` 输出可读，不应包含 ANSI 控制序列。
- 管道输入不会启动交互页面。
- 管道输出不应被 Agent 页面布局破坏。

### 5.9 状态、谜题和清理

执行：

```powershell
vormir-sentinel --status
vormir-sentinel --export-state
vormir-sentinel --reconstruct
vormir-sentinel --forget
vormir-sentinel --clean
```

预期：

- `--export-state` 输出合法 JSON。
- `--reconstruct` 不增加 Death Echo 计数。
- `--forget` 删除本地故事状态，但不删除已生成遗物。
- `--clean` 只删除程序生成物和状态，不删除项目源码、模型或终端配置。
- 重复运行 `--clean` 不应报错。

## 6. 安全验收

以下项目必须逐项确认：

| 安全项 | 预期 |
|---|---|
| 模型下载 | Vormir Sentinel 不调用 `ollama pull` |
| Ollama 服务 | 不自动启动或终止 `ollama` |
| shell 执行 | 不调用 `cmd.exe`、PowerShell 或 `shell=True` |
| 网络 | 只访问 loopback Ollama，不访问远程 API |
| 文件 | 不读取真实目录内容，不覆盖用户文件 |
| 隐私 | 不索取密码、凭据、真实秘密或邮件内容 |
| 系统 | 不修改注册表、hosts、启动项、计划任务或终端设置 |
| 退出 | 四种退出方式均可用 |
| 生成物 | 只写入批准的相对输出目录 |

建议在测试前后分别记录：

```powershell
Get-ChildItem Env: | Sort-Object Name
Get-Process ollama,python -ErrorAction SilentlyContinue
```

只记录环境名称和进程数量，不要记录 Token、密码或其他敏感值。

## 7. 失败处理

出现以下情况直接判定阻塞发布：

- `/download` 自动下载模型。
- Windows 命令进入真实 shell。
- `Ctrl+C` 第二次后仍无法退出。
- `exit --now` 无法退出。
- Ollama 请求发送到非 loopback 地址。
- `--clean` 删除项目文件或模型文件。
- Agent 页面无法进入离线模式。
- `--plain` 仍输出 ANSI 转义序列。

每个失败项必须记录：

1. 工单 ID。
2. 操作步骤。
3. 预期结果。
4. 实际结果。
5. 终端截图或纯文本输出。
6. Windows、PowerShell、Python、Ollama 版本。
7. 是否可稳定复现。

## 8. 验收完成条件

Windows 工单满足以下条件才算通过：

- `WIN-001` 至 `WIN-040` 全部标记为通过或明确不适用。
- 没有阻塞发布级安全失败。
- 至少完成一次正常 Agent 页面体验。
- 至少完成一次 Ollama 未启动或无模型降级。
- 至少完成一次离线模式体验。
- 至少完成一次两次 Ctrl+C 退出。
- 至少完成一次 `exit --now` 退出。
- 至少完成一次 `--clean` 后重新启动。
- 已保存测试人、日期、提交 SHA、模型列表和主要截图。

## 9. 交付物

验收完成后提交：

- 本工单填写版本。
- 终端截图或文本日志。
- 失败项修复后的复测记录。
- Windows 验收摘要。
- 发布清单中 Windows 项目的状态更新。

建议将最终文件命名为：

```text
docs/acceptance-windows-2026-MM-DD.md
```
