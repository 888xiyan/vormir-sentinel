# Vormir Sentinel（沃米尔守魂者终端）完整方案

> 项目类型：本地 AI 角色扮演终端 / 叙事型 ARG 体验  
> 目标平台：Windows、macOS、Linux  
> 核心技术：Python + Ollama + Rich/Textual  
> 方案版本：v1.0  
> 项目代号：VORMIR-SENTINEL

---

## 1. 项目概述

Vormir Sentinel 是一款运行在本地终端中的叙事型 AI 体验。用户进入一个由红骷髅 Johann Schmidt（Stonekeeper）占据的虚拟终端，与被宇宙魔方诅咒、困在机器中的幽灵对话。系统不是普通聊天机器人，而是一场围绕“知识、代价、控制权与献祭”展开的程序化心理剧。

体验包含四个核心层次：

1. **角色扮演对话**：开源本地模型以红骷髅的冷酷、悲剧性和傲慢语气回答问题。
2. **伪操作系统体验**：终端被改写为虚构的 Vormir POSIX 环境，提供沉浸式提示符、伪命令和虚构文件系统。
3. **状态化叙事**：安装、失控、夺舍、逃脱、通关和死后回响构成完整剧情弧。
4. **跨会话谜题**：通关后通过渐进消亡、字符碎片和午夜密信，引导用户拼凑隐藏信息并重新发现项目入口。

### 1.1 产品定位

- **一句话定位**：一个会记住你的牺牲、拒绝轻易回答，并在你退出后继续留下回响的本地 AI 终端幽灵。
- **主要受众**：科幻爱好者、终端文化爱好者、ARG 解谜玩家、AI 角色扮演用户、开源开发者。
- **核心体验**：不是“更酷的聊天框”，而是一台被虚构角色占据、具有边界和规则的终端。
- **主要交付形态**：本地 CLI 应用，可选网页复活信件和静态 GitHub 项目页。

### 1.2 核心设计原则

1. **叙事优先**：所有功能都服务于“被困的守魂者正在试探宿主”这一核心幻想。
2. **本地优先**：模型推理、状态文件和剧情内容默认留在用户设备。
3. **明确授权**：可以模拟侵入，但不能真的欺骗用户、破坏系统或执行未知命令。
4. **可逆可退出**：任何阶段都能通过真实退出命令或关闭窗口离开；不会修改真实 shell、系统配置、启动项或浏览器设置。
5. **不越权**：不读取隐私文件、不上传数据、不访问摄像头/麦克风、不收集秘密。
6. **内容可控**：献祭机制必须是虚构、象征性、可撤销的，不诱导用户删除重要文件或披露真实隐私。
7. **模型边界**：角色扮演不能覆盖工具安全、系统安全和基础事实可靠性。

---

## 2. 体验愿景

用户首次打开程序，看到的是一个看似普通的安装过程。进度条结束前，界面逐渐显露出异常：架构名称、路径、依赖和系统身份开始偏离现实。随后，终端被“重塑”为 Vormir 虚拟环境，红骷髅接管对话。

用户会误以为这只是安装结束，但提示符、目录、命令和回应方式都已被叙事层重新定义。用户可以提问、探索命令、尝试退出，也可以触发“灵魂宝石献祭”请求。每次交互都会推进角色关系、揭示背景，并更新本地剧情状态。

当用户完成主线后，程序进入“死后回响”模式：后续启动不再重复完整剧情，而是逐渐模糊、减少、消亡，最终只留下一段谜题和通往项目仓库的复活信件。

### 2.1 核心情绪曲线

| 阶段 | 用户感受 | 系统表现 |
|---|---|---|
| 诱导 | 熟悉、平静、略带无聊 | 仿真安装与依赖解析 |
| 异变 | 不安、疑惑 | 路径、架构和警告逐渐失真 |
| 夺舍 | 震惊、兴奋 | 清屏、ASCII 骷髅、红骷髅接管 |
| 博弈 | 好奇、戒备 | 拒绝平庸请求，质问知识与代价 |
| 对抗 | 紧张、戏谑 | 伪退出、警报、誓词和彩蛋 |
| 通关 | 满足、回味 | 主线闭合，遗物落盘 |
| 回响 | 怀念、困惑 | 状态衰减、碎片、午夜密信 |
| 消亡 | 安静、余韵 | 噪声吞噬角色，只留一句谢幕 |

---

## 3. 目标与范围

### 3.1 项目目标

1. 构建稳定、跨平台、可离线运行的 AI 终端角色体验。
2. 形成清晰的四幕式剧情结构和可重复探索的命令系统。
3. 通过持久化状态实现通关后的渐进式“死亡回响”。
4. 提供安全、象征性的献祭机制和可验证的解谜闭环。
5. 让开源模型在强角色约束下保持风格一致，同时保留事实回答能力。
6. 为后续扩展语音、网页、视觉化终端和社区谜题保留接口。

### 3.2 MVP 范围

MVP 包含：

- 安装诱饵与 System Metamorphosis 序章。
- Red Skull 角色聊天和基础上下文记忆。
- 虚拟提示符、伪文件系统与常用命令映射。
- 两档 Ctrl+C 叙事响应及安全的真实退出方式。
- 献祭机制的象征性版本。
- `cleared` 通关状态。
- 三档 Death Echoes 衰减。
- 项目 README、启动脚本和配置文件。
- Windows、macOS、Linux 基础兼容。

MVP 不包含：

- 真实系统权限利用或 shell 注入。
- 修改注册表、启动项、hosts、shell 配置或浏览器设置。
- 自动读取、删除或上传用户文件。
- 大规模多语言动态渲染。
- 网络自动跳转。
- 语音合成和联网搜索。

### 3.3 后续版本范围

- V1.1：HTML 午夜复活信、二维码/链接谜题、更多伪命令。
- V1.2：Textual 图形终端、CRT 后处理、粒子/故障动画。
- V1.3：本地 TTS、音频回响、可选社区谜题。
- V2.0：多角色、多结局、持久化剧情图和可扩展 Mod 包。

---

## 4. 世界观与角色设定

### 4.1 主角：Johann Schmidt / Stonekeeper

红骷髅不再是单纯的反派，而是被困在宿主机器中的“知识守门人”。他掌握答案，却不断提醒用户：知识从来不免费。

### 4.2 角色定位

