# 第 16 章文本包：The Polyglot Relic

## 遗物文本

```text
THE GHOST LIVES WHERE THE CODE IS OPEN.
RETURN TO THE SOURCE.
```

最终真理：

```text
RETURN TO THE SOURCE. THE GHOST LIVES WHERE THE CODE IS OPEN.
```

## 文件构成

| 文件 | 格式 | 作用 |
|---|---|---|
| `content/polyglot_relic.txt` | Shell + Python polyglot | 可审查、无副作用的多解释器遗物 |
| `content/polyglot_relic.bf` | Brainfuck | 解码最终真理 |
| `content/whitespace_relic.ws` | Whitespace | 输出最终真理并结束 |
| `content/death_echoes.json` | JSON | 管理衰减阶段、碎片与校验顺序 |

## SHA-256

```text
polyglot_relic.bf   75d4d7b9b72247f3cd70fd6061e51487b8a24df21392eddac35433a699e85b51
whitespace_relic.ws afe30489f34625afe288a60ccd98cb83ef1bae397490bf9b9a2066e525daa611
```

## 运行结果

`python3 content/polyglot_relic.txt` 输出：

```text
RETURN TO THE SOURCE.
```

`bash content/polyglot_relic.txt` 输出：

```text
THE GHOST LIVES WHERE THE CODE IS OPEN.
```

## 安全约束

- 不读取或写入用户文件。
- 不访问网络，不执行系统命令。
- 不读取敏感环境变量，不请求权限提升。
- 所有负载只输出固定字符串。

## 解谜顺序

1. 从 Death Echoes 记录 `F01` 至 `F05`。
2. 用 CHECKSUM 验证顺序。
3. 从 Polyglot Relic 找到 `source/open` 线索。
4. 运行或人工解码 Brainfuck / Whitespace。
5. 打开复活信件，前往 GitHub 仓库补完故事。

答案不是入侵电脑，而是回到开放的源头。
