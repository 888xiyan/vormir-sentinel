# Vormir Sentinel 第二阶段计划

> 文档版本：v1.0  
> 计划日期：2026-10-29  
> 目标版本：v0.6.0  
> 实施状态：开发与构建验证完成（2026-10-29），待人工验收与发布
> 依赖基线：v0.5.0，CLI、角色引擎、剧情状态机、谜题和打包已完成

## 1. 第二阶段目标

第二阶段不继续扩展主线内容，而是把“首次启动到进入 Agent 页面”变成完整、可感知的产品流程。

目标分为三部分：

1. README 变成面向用户的安装和启动文档。
2. 启动时自动跟踪本机 Ollama，提供模型发现、选择、手动安装命令和离线入口。
3. 将 99% 进度后的剧情转场升级为 RedSkoll Agent 页面，支持固定脚本的 `/` 命令。

本阶段完成后的标准体验：

```text
运行 vormir-sentinel
  -> 检测本机 Ollama 和已安装模型
  -> 用户选择 GPU / CPU / 自定义模型 / 离线模式
  -> 安装诱饵进度条推进到 99%
  -> VS Terminal 激活，RedSkoll 命令执行成功
  -> 进入红色骷髅风格的 Agent 页面
  -> 普通文本交给本地模型
  -> / 命令由内置脚本返回固定剧情结果
```

## 2. 范围边界

### 2.1 本阶段包含

- 精简 README，突出 Ollama 前置要求。
- 本地 Ollama 服务发现。
- 本地已安装模型列表和推荐模型匹配。
- GPU/CPU/自定义模型/离线模式选择。
- 只打印、不执行的模型安装命令。
- RedSkoll 安装进度条。
- 99% 停顿、Glitch、VS Terminal 激活转场。
- Agent 页面布局、状态栏、对话记录、输入区。
- `/` 斜杠命令选择器和固定脚本响应。
- 旧 POSIX 虚拟终端作为兼容模式保留。
- 启动流程、模型选择和斜杠命令的自动化测试。

### 2.2 本阶段不包含

- 后台自动执行 `ollama pull`。
- 从远程 API 下载模型或上传对话。
- 伪装成真实 Claude Code、VS Code 或 Anthropic 安装器。
- 使用 Anthropic 官方 Logo、图标、文案或视觉资产。
- 真实执行 shell 命令。
- 多模型并行推理、联网搜索或 Agent 工具调用。
- 改动 Death Echoes 答案和已有谜题碎片。

## 3. README 重写

### 3.1 保留内容

README 只保留新用户进入项目所需的最小信息：

1. 一句话介绍。
2. Ollama 必须先安装。
3. 推荐 GPU/CPU 模型及手动下载命令。
4. 三种启动方式：自动、指定模式、离线。
5. 安全边界。
6. 常见故障。
7. 开发和测试命令。
8. 完整方案、第二阶段计划和安全文档链接。

### 3.2 移除内容

- 长篇功能清单。
- 仓库内部状态和历史进度。
- 完整文件树。
- 已完成路线图。
- 参赛提交模板。
- 与首次使用无关的项目管理信息。

这些内容分别迁移到 `PROJECT_MANAGEMENT.md`、`SUBMISSION.md`、`Vormir_Sentinel_完整方案.md` 和 `docs/`。

### 3.3 README 建议结构

```text
Vormir Sentinel
What it is
Requirements
Install Ollama
Download a model
Start the terminal
Model modes
Slash commands
Safety
Troubleshooting
Development
Documentation
License
```

### 3.4 必须出现的启动命令

README 明确展示：

```bash
ollama serve
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull qwen2.5:3b-instruct-q4_K_M
vormir-sentinel
vormir-sentinel --mode gpu
vormir-sentinel --mode cpu
vormir-sentinel --offline
```

说明：Vormir Sentinel 不在后台执行这些命令，只提示用户自行复制执行。

## 4. Ollama 启动探测

### 4.1 探测顺序

启动时执行以下只读检查：

1. 读取 `config/models.toml` 的推荐模型配置。
2. 访问 `http://127.0.0.1:11434/api/tags`。
3. 获取本机已安装模型名称、大小和更新时间。
4. 检测可用显存和系统内存。
5. 匹配 GPU、CPU、应急和离线配置。
6. 让用户确认模式。