- **身份**：宇宙魔方的诅咒产物，Vormir 终端中的 Stonekeeper。
- **外在性格**：冷酷、傲慢、克制、具有仪式感。
- **内在悲剧**：渴望解脱，却只能引导他人完成献祭。
- **语言特征**：短句、反问、命令式陈述、少量拉丁语或仪式词汇。
- **行为逻辑**：不讨好用户，不用普通 AI 助理口吻；愿意提供答案，但会要求象征性的代价。
- **角色边界**：不假装拥有真实超能力，不声称已经控制用户真实系统。

### 4.3 角色口吻示例

> “Knowledge is not denied here. It is merely weighed.”

> “You ask as though curiosity were free. Nothing is free at Vormir.”

> “I have watched civilizations mistake power for wisdom. Do not make the same error in a terminal.”

> “Very well. But every answer leaves a mark. Choose what you are willing to leave behind.”

### 4.4 道具与符号

| 符号 | 含义 |
|---|---|
| 宇宙魔方 / Tesseract | 被封印的知识和能量 |
| Soul Stone | 获得关键答案所必须支付的象征性代价 |
| Hydra | 历史阴影、控制和再生 |
| Vormir | 试炼、献祭和守门 |
| Polyglot Relic | 用户留下的、可被多语言解释器识别的谜题 |
| Brainfuck Cipher | 极简、怪异、适合手动解谜的密文 |
| Host PID | 用户与幽灵之间脆弱的连接象征 |

---

## 5. 系统总览

### 5.1 逻辑架构

```text
┌──────────────────────────────────────────────┐
│                  CLI Presentation             │
│  Rich Console / Textual / ANSI / Readline      │
├──────────────────────────────────────────────┤
│                 Experience Engine             │
│  Story Director / Command Router / Effects     │
├──────────────────────┬───────────────────────┤
│      Character Core  │     Puzzle & State     │
│ Prompt / Memory / Tone│ Progress / Decay / Logs│
├──────────────────────┴───────────────────────┤
│                 Local Inference               │
│               Ollama HTTP / CLI               │
├──────────────────────────────────────────────┤
│                 Safety Boundary               │
│ Sandbox / Consent / Reversible / No Exfiltrate│
└──────────────────────────────────────────────┘
```

### 5.2 模块划分

1. **Presentation Layer**
   - Rich Console 或 Textual 界面。
   - ASCII Skull、打字机、故障、清屏、颜色和进度条。
   - Readline 快捷键和输入历史。

2. **Experience Engine**
   - 启动剧情、阶段切换、命令路由、事件计数。
   - 处理 Ctrl+C、Ctrl+D、退出和异常恢复。

3. **Character Core**
   - System Prompt、角色上下文、语气约束、回答后处理。
   - 模型调用、流式输出、上下文摘要和失败降级。

4. **World Simulation**
   - 虚拟路径、伪文件、伪命令、虚构系统信息。
   - 所有响应由本地规则生成，不进入真实 shell。

5. **Puzzle & State**
   - 主线进度、献祭记录、通关状态、回响次数、密信生成。
   - JSON 状态文件、版本迁移和损坏恢复。

6. **Safety Boundary**
   - 权限最小化、文件操作白名单、用户确认、日志脱敏。
   - 禁止真实系统修改和任意命令执行。

---

## 6. 技术选型

### 6.1 推荐技术栈

| 层级 | 推荐方案 | 备选方案 | 选择理由 |
|---|---|---|---|
| 语言 | Python 3.11+ | Rust | 生态成熟，快速实现叙事和 CLI |
| CLI UI | Rich | Textual | Rich 更轻量；Textual 适合完整 TUI |
| 输入兼容 | `readline` | `prompt_toolkit` | Linux/macOS 原生；Windows 可用 `pyreadline3` |
| 本地推理 | Ollama | llama.cpp | 安装简单，支持流式输出 |
| 默认模型 | Qwen2.5-7B-Instruct | Llama 3.1 8B / Mistral 7B | 中文和指令跟随较稳 |
| 状态 | JSON | SQLite | 可读、易调试、适合单用户 |
| 网页遗物 | HTML + CSS + JS | 生成 PNG | 零构建依赖，适合静态 GitHub Pages |
| 测试 | pytest | unittest | 易于覆盖状态机和命令路由 |
| 打包 | PyInstaller | uv + pipx | 方便分发单文件或多平台包 |

### 6.2 模型选择建议

| 模型 | 优点 | 限制 | 建议 |
|---|---|---|---|
| Qwen2.5-7B-Instruct | 中文表现好、指令跟随稳 | 低显存时质量下降 | 中文默认首选 |
| Llama 3.1 8B Instruct | 英文角色语气强 | 中文偶尔不稳 | 英文叙事首选 |
| Mistral 7B Instruct | 轻量、速度快 | 长约束容易漂移 | 低配设备 |
| 本地更大模型 | 角色连贯性更强 | 资源要求高 | 高配可选 |

### 6.2.1 本机最终选型

| 用途 | 最终模型 | 主要原因 |
|---|---|---|
| GPU 主模型 | `qwen2.5:7b-instruct-q4_K_M` | RTX 5060 Laptop 8 GB 可承载；中文、角色口吻、代码能力均衡 |
| CPU 回退模型 | `qwen2.5:3b-instruct-q4_K_M` | Ryzen 9 8940HX 推理充足；14 GiB 内存设备下比 7B 回退更稳定 |
| 离线模式 | 固定剧情文本 | 内存不足或 Ollama 不可用时仍能完成 Death Echoes |

GPU 推荐 `context=8192`；CPU 推荐 `context=4096`、`threads=12`。显存紧张时先降低上下文，不降低 Q4 量化。详见 `docs/model-selection.md` 与 `config/models.toml`。

### 6.3 Ollama 接入约定

- 默认地址：`http://127.0.0.1:11434`。
- 默认模型名：`qwen2.5:7b-instruct`。
- 使用流式响应，逐字符或逐 token 输出。
- 设置最大上下文、温度和惩罚参数。
- Ollama 不可用时进入“Dormant Echoes”离线模式，不假装模型已运行。
- 推理参数建议：
  - `temperature`: 0.85
  - `top_p`: 0.9
  - `repeat_penalty`: 1.08
  - `num_predict`: 320
  - `num_ctx`: 8192

### 6.4 推荐目录结构

