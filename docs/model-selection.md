# 本机 GPU / CPU 模型选型

## 1. 当前硬件结论

| 项目 | 当前设备 | 选型影响 |
|---|---|---|
| GPU | NVIDIA GeForce RTX 5060 Laptop GPU，8 GB VRAM，Compute Capability 12.0 | 适合 7B～8B Q4 模型；必须使用支持 Blackwell / sm_120 的 Ollama 与 CUDA 运行时 |
| CPU | AMD Ryzen 9 8940HX，16 核 32 线程，最高约 5.4 GHz | CPU 推理能力很强，但内存容量会成为主要限制 |
| 内存 | 约 14 GiB；本次检查可用约 4.9 GiB，Swap 已使用约 6.9 GiB | CPU 回退模型不宜直接上 7B，3B Q4 更稳定 |
| Ollama | Server 0.33.1，CLI 0.30.9 | 客户端和服务端版本不一致，正式测试前应统一版本 |
| 已安装模型 | `deepseek-r1:7b`、`deepseek-coder:6.7b`、两个 embedding 模型 | embedding 模型不能作为对话模型；当前缺少合适的中文通用 3B/7B Instruct 模型 |

## 2. 最终选择

### GPU 主模型

**选择：`qwen2.5:7b-instruct-q4_K_M`，Ollama 可使用标签 `qwen2.5:7b-instruct-q4_K_M`。**

选择理由：

- 8 GB VRAM 足以承载 7B Q4 权重和中等上下文。
- 中文指令跟随和角色口吻稳定性优于同规模 Llama/Mistral。
- 适合红骷髅的短句、反问、冷酷表达。
- 可以兼顾角色扮演、解释和代码生成。
- 全部本地运行，不依赖闭源 API。

推荐参数：

```text
context       8192
temperature   0.85
top_p         0.90
repeat_penalty 1.08
num_predict   320
num_gpu       999
```

若显存溢出或桌面环境占用较高，将上下文降至 `4096`，不要首先降低模型量化。

### CPU 回退模型

**选择：`qwen2.5:3b-instruct-q4_K_M`，Ollama 可使用标签 `qwen2.5:3b-instruct-q4_K_M`。**

选择理由：

- Q4 权重较小，当前 14 GiB 内存设备可在 GPU 不可用时保持响应。
- Ryzen 9 8940HX 的 16 个物理核心对 3B Q4 推理足够。
- 仍保持较好的中文和角色一致性。
- 比 7B CPU 回退更不容易触发 Swap，也更适合 Death Echoes 的短文本。
- 可以在无 GPU、驱动异常或显存不足时继续提供基础体验。

推荐参数：

```text
context       4096
temperature   0.82
top_p         0.90
repeat_penalty 1.10
num_predict   220
threads       12
```

不要把 32 个逻辑线程全部分配给推理；建议 8-12 线程，预留桌面和 Ollama 服务资源。

## 3. 现有本地模型的应急策略

| 模型 | 可用性 | 用途 |
|---|---|---|
| `deepseek-r1:7b` | 可作为临时 GPU 对话模型 | 推理和代码问题；需要后处理隐藏思考标签，角色口吻弱于 Qwen |
| `deepseek-coder:6.7b` | 可作为代码专用后备 | 只处理代码，不作为主要角色模型 |
| `qwen3-embedding:4b` | 不可作为对话模型 | 文本向量 |
| `batiai/qwen3-embedding:8b` | 不可作为对话模型 | 文本向量，且体积过大 |

如果暂时不能拉取 Qwen：

1. GPU 模式临时使用 `deepseek-r1:7b`。
2. CPU 模式启用纯离线剧本，而不是加载 7B 模型进入 Swap。
3. 正式发布前安装 Qwen GPU/CPU 双配置并完成角色回归测试。

## 4. 部署建议

```text
GPU_MODE=qwen2.5:7b-instruct-q4_K_M
CPU_MODE=qwen2.5:3b-instruct-q4_K_M
OLLAMA_MAX_LOADED_MODELS=1
```

启动逻辑：

1. 检测 NVIDIA GPU 和可用显存。
2. 显存可用量大于 6.5 GiB 时加载 GPU 模型。
3. GPU 不可用、驱动不兼容或模型加载失败时加载 CPU 3B。
4. 内存可用量低于 2.5 GiB 时直接进入离线故事模式。
5. Ollama 客户端/服务端版本不一致时显示诊断，但不阻断安全模式。

## 5. M2 运行时实现

当前 CLI 已实现以下选择与降级行为：

- `--mode auto`：读取 `/proc/meminfo`、Windows `GlobalMemoryStatusEx` 或 POSIX 可用内存估算，不执行 `nvidia-smi`、`sysctl` 或其他宿主机诊断命令。
- 可用内存低于 `2.5 GiB` 时进入固定离线故事模式。
- 内存充足时优先尝试 `gpu_primary`，并保留 `gpu_emergency`；GPU 档案请求失败且尚未输出内容时自动重试 CPU 档案。
- `--mode gpu` 与 `--mode cpu` 是显式优先级，不绕过安全边界。
- Ollama `/api/tags` 用于确认已安装模型；模型缺失时直接降级到离线角色，不会伪造回答。
- Ollama 请求只允许 `127.0.0.1`、`localhost` 或 `::1`，并禁用代理与重定向。
- `--safe` 和 `--offline` 完全禁用本地推理，不建立任何 Ollama 连接。

当前机器如果尚未安装 Qwen 2.5 GPU/CPU 档案，`--mode gpu` 可使用已有的 `gpu_emergency` DeepSeek 档案；正式发布前仍应安装 Qwen 双档案并完成中文角色回归。