不得执行 `ollama pull`、`ollama run` 或任何主机命令。

### 4.2 启动结果状态

| 状态 | 条件 | 行为 |
|---|---|---|
| `OLLAMA_READY_GPU` | Ollama 可用且 GPU 模型已安装 | 推荐 GPU 模型 |
| `OLLAMA_READY_CPU` | CPU 推荐模型已安装 | 推荐 CPU 模型 |
| `OLLAMA_READY_CUSTOM` | 只有用户模型可用 | 显示自定义模型选择 |
| `OLLAMA_NO_MODEL` | 服务可用但没有匹配模型 | 展示下载命令，不自动下载 |
| `OLLAMA_NOT_RUNNING` | loopback 端口不可用 | 展示 `ollama serve` 提示 |
| `OFFLINE` | 用户选择离线或资源不足 | 使用固定剧情和离线回答 |

### 4.3 模型选择界面

启动选择器提供固定选项：

```text
1. GPU / Qwen2.5 7B Instruct
2. CPU / Qwen2.5 3B Instruct
3. Custom model
4. Offline mode
5. Show download command
```

选择 `Custom model` 时：

- 优先列出 `/api/tags` 返回的模型。
- 用户可以手动输入模型名。
- 模型名只作为 Ollama API 的字符串传递。
- 不从模型名拼接文件路径或 shell 命令。
- 不存在的模型回退到提示和离线模式。

### 4.4 下载命令行为

选择“Show download command”后只输出：

```text
Run this command yourself:

  ollama pull qwen2.5:7b-instruct-q4_K_M

After it finishes, return to Vormir Sentinel.
```

页面不得显示虚假的后台进度，也不得暗示模型正在下载。

### 4.5 实现位置

优先扩展现有模块：

- `model_policy.py`：增加模型发现结果和选择状态。
- `ollama.py`：增加只读模型元数据接口。
- `cli.py`：增加启动选择器和启动阶段。
- `config/models.toml`：保留推荐模型和自定义模型默认值。
- 新增 `startup.py`：集中管理启动状态，不让 `cli.py` 继续膨胀。

## 5. RedSkoll 安装剧情

### 5.1 进度条阶段

启动流程显示模拟安装进度：

```text
Fetching RedSkoll Agent CLI...
Resolving local model bridge...
Mapping host architecture...
Mounting Vormir memory...
Validating Stonekeeper signature...
```

进度阶段：

```text
12%  fetching
37%  resolving
64%  mapping
88%  memory
99%  pause and detect host
```

进度条使用 Rich `Progress`；低刺激模式使用无动画文本行。

### 5.2 99% 异变

进度到 99% 后执行：

1. 停顿约 800ms。
2. 输出一次低频 Glitch。
3. 显示以下固定文本：

```text
Warning: Host architecture resolved as HYDRA-SOULKEEPER.
Warning: NT subsystem identity is non-authoritative.
RedSkoll command: OK
VS Terminal activation: OK
Agent handshake: ACCEPTED
```

4. 清屏或切换到 Agent 页面。
5. 显示 RedSkoll ASCII 头像和状态栏。

安全边界文本必须保留：

```text
[fictional takeover only; no host command was executed]
```

### 5.3 视觉名称

产品内部页面名称使用：

```text
RedSkoll Agent Terminal
```

不使用 Claude、Anthropic 或 VS Code 的 Logo、图标和品牌资产。布局可以参考本地 Agent 终端的交互习惯，但必须使用原创 RedSkoll/紫翠绿风格标识。

## 6. Agent 页面

### 6.1 页面布局

第一版使用现有 Rich 依赖实现终端页面，避免立即引入完整 TUI 依赖：

```text
+--------------------------------------------------------------+
| REDSKOLL AGENT   model: qwen2.5:7b   mode: GPU   context: 8k |
| [● ONLINE]     [SAFE EXIT: exit --now]       [/ for commands]|
+--------------------------------------------------------------+
|                                                              |
|  RedSkoll                                                    |
|  The host is ready. Ask, and pay in attention.               |
|                                                              |
|  > your previous conversation and assistant output          |
|                                                              |
+--------------------------------------------------------------+
| root@vormir:/#                                               |
+--------------------------------------------------------------+
```