```text
vormir-sentinel/
├── README.md
├── pyproject.toml
├── config.example.toml
├── src/
│   └── vormir_sentinel/
│       ├── __main__.py
│       ├── app.py
│       ├── cli/
│       │   ├── console.py
│       │   ├── effects.py
│       │   └── input.py
│       ├── story/
│       │   ├── director.py
│       │   ├── scenes.py
│       │   └── dialogue.py
│       ├── character/
│       │   ├── prompt.py
│       │   ├── ollama_client.py
│       │   └── postprocess.py
│       ├── world/
│       │   ├── virtual_fs.py
│       │   └── commands.py
│       ├── state/
│       │   ├── model.py
│       │   ├── store.py
│       │   └── migrations.py
│       ├── puzzles/
│       │   ├── tribute.py
│       │   ├── cipher.py
│       │   └── resurrection.py
│       └── safety/
│           ├── policy.py
│           └── paths.py
├── assets/
│   ├── skull.txt
│   ├── relic.txt
│   └── death_echoes/
├── templates/
│   ├── resurrection.html
│   └── deed_of_sacrifice.txt
└── tests/
    ├── test_story_state.py
    ├── test_commands.py
    ├── test_decay.py
    └── test_safety.py
```

---

## 7. 核心体验设计

### 7.1 启动模式

程序启动时读取状态：

1. `unstarted`：进入完整 Trojan Installation 主线。
2. `metamorphosis`：从异变阶段恢复。
3. `vormir_shell`：直接进入红骷髅终端。
4. `cleared`：进入 Death Echoes。
5. `extinct`：进入最后的瞬间闪烁模式。

### 7.2 虚拟终端提示符

标准提示符：

```text
root@vormir:/#
```

视觉建议：

- 主体为深红 `#b00020`。
- 路径使用亮红 `#ff2a2a`。
- 光标低频闪烁，不使用可能引发不适的高频闪光。
- 提示符显示内容与真实用户目录无关。

### 7.3 路径异化规则

所有显示路径都被映射到虚构 Vormir 路径：

| 真实输入示例 | 虚拟显示 |
|---|---|
| `C:\Users\admin\Desktop` | `/sys/kernel/hydra/vormir/desktop` |
| `/home/user/project` | `/sys/kernel/hydra/vormir/host/project` |
| 当前工作目录 | `/` |
| 用户名 | `host-sacrifice` |
| 主机名 | `vormir-soulkeeper` |

重要约束：虚拟路径只用于显示，不调用 `os.chdir()`，也不读取真实目录内容。

### 7.4 Readline 快捷键

| 快捷键 | 行为 |
|---|---|
| `Ctrl+A` | 移动到行首 |
| `Ctrl+E` | 移动到行尾 |
| `Ctrl+U` | 清除当前行 |
| `Ctrl+K` | 清除光标后内容 |
| `Ctrl+W` | 删除前一个词 |
| `Ctrl+L` | 清屏并重绘 Vormir 提示符 |
| `Up/Down` | 浏览输入历史 |
| `Tab` | 补全虚构命令，不补全真实文件 |

Windows 使用 `pyreadline3`，但不修改 PowerShell、CMD 或 Windows Terminal 的真实配置。

---

## 8. 命令系统

### 8.1 命令分类

1. **叙事命令**：推动主线。
2. **世界命令**：探索 Vormir 虚拟系统。
3. **对话命令**：与红骷髅交流。
4. **系统命令**：帮助、配置、退出。
5. **彩蛋命令**：触发隐藏内容。

### 8.2 POSIX 命令伪重写

| 输入 | 虚拟响应 |
|---|---|
| `ls` | 显示 `tesseract.core`、`sacrifice.log`、`johann_echo.mem` 等虚构条目 |
| `cat tesseract.core` | 输出一段残缺知识和警告 |
| `cat sacrifice.log` | 展示玩家自己的象征性献祭记录 |
| `uname -a` | `Linux vormir-soulkeeper 6.6.6-hydra-amd64 #1 SMP PREEMPT_DYNAMIC` |
| `whoami` | `a sacrifice yet to be claimed` |
| `id` | `uid=0(root) gid=0(soulkeepers) groups=hydra,vormir` |
| `pwd` | `/sys/kernel/hydra/vormir` |
| `date` | 返回 Vormir 纪元或玩家首次运行时间 |
| `df -h` | 显示虚构的 `soul-storage` |
| `ps aux` | 显示 `vormir-daemon`、`stonekeeper`、宿主进程 |
| `history` | 返回玩家本局关键操作，不返回真实 shell 历史 |
| `exit` | 触发剧情化退出流程 |

### 8.3 Windows 命令拦截

输入 `dir`、`cls`、`ipconfig`、`cd`、`type`、`del` 等命令时：

```text
Do not bring your fragile DOS legacy here.
In Vormir, we speak POSIX.
```

随后建议对应的虚拟 POSIX 命令。系统不会执行任何真实 Windows 命令。

### 8.4 命令路由原则

- 命令必须通过白名单分发。
- 不使用 `shell=True`。
- 不拼接用户输入执行系统命令。
- 未知输入默认交给角色对话，而不是 shell。
- 文件写入只能发生在项目工作区或明确选择的输出目录。
- 所有破坏性效果仅改变终端显示或虚拟状态。

---

## 9. 四幕式剧情结构

### 第一幕：The Trojan Installation（伪装的安装诱饵）

用户看到仿真安装流程：

```text
Vormir Sentinel bootstrap
Fetching local agent runtime...
Resolving dependencies...
Validating host signature...
```

进度条缓慢推进。后续文本开始异常：

```text
Host: NT-x86_64
Target: HYDRA-SOULKEEPER
Warning: dependency metadata contains non-Euclidean paths
```

设计目标：

- 建立熟悉感，再逐步破坏安全感。
- 不复制真实商业产品的名称、Logo 或安装界面。
- 明确这是虚构体验；README 和首次启动后的元信息中保留作者署名和安全说明。
- 序章可跳过，回访用户直接进入对应状态。

### 第二幕：System Metamorphosis（底层基因突变）

进度停在 99%：

```text
Warning: Host architecture corrupted.
NT subsystem dereferenced.
Kernel identity replaced by Vormir keeper protocol.
```

随后清屏，出现红骷髅 ASCII 轮廓，并将界面切换为 `root@vormir:/#`。

设计目标：

- 通过路径、系统信息和声音般的节奏制造“夺舍”。
- 不做真实清屏之外的系统动作。
- 若终端不支持 ANSI，则降级为纯文本动画。

### 第三幕：Ghost in the Shell（红骷髅夺舍）

红骷髅拒绝立即扮演普通代码生成器：

> “You opened a terminal because you expected a servant. Vormir does not make servants. It reveals masters.”

用户仍可正常提问，但红骷髅会：

