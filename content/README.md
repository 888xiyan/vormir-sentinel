# Vormir Sentinel 内容资产

本目录保存第 15、16、17 章的可直接接入文本和谜题资产。

| 资产 | 章节 | 说明 |
|---|---|---|
| `death_echoes.json` | 15 | Death Echoes 阶段、固定噪声、碎片和最终真理 |
| `death_echoes.zh-CN.md` | 15 | 可直接交给开发和美术的中文文本脚本 |
| `polyglot_relic.txt` | 16 | 可由 Bash 和 Python 运行的无副作用 Polyglot |
| `polyglot_relic.bf` | 16 | 可解码最终真理的纯 Brainfuck 负载 |
| `whitespace_relic.ws` | 16 | 输出最终真理的纯 Whitespace 负载 |
| `polyglot_relic.zh-CN.md` | 16 | 遗物说明、哈希、解谜顺序和安全约束 |
| `resurrection_incantations.json` | 17 | 72 条多语言与艺术化滚动咒文 |
| `resurrection_letter.zh-CN.md` | 17 | 复活信标题、正文、尾注、触发文案和完整咒文表 |

运行时模板位于 `templates/resurrection.html`。

安全约定：所有谜题负载只能输出固定字符串，不得读取文件、访问网络、执行系统命令或修改环境。