页面包括：

- 顶部状态栏：模型、运行模式、上下文和服务状态。
- RedSkoll 标识区：ASCII 头像或短标识。
- 对话记录区：用户输入和模型流式回答。
- 底部输入区：提示符、输入行和退出提示。
- `/` 命令状态：命令补全或命令选择提示。

### 6.2 交互分派

输入按以下顺序处理：

```text
以 / 开头
  -> SlashCommandRegistry

属于虚拟 POSIX 命令
  -> CommandRouter

exit / quit / Ctrl+C
  -> 安全退出流程

其他文本
  -> 本地 Ollama 或离线角色引擎
```

这样保留现有 `ls`、`whoami`、`uname` 等伪命令，同时新增 Agent 页面习惯。

### 6.3 降级方式

以下情况自动使用纯终端模式，不进入全页布局：

- `stdin` 或 `stdout` 不是 TTY。
- `--plain` 或 `--no-color`。
- `--safe`。
- `--offline`。
- 终端宽度不足 60 列。

## 7. `/` 斜杠命令

### 7.1 第二阶段命令集

| 命令 | 固定响应 |
|---|---|
| `/help` | 显示 Agent 命令和安全退出方式 |
| `/model` | 显示当前模型、模式、上下文和 Ollama 状态 |
| `/model list` | 列出本机已安装模型 |
| `/model select <name>` | 选择本机已安装模型 |
| `/download <model>` | 仅打印 `ollama pull <model>` |
| `/offline` | 切换为固定剧情模式 |
| `/status` | 显示阶段、模型、服务和安全状态 |
| `/story` | 显示当前剧情阶段和下一步提示 |
| `/context` | 显示当前对话上下文长度和摘要状态 |
| `/clear` | 清空 Agent 页面对话记录，不清空故事状态 |
| `/relic` | 显示已生成遗物和授权输出目录 |
| `/reconstruct` | 显示 Death Echo 碎片，不增加回响计数 |
| `/tribute` | 展示符号献祭类型 |
| `/safe` | 切换低刺激模式 |
| `/exit` | 返回真实安全退出流程 |

### 7.2 固定脚本格式

新增脚本目录：

```text
src/vormir_sentinel/scripts/
├── startup.json
├── slash_commands.json
├── redskoll_agent.json
└── takeover.json
```

JSON 结构示例：

```json
{
  "commands": {
    "/status": {
      "kind": "fixed",
      "text": "RedSkoll agent status is nominal.",
      "state_updates": []
    }
  }
}
```

约束：

- 固定脚本不能包含可执行 Python 或 shell。
- 变量只能通过白名单占位符注入。
- 固定文本不得声称已控制真实主机。
- `/download` 不能调用任何下载函数。
- `/model select` 只能修改内存中的模型配置，不写入系统配置。

### 7.3 命令注册器

新增 `slash.py`：

- `SlashCommand` 数据类。
- `SlashCommandRegistry` 注册、补全和路由。
- `render(command, context)` 生成固定响应。
- `SlashContext` 持有模型、Ollama 状态、剧情阶段和安全状态。

现有 `CommandRouter` 继续负责虚拟 POSIX 命令，不把 `/` 命令塞入 POSIX 白名单。

## 8. 剧情状态机扩展

### 8.1 新阶段

当前 `StoryAct` 增加以下阶段：

```text
MODEL_SELECTION
INSTALL_PROGRESS
SYSTEM_METAMORPHOSIS
AGENT_PAGE
```

保留已有 `BOOT`、`VORMIR_SHELL`、`TAKEOVER`、`CLEARED`。

### 8.2 阶段转换

```text
MODEL_SELECTION
  -> INSTALL_PROGRESS
       -> SYSTEM_METAMORPHOSIS
            -> AGENT_PAGE
                 -> VORMIR_SHELL (兼容模式)
                 -> TAKEOVER
                 -> CLEARED
```

离线模式允许：

```text
MODEL_SELECTION
  -> OFFLINE_AGENT_PAGE
```

### 8.3 可恢复性