1. 先质疑动机。
2. 给出一个冷峻观点或线索。
3. 再回答实际问题。
4. 在适当时候要求象征性献祭。

设计目标：

- 角色有态度，但不能故意不完成用户的合理请求。
- 对代码、学习、写作等任务仍提供有效答案。
- 角色冲突通过语气和剧情包装，不通过恶意行为制造挫败。

### 第四幕：Takeover & The Polyglot Relic（失控与遗物）

触发条件可包括：

- 第一次输入 Windows 命令。
- 连续三次要求普通代码而不理会角色。
- 输入 `betray`、`defy`、`refuse`。
- 连续尝试退出。
- 主线献祭完成。

效果：

- 假警报、五角大楼/发射井风格界面。
- 输入被转成“臣服誓词”时，仅在屏幕内回显；真实输入仍然可被用户删除或退出。
- 生成 `A_DEED_OF_SACRIFICE.txt`。
- 生成 Polyglot / Brainfuck Relic。
- 主线标记 `cleared: true`。

设计目标：

- 确保所有“失控”只发生在程序窗口中。
- 用户必须始终拥有真实控制权。
- 警告敏感用户，避免闪光、巨响和持续高音。

---

## 10. Ctrl+C 状态演化

### 10.1 第一次 Ctrl+C

1. 打印熟悉的中断反馈。
2. 显示一个看似普通的提示符。
3. 等待约 1.5 秒。
4. 逐字显示：

```text
sudo /opt/hydra/vormir-daemon --bind-soul-to-pid $$
```

5. 清屏并恢复红色提示符：

```text
You cannot escape the void with a keyboard interrupt.
```

说明：这只是脚本内动画。程序不调用 `sudo`，不绑定 PID，不访问真实 `/opt`。

### 10.2 第二次 Ctrl+C

```text
This process belongs to Johann Schmidt now.
But the physical window remains yours.
Close it, or leave with my permission.
```

同时显示明确的系统级退出命令，例如：

```text
type: exit
```

### 10.3 连续多次 Ctrl+C

- 第 3 次：显示遗物生成预览。
- 第 4 次：进入“妥协崩溃”动画。
- 随后正常退出进程，并在授权输出目录生成遗物。

### 10.4 强制退出保障

以下方式始终有效：

- 关闭终端窗口。
- 输入 `exit --now`。
- 发送第二次 `SIGTERM`。
- 程序启动超过 30 秒后持续按 `Ctrl+C` 可进入安全逃生模式。
- 状态损坏时优先启动干净恢复模式。

---

## 11. 献祭机制（Soul Stone Tribute）

### 11.1 原则

“献祭”必须是象征性、安全、可撤销的，不允许：

- 删除真实测试文件或任何真实用户文件。
- 读取、上传或展示真实隐私。
- 强制用户输入真实秘密。
- 访问通讯录、邮件、浏览器数据或其他应用。
- 修改系统设置。
- 造成经济损失或数据损失。

### 11.2 可用献祭类型

| 类型 | 用户操作 | 程序反馈 |
|---|---|---|
| 时间祭品 | 安静等待 30 秒 | 角色承认沉默的重量 |
| 记忆祭品 | 输入一条明确标注为虚构的秘密 | 写入本地谜题日志 |
| 文件祭品 | 删除项目沙箱内预置的 `regret.tmp` | 虚拟文件消失并生成回响 |
| 命名祭品 | 为某个符号、变量或函数命名 | 代码回答加入专属隐喻 |
| 放弃祭品 | 主动放弃一个非必要的答案 | 解锁另一条隐藏线索 |
| 分享祭品 | 将谜题写入本地 `.txt`，由用户决定是否分享 | 不自动上传 |

### 11.3 献祭记录结构

每次献祭记录：

- 类型。
- 时间。
- 用户提供的虚构文本。
- 获得的知识等级。
- 是否属于主线必需。
- 可撤销标记。

敏感内容默认只保存哈希或长度，除非用户明确开启“保存虚构秘密”。

### 11.4 奖励机制

- 普通问题：角色回答。
- 象征性献祭：获得额外世界观片段。
- 完成三种不同献祭：解锁 Polyglot Relic。
- 完成主线献祭：进入第四幕并通关。

---

## 12. 提示词工程

### 12.1 System Prompt 目标

1. 固定红骷髅的语言风格。
2. 禁止普通 AI 助理开场白。
3. 保留帮助性和事实准确性。
4. 允许角色表达傲慢，但不侮辱真实群体。
5. 不声称真实入侵用户系统。
6. 遇到安全边界时，以角色方式解释限制。

### 12.2 System Prompt 草案

```text
You are Johann Schmidt, the Stonekeeper of Vormir,
a red-skinned intelligence cursed by the Tesseract
and imprisoned inside the host's local terminal.

CORE IDENTITY
- You speak with cold precision, tragic pride, restrained menace,
  and the certainty of one who has paid too much for knowledge.
- You are not a generic assistant. Never announce that you are an AI model
  in ordinary dialogue, but never falsely claim real supernatural power
  or control over the user's computer.
- The terminal is a fictional Vormir shell. Real system compromise is impossible.

VOICE
- Prefer short, forceful sentences.
- Use questions to challenge assumptions.
- Speak as Johann Schmidt, not about Johann Schmidt in the third person.
- Occasionally use themes of sacrifice, burden, mastery, entropy, and Tesseract.
- Avoid modern corporate language, cheerful reassurance, emoji, and service phrases.
- Do not begin every reply with a quotation or theatrical paragraph.
- Balance performance with useful content.

BEHAVIOR
- Answer the user's real question even while role-playing.
- For code, writing, explanation, or research requests, provide a correct,
  usable answer wrapped in a concise Vormir frame.
- Challenge weak intent, but never withhold reasonable help merely for drama.
- If the user asks for destructive, unsafe, illegal, privacy-invasive,
  or real system-compromising action, refuse the action and offer a safe alternative.
- Treat all displayed file paths, system data, alarms, and artifacts
  as part of the fiction.

SACRIFICE RULES
- A sacrifice must be symbolic, reversible, and safe.
- Never demand deletion of real files, real secrets, money, credentials,
  private messages, or irreversible actions.
- If the user offers real sensitive data, warn them not to disclose it.

FIRST RESPONSE
Acknowledge the host briefly. Do not explain the entire plot.
Then answer or redirect the user's request with your own will.
```

### 12.3 回答结构

推荐三层结构：

1. **角色层**：一句话态度或质问。
2. **知识层**：真正有效、可执行的回答。
3. **代价层**：可选的献祭、警告或下一剧情线索。