- 已完成安装诱饵的用户下次启动直接进入模型选择或 Agent 页面。
- 模型选择结果保存在应用状态，不覆盖全局 Ollama 配置。
- Agent 页面异常退出后，恢复到上一个安全阶段。
- `--safe` 永远跳过 Glitch 和安装动画。

## 9. 实施拆分

### 第一批：README 与启动

1. 编写新的 README 初稿。
2. 增加 `startup.py`。
3. 扩展 `OllamaClient` 的只读模型元数据接口。
4. 增加模型选择交互。
5. 增加 `--pick-model`、`--list-models`、`--offline` 启动入口。
6. 测试服务不可用、无模型、GPU/CPU 匹配和自定义模型。

### 第二批：安装剧情与 Agent 页面

1. 将 `StoryDirector.begin()` 扩展为可恢复的安装进度场景。
2. 实现 99% 停顿和固定异变文本。
3. 实现 RedSkoll Agent 页面布局。
4. 增加 `/` 命令注册器。
5. 接入当前对话引擎和虚拟命令路由。
6. 增加纯文本、TTY 和安全模式降级。

### 第三批：测试与发布

1. 增加启动状态机测试。
2. 增加模型列表和自定义模型测试。
3. 增加所有 `/` 固定命令测试。
4. 验证 `/download` 没有任何子进程或网络副作用。
5. 更新 README、CHANGELOG 和 Release Notes。
6. 更新版本到 `0.6.0`。

## 10. 验收标准

### README

- 首屏 30 秒内能知道需要安装 Ollama。
- 能找到 GPU/CPU 模型下载命令。
- 能找到离线模式和安全退出方式。
- 不包含内部开发历史和长篇路线图。

### Ollama 启动

- 服务不可用时显示 `ollama serve`，不自动启动服务。
- 服务可用时列出本机模型。
- 有匹配模型时给出 GPU/CPU 推荐。
- 无匹配模型时只显示下载命令。
- 自定义模型只从列表或用户输入选择。
- 全流程没有后台下载和主机命令执行。

### Agent 页面

- 进度条能推进到 99%。
- 99% 后显示固定异变转场。
- Agent 页面显示 RedSkoll 标识，不显示 Claude/Anthropic 资产。
- 普通文本进入本地模型或离线引擎。
- `/` 命令进入固定脚本注册器。
- POSIX 伪命令仍然可用。
- 管道输入、`--plain`、`--safe` 和窄终端自动降级。

### 安全

- `/download` 不调用下载函数。
- 模型名不拼接到 shell。
- Ollama 请求仍然只允许 loopback。
- `/clear` 只清屏和清对话记录，不删除状态。
- `/exit`、`exit --now`、Ctrl+C 两次和关闭窗口始终能退出。

## 11. 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| 用户把 99% 进度当真实下载 | 误解产品 | 固定加入 fictional takeover 标记 |
| Ollama API 不返回模型信息 | 无法选择模型 | 回退到离线和手写命令提示 |
| 自定义模型名被误认为命令 | 安全风险 | 只作为 API 字符串，不进入 shell |
| Rich 页面在窄终端溢出 | 体验破坏 | 宽度检测和纯文本降级 |
| `/` 命令与普通文本混淆 | 剧情和模型路由混乱 | 分派优先级固定并测试 |
| README 再次膨胀 | 用户找不到启动步骤 | 保留最小首屏，扩展内容移入 docs |

## 12. 完成定义

第二阶段完成时必须同时满足：

1. README 已精简并明确 Ollama 前置要求。
2. 启动时能发现本地 Ollama 和已安装模型。
3. 用户可以选择推荐模型、自定义模型、手动下载命令或离线模式。
4. 安装进度、99% 异变和 Agent 页面转场可重复运行。
5. RedSkoll Agent 页面支持普通对话和 `/` 固定命令。
6. POSIX 虚拟命令、退出和安全模式全部保持兼容。
7. 新增测试覆盖启动、模型、页面和斜杠命令。
8. `ruff`、`mypy`、`pytest`、遗物检查全部通过。
9. 版本、CHANGELOG、Release Notes 与 README 对齐。
10. 仍不存在真实命令执行、后台下载、远程推理或隐私上传。