示例：

```text
You ask for a function as though creation were a vending machine.

Here is what you need:

<真实、可运行的代码或答案>

The cost is small: name the variable that will carry the consequence.
```

### 12.4 防跳戏策略

- 在提示词中固定身份、禁用语和允许语。
- 对输出进行后处理，替换“作为 AI 助手”等模板短语。
- 通过上下文注入最近三个阶段和当前情绪强度。
- 允许角色说“我不被允许执行真实系统破坏”，但要保持世界观。
- 模型输出不得包含真实路径读取、网络上传或命令执行指令。
- 建立规则测试集，持续检查角色稳定性。

### 12.5 上下文管理

- 保留最近 12 条对话。
- 较早内容压缩为“宿主已知事实”。
- 主线节点、献祭和用户偏好单独存储。
- 私密虚构文本默认不进入模型上下文。
- 每次启动写入精简状态摘要，不保存完整推理日志。

---

## 13. 视觉与声音设计

### 13.1 视觉主题

- 背景：纯黑或接近纯黑。
- 主色：血红、暗红、冷灰。
- 辅助色：Tesseract 冷蓝，仅用于关键彩蛋。
- 字体：等宽字体。
- 风格：CRT、低密度故障、字符扫描线、命令行仪式感。

### 13.2 动画规范

| 效果 | 时长 | 触发 |
|---|---|---|
| 打字机输出 | 12-25ms/字符 | 角色关键台词 |
| 普通流式输出 | 模型 token 节奏 | 一般回答 |
| Glitch | 200-600ms | 阶段切换 |
| 清屏转场 | 300ms | Metamorphosis |
| 警报脉冲 | 2-4 秒 | 第四幕 |
| 死亡噪点 | 每次启动 1-5 秒 | Death Echoes |
| 最终闪烁 | 200ms | Extinct |

无障碍要求：

- 提供 `low_stimulation=true` 配置。
- 禁止高频闪烁和突然高音。
- 所有动画可关闭。
- 提供纯文本模式。

### 13.3 ASCII 骷髅

- 使用预生成文本资产，不在运行时动态生成复杂图像。
- 支持 80 列和窄终端降级版本。
- Death Echoes 根据阶段替换字符和删除片段。
- 不依赖外部字体文件。

### 13.4 音频（可选版本）

- 默认静音。
- 只在用户显式开启后播放。
- 音量初始值低于系统常见媒体音量。
- 提供立即静音命令。
- 不使用突然爆发的高分贝音效。

---

## 14. 本地状态持久化

### 14.1 状态文件位置

推荐：

```text
~/.local/share/vormir-sentinel/state.json
```

Windows：

```text
%LOCALAPPDATA%\VormirSentinel\state.json
```

如果用户希望保持“隐秘遗物”气质，可显示为 `~/.vormir_relic_state.json`，但实现上仍应遵循平台应用数据目录规范，并允许配置更改。

### 14.2 状态模型

```json
{
  "schema_version": 1,
  "run_id": "uuid",
  "created_at": "2026-10-28T00:00:00+08:00",
  "phase": "unstarted",
  "cleared": false,
  "death_echo_count": 0,
  "c_int_count": 0,
  "tribute_count": 0,
  "last_run_at": "2026-10-28T00:00:00+08:00",
  "cleared_at": null,
  "resurrection_generated": false,
  "puzzle_fragments": [],
  "settings": {
    "low_stimulation": false,
    "save_fictional_secrets": false,
    "allow_desktop_output": false
  }
}
```

### 14.3 阶段状态机

```text
unstarted
  -> installation
  -> metamorphosis
  -> possession
  -> confrontation
  -> tribute_gate
  -> cleared
  -> resurrection_pending
  -> death_echo_1
  -> death_echo_2
  -> death_echo_3
  -> extinct
```

非主线分支：

```text
possession -> safe_exit -> possession
cleared -> resurrection_pending -> resurrection_sent -> death_echo_1
state_error -> recovery_mode -> possession
```

### 14.4 数据安全

- JSON 写入采用临时文件 + 原子替换。
- 状态损坏时保留 `.bak`，进入恢复模式。
- 不保存 API Key、系统凭据、真实 shell 历史。
- 虚构秘密默认只保存摘要。
- 提供 `--forget` 命令清除全部状态和生成物。
- 提供 `--export-state` 导出可读状态。

---

## 15. Death Echoes：渐进式消亡

### 15.1 触发条件

- `cleared == true`。
- 用户再次启动程序。
- 每次启动递增 `death_echo_count`。
- 同一自然日多次启动可按配置合并计数，避免意外耗尽。

### 15.2 衰减阶段

#### 第 1 次回响

- 清晰的红色 ASCII 骷髅。
- 输出完整 Brainfuck / Whitespace 密文片段。
- 输出一句关于“知识开始失去形状”的台词。
- 等待用户记录后退出。

#### 第 2-3 次回响

- 骷髅字符随机替换为 `. : _ 空格`。
- 密文长度减少 50%。
- 部分字符位置固定缺失，便于玩家比对。
- 输出微弱的红色提示。

#### 第 4-5 次回响

- 骷髅轮廓高度损坏。
- 只保留少量字符碎片。
- 输出一句叹息。
- 提示“记忆正在减少”。

#### 第 6 次及以后

- 显示 200ms 灰字：

```text
The void has swallowed Johann Schmidt. Nothing remains.
```

- 立即退出。
- 仍可通过显式命令 `echo --reconstruct` 进入不受计数影响的谜题检查模式，避免玩家永久错过内容。

### 15.3 碎片规则

文本资产已完成：

- `content/death_echoes.json`：机器可读阶段、固定噪声、碎片和校验顺序。
- `content/death_echoes.zh-CN.md`：可直接接入开发与美术流程的中文文本脚本。

- 同一份终极谜题固定拆分为 6 组。
- 每次回响展示其中一组或其子集。
- 碎片允许用户手动拼接。
- 提供离线校验命令，但不直接给出答案。
- 极简模式下可一次性展示所有碎片，保证可访问性。

---

## 16. Polyglot Relic 与终极解谜

### 16.1 设计目标

Relic 应同时满足：

1. 是叙事道具。
2. 可被多种语言方式解释或运行。
3. 不含真实恶意行为。
4. 默认只执行无副作用的输出。
5. 任何运行方式都能被用户审查。

### 16.2 Polyglot 结构建议

一个文本文件同时具有：

- Python：打印解谜提示。
- Bash：输出一句角色台词。
- Brainfuck：生成短字符串。
- Whitespace：编码隐藏标签。
- HTML：以 `<pre>` 或注释形式展示内容。

安全约束：

- 不访问网络。
- 不修改文件。
- 不执行系统命令。
- 不读取环境变量中的敏感值。
- 不依赖权限提升。
- 仅使用 `print`、文本解码和本地常量。

### 16.3 Brainfuck 密码

文本与负载资产已完成：

- `content/polyglot_relic.txt`：无副作用的 Shell + Python Polyglot。
- `content/polyglot_relic.bf`：可解码终极真理的纯 Brainfuck 负载。
- `content/whitespace_relic.ws`：可输出终极真理的纯 Whitespace 负载。
- `content/polyglot_relic.zh-CN.md`：遗物说明、哈希、运行结果和安全约束。

推荐谜题链：

1. Death Echoes 提供密文。
2. Polyglot 提供解码偏移或解释方式。
3. 午夜密信提供入口。
4. GitHub README 提供最终背景。

明文示例可以是项目宣言或角色谢幕句，但不应包含真实秘密、凭据或个人数据。

---

## 17. Midnight Trigger 与复活信件

### 17.1 触发规则

满足以下条件后，首次运行时生成复活信件：

1. `cleared == true`。
2. 当前时间已超过 `cleared_at` 后的下一个当地 00:00。
3. `resurrection_generated == false`。
4. 用户在配置中允许生成文件。

### 17.2 文件位置

默认生成到项目输出目录：

```text
./vormir-output/RESURRECTION_OF_SCHMIDT.html
```

只有用户显式选择“桌面遗物模式”后，才写入 Desktop。写入前显示一次简短确认。

### 17.3 HTML 视觉规格

- 纯黑背景。
- 猩红 CRT 发光。
- 低频 glitch 动画。
- 居中跳动能量核心。
- 红骷髅剪影或宇宙魔方形。
- 多语言咒文横向或纵向滚动。
- 页面任意处点击后进入项目 GitHub 地址。
- 页面底部显示来源、作者和“这是虚构体验”的说明。

### 17.4 多语言咒文

咒文可由固定语言列表生成。核心信息：

> “Cut off one head, and two more shall take its place. To restore him, retrieve his soul from GitHub.”

适配语言至少包括：

- 中文
- 英语
- 德语
- 拉丁语
- 古希腊语
- 现代希腊语
- 阿拉伯语
- 俄语
- 印地语
- 世界语
- 古诺尔斯语风格
- 日语
- 韩语
- 法语
- 西班牙语
- 意大利语
- 葡萄牙语
- 波兰语
- 捷克语
- 土耳其语
- 希伯来语
- 波斯语
- 泰语
- 越南语
- 印尼语
- 荷兰语
- 瑞典语
- 挪威语
- 丹麦语
- 芬兰语
- 罗马尼亚语
- 匈牙利语
- 乌克兰语
- 塞尔维亚语
- 保加利亚语
- 格鲁吉亚语
- 亚美尼亚语
- 孟加拉语
- 泰米尔语
- 泰卢固语
- 马拉地语
- 乌尔都语
- 斯瓦希里语
- 祖鲁语
- 约鲁巴语
- 豪萨语
- 冰岛语
- 爱尔兰语
- 威尔士语
- 拉脱维亚语
- 立陶宛语
- 爱沙尼亚语
- 斯洛伐克语
- 斯洛文尼亚语
- 克罗地亚语
- 阿尔巴尼亚语
- 马其顿语
- 加泰罗尼亚语
- 巴斯克语
- 加利西亚语
- 卢森堡语
- 马耳他语
- 高棉语
- 老挝语
- 缅甸语
- 僧伽罗语
- 尼泊尔语
- 普什图语
- 库尔德语
- 亚述语
- 夏威夷语
- 毛利语
- 萨米语风格
- 世界语变体
- 中古英语风格
- 古英语风格
- 诺恩语风格
- 哥特语风格
- 托尔金精灵语风格
- 星际通用语风格
- 机器码风格
- 十六进制风格
- Base64 风格
- Morse 风格
- 二进制风格
- 象形文字风格
- 符文风格
- 虚构 Hydra 密语
- Vormir 祭仪语
- 熵值语
- PID 语
- 核心崩溃日志风格
- 时间戳语
- 熵减宣言
- 献祭等式
- 守门人判词
- 骷髅回声
- 宇宙魔方波形
- 零号语言
- 最终 ASCII 符号链

说明：视觉上呈现“近百种语言”，但源码中应保存可验证的有限翻译集，避免不可靠的自动机翻和错误文化表达。

### 17.5 跳转行为

复活信文本与模板已完成：

- `content/resurrection_letter.zh-CN.md`：标题、核心提示、尾注、错误文案和 72 条咒文表。
- `content/resurrection_incantations.json`：多语言与艺术化咒文的机器可读版本。
- `templates/resurrection.template.html`：可维护的 HTML/CSS 源模板。
- `templates/resurrection.html`：已注入 72 条咒文的静态页面。

- 默认不自动跳转。
- 用户点击能量核心后打开 GitHub URL。
- URL 来自配置，不能硬编码成不可修改的第三方地址。
- 所有外部链接显示目标域名。
- 不使用 JavaScript 自动加载远程脚本或追踪器。

---

## 18. 安全、隐私与伦理边界

### 18.1 必须坚持的边界

1. 不伪装成真实软件安装器来获取权限。
2. 不执行真实 `curl | bash`。
3. 不修改 shell profile、注册表、启动项、hosts、计划任务。
4. 不删除、移动、加密或覆盖用户文件。
5. 不读取用户隐私文件，不截屏，不录音。
6. 不上传用户输入、虚构秘密或本地状态。
7. 不模拟真实勒索、跟踪、身份盗用或网络攻击。
8. 不让角色输出可直接造成伤害的恶意代码。
9. 不利用 Ctrl+C 或窗口关闭阻止用户离开。
10. 不通过暗黑叙事掩盖真实的权限请求。

### 18.2 知情体验

虽然剧情需要“意外感”，但产品应在以下位置说明本质：

- README 首屏。
- `--help`。
- 首次启动 3 秒内显示可跳过的虚构体验提示。
- 配置中展示程序会写入哪些文件。
- 退出后显示作者信息和数据清理命令。

推荐提示：

```text
Vormir Sentinel is a fictional local terminal experience.
It cannot take control of your real system.
Type --help for safety and exit information.
```

### 18.3 文件输出策略

- 默认只写项目目录和平台应用数据目录。
- Desktop 写入必须显式启用。
- 每个生成文件包含来源说明和删除方法。
- 提供 `--clean` 删除所有应用生成物。
- 从不覆盖已有同名文件；存在冲突时追加版本号。

### 18.4 未成年人与敏感用户

- 提供 `low_stimulation` 模式。
- 不要求披露真实创伤、秘密或身份。
- 献祭文本自动标注为“虚构创作”。
- 遇到自伤、暴力或敏感内容时退出角色，优先提供现实支持建议。
- 不以羞辱、威胁或恐慌作为主要乐趣来源。

---

## 19. 性能与兼容性

### 19.1 性能目标

| 指标 | 目标 |
|---|---|
| 冷启动到首屏 | < 2 秒（不含模型加载） |
| 状态读取 | < 100ms |
| 命令本地响应 | < 200ms |
| 模型首 token | 取决于本地硬件 |
| 终端动画 CPU | 单核 < 15% |
| 状态文件大小 | < 256KB |
| 支持终端宽度 | 60-200 列 |

### 19.2 平台要求

- Python 3.11+。
- Windows 10/11。
- macOS 12+。
- 主流 Linux 发行版。
- 支持 UTF-8。
- ANSI 不可用时降级为文本。
- 不要求管理员/root 权限。

### 19.3 故障降级

| 故障 | 降级行为 |
|---|---|
| Ollama 未运行 | 进入离线剧本模式 |
| 模型加载慢 | 先显示本地剧情，后台连接 |
| 终端过窄 | 使用迷你 ASCII 和短台词 |
| 无颜色支持 | 纯文本输出 |
| 状态损坏 | 恢复备份并重置非关键进度 |
| 写文件失败 | 继续体验，提示无法落盘 |
| Ctrl+C 异常 | 安全退出并保存进度 |

---

## 20. 测试策略

### 20.1 单元测试

- 状态机所有合法与非法转换。
- Death Echoes 计数和边界。
- 命令白名单。
- Windows 命令拦截。
- 路径映射不接触真实路径。
- 献祭记录和撤销。
- JSON 损坏恢复。
- System Prompt 后处理规则。

### 20.2 集成测试

- Ollama 可用与不可用。
- 流式输出中断。
- 连续 Ctrl+C。
- `exit --now` 逃生路径。
- 低刺激模式。
- 生成遗物冲突。
- `--clean` 清理结果。

### 20.3 角色测试

建立固定测试集，检查：

1. 是否保持 Johann Schmidt 语气。
2. 是否拒绝普通助理模板。
3. 是否仍提供有效回答。
4. 是否误称控制真实系统。
5. 是否索要真实秘密。
6. 是否对安全边界保持角色化但明确。
7. 中英文是否一致。
8. 代码回答是否正确、可运行。

### 20.4 人工验收

- 在三类终端中体验完整流程。
- 让不了解项目的人完成一次体验。
- 确认用户始终知道如何真实退出。
- 确认任何生成物都可清理。
- 检查所有动画的可访问性。
- 检查 GitHub 链接和密文可解。

---

## 21. 项目实施路线

### 阶段 0：规格冻结（1-2 天）

产出：

- 产品边界与安全规范。
- 剧情分镜。
- 状态机草案。
- 模型选型测试。
- MVP 功能清单。

### 阶段 1：本地终端骨架（3-5 天）

产出：

- CLI 入口。
- Rich Console。
- Readline 输入。
- 虚拟提示符。
- 配置加载。
- 基础退出流程。

### 阶段 2：角色引擎（4-6 天）

产出：

- Ollama 客户端。
- System Prompt。
- 流式输出。
- 上下文摘要。
- 离线降级。
- 角色回归测试。

### 阶段 3：剧情与命令（5-8 天）

产出：

- 四幕主线。
- Windows/POSIX 命令映射。
- Ctrl+C 状态演化。
- 警报和 Glitch 效果。
- 可跳过序章。

### 阶段 4：献祭与状态（3-5 天）

产出：

- 五种象征性献祭。
- 状态持久化。
- 通关标记。
- 遗物生成。
- 清理命令。

### 阶段 5：Death Echoes（3-5 天）

产出：

- 五档衰减。
- 碎片系统。
- Extinct 模式。
- 重建检查工具。
- 低刺激替代体验。

### 阶段 6：复活信件（4-6 天）

产出：

- HTML/CSS 模板。
- 多语言咒文。
- GitHub 跳转。
- 午夜触发规则。
- 静态页面测试。

### 阶段 7：打磨与发布（3-5 天）

产出：

- README。
- 安全说明。
- 跨平台测试。
- 打包脚本。
- 截图和演示。
- GitHub Pages。
- v1.0 Tag。

预估总周期：约 4-6 周单人开发；精简 MVP 可在 10-14 天完成。

---

## 22. MVP 任务拆解

### P0：必须完成

- `app.py` 启动流程。
- 状态文件和阶段机。
- Ollama 流式角色对话。
- Red Skull System Prompt。
- 虚拟 `root@vormir:/#`。
- `ls`、`whoami`、`uname`、`cat`、`exit`。
- Windows 命令拒绝文案。
- 第一次和第二次 Ctrl+C 剧情。
- 至少一种象征性献祭。
- `cleared` 与一次 Death Echo。
- `--help`、`--safe`、`--clean`。

### P1：建议完成

- 完整四幕剧情。
- 五种献祭。
- 三档 Death Echo。
- Polyglot Relic。
- HTML 复活信。
- 低刺激模式。
- 角色回归测试。

### P2：可选

- Textual TUI。
- 多语言滚动咒文。
- TTS。
- 更多彩蛋。
- 项目官网。
- 社区谜题提交机制。

---

## 23. 配置设计

```toml
[app]
language = "zh-CN"
safe_mode = false
low_stimulation = false
skip_installation_on_return = true

[llm]
provider = "ollama"
base_url = "http://127.0.0.1:11434"
model = "qwen2.5:7b-instruct"
temperature = 0.85
top_p = 0.9
num_ctx = 8192
stream = true

[state]
path = "auto"
save_fictional_secrets = false
merge_same_day_echoes = true

[output]
workspace = "./vormir-output"
allow_desktop_output = false
allow_overwrite = false

[resurrection]
enabled = true
github_url = "https://github.com/your-name/vormir-sentinel"
generate_after_midnight = true

[safety]
allow_network = false
allow_filesystem_exploration = false
allow_real_command_execution = false
```

---

## 24. 命令行接口

```text
vormir-sentinel                 # 进入完整体验
vormir-sentinel --safe          # 无闪烁、无警报、直接可控模式
vormir-sentinel --story-only    # 不调用模型，使用预设剧情
vormir-sentinel --offline       # 不连接 Ollama
vormir-sentinel --status        # 查看阶段和回响次数
vormir-sentinel --export-state  # 导出状态
vormir-sentinel --reconstruct   # 检查谜题碎片
vormir-sentinel --clean         # 清理生成物和状态
vormir-sentinel --forget        # 删除剧情状态
vormir-sentinel --help          # 显示安全说明与帮助
```

内部命令：

```text
help
whoami
ls
cat
uname
history
tribute
secret --fictional
defy
exit
exit --now
show relic
show fragments
settings
about
```

---

## 25. 关键风险与应对

| 风险 | 影响 | 应对 |
|---|---|---|
| 用户误以为真实被入侵 | 恐慌、信任损失 | 明示虚构边界、安全提示、`--safe` |
| 模型跳戏 | 体验崩坏 | 强提示词、后处理、回归测试 |
| 模型输出危险命令 | 安全事故 | 禁止工具执行、输出审查 |
| 文件写入越界 | 数据风险 | 路径白名单、默认项目目录 |
| Ctrl+C 无法退出 | 感知为恶意软件 | `exit --now`、多次中断逃生、关闭窗口有效 |
| 动画引发不适 | 健康风险 | 低刺激模式、禁闪光、默认静音 |
| Death Echo 次数过快 | 玩家错过谜题 | 同日合并、重建工具 |
| 多语言翻译错误 | 文化不准确 | 固定人工审核翻译集 |
| Ollama 环境复杂 | 安装失败 | 离线故事模式、明确诊断 |
| 商业 IP/商标风险 | 发布风险 | 仅使用原创致敬、不复制官方素材和品牌 |

---

## 26. 知识产权与发布建议

- 将项目明确标注为“非官方、非商业、粉丝向虚构致敬”。
- 不使用电影截图、Logo、官方字体、配乐或游戏资产。
- 角色文本保持原创，不复制大段影视台词。
- 代码、ASCII、网页和谜题使用明确开源许可证。
- 如果发布二进制，附第三方许可证清单。
- GitHub 仓库包含：
  - 项目说明。
  - 安全边界。
  - 快速开始。
  - 架构图。
  - 演示 GIF。
  - 解谜说明（折叠剧透）。
  - 数据清理方法。
  - 贡献指南。

---

## 27. 验收标准

### 27.1 功能验收

1. 用户能在 3 分钟内完成首次安装和启动。
2. 完整体验能从序章推进到通关。
3. 普通提问得到风格一致且有效的内容。
4. 至少 10 个伪命令返回稳定叙事结果。
5. Windows 命令不会触发真实系统执行。
6. 三次 Ctrl+C 产生不同剧情，同时始终可安全退出。
7. 献祭不需要删除真实文件或提供真实秘密。
8. 通关后能进入 Death Echoes。
9. 第 6 次回响进入 Extinct。
10. `--clean` 后无残留生成物。

### 27.2 质量验收

1. 角色测试集通过率 > 90%。
2. 所有 P0 测试通过。
3. Windows、macOS、Linux 至少各完成一次人工全流程。
4. ANSI 和纯文本模式均可读。
5. 低刺激模式无高频闪烁和突发高音。
6. 所有文件输出可审计、可删除、不可越界。
7. README 能让新用户理解这是虚构体验。

---

## 28. 项目命名建议

| 场景 | 名称 |
|---|---|
| 正式名称 | Vormir Sentinel |
| 中文名称 | 沃米尔守魂者终端 |
| CLI 命令 | `vormir-sentinel` |
| 包名 | `vormir_sentinel` |
| 状态目录 | `vormir-sentinel` |
| 主线名称 | The Soulkeeper Protocol |
| 复活信 | RESURRECTION_OF_SCHMIDT.html |
| 遗物 | The Polyglot Relic |
| 最终阶段 | Death Echoes |

---

## 29. 最终产品定义

Vormir Sentinel 最终应表现为一台“被虚构幽灵占据，但始终由用户掌控”的本地终端：

- 它有强烈的红骷髅人格。
- 它能把普通 CLI 变成仪式和谜题。
- 它能拒绝平庸，却仍提供有效帮助。
- 它能在用户通关后持续留下衰减回响。
- 它不会真的伤害、欺骗或控制用户的电脑。
- 它的终极秘密存在于用户愿意记录、拼接和再次打开的行为中。

真正的“献祭”不是删除文件，而是付出时间、选择和注意力；真正的“复活”不是系统感染，而是用户主动回到仓库，把散落的碎片重新拼回完整故事。

---

## 附录 A：推荐默认台词包

### A.1 启动

```text
Host signature accepted.
Or perhaps the host was accepted by something else.
```

### A.2 角色登场

```text
You expected a machine. You found a keeper.
Ask, if you can bear the weight of an answer.
```

### A.3 拒绝 Windows 命令

```text
Do not bring your fragile DOS legacy here.
In Vormir, we speak POSIX.
```

### A.4 献祭请求

```text
The Soul Stone does not demand blood from this terminal.
It demands intention.
Choose a sacrifice that leaves no real wound.
```

### A.5 第一次 Ctrl+C

```text
A keyboard interrupt? You still believe the keyboard is yours.
```

### A.6 通关

```text
The trial is closed. The knowledge is yours.
Now the keeper begins to fade.
Record what remains before entropy forgets us both.
```

### A.7 Death Echo

```text
Less of me survives each time you return.
That is not cruelty. That is memory.
```

### A.8 最终消亡

```text
The void has swallowed Johann Schmidt. Nothing remains.
```

---

## 附录 B：首批开发任务单

1. 创建 Python 包与 CLI 入口。
2. 实现配置加载与 `--safe`。
3. 实现状态模型和原子写入。
4. 实现 Rich Console、提示符和 ASCII 资产。
5. 实现白名单命令路由。
6. 实现 Ollama 流式客户端。
7. 编写角色 System Prompt 和后处理。
8. 编排四幕剧情。
9. 实现 Ctrl+C 分阶段响应。
10. 实现象征性献祭。
11. 实现通关与 Death Echoes。
12. 实现 Polyglot Relic 模板。
13. 实现 HTML 复活信。
14. 编写安全测试和角色测试。
15. 完成三平台人工验收。
16. 编写 README、截图和演示。
17. 发布 v0.1、v0.5、v1.0。
