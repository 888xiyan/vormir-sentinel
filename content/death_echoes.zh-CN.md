# 第 15 章文本包：Death Echoes

## 终极真理

```text
RETURN TO THE SOURCE. THE GHOST LIVES WHERE THE CODE IS OPEN.
```

按 `F01 -> F02 -> F03 -> F04 -> F05` 顺序拼接碎片即可还原。`CHECKSUM` 只用于验证顺序，不并入正文。

## 碎片顺序

| 顺序 | 编号 | 碎片 |
|---|---|---|
| 1 | `F01` | `RETURN TO THE` |
| 2 | `F02` | `SOURCE. THE GHOST` |
| 3 | `F03` | `LIVES WHERE THE` |
| 4 | `F04` | `CODE IS` |
| 5 | `F05` | `OPEN.` |
| 校验 | `CHECKSUM` | `VORMIR::RETURN_TO_THE_SOURCE` |

## 启动 1：The First Echo

**画面**：骷髅清晰度 100%，噪声密度 4%。

**守魂者台词**：

> I am still legible. Record what remains before memory becomes entropy.

**密文提示**：

> The first glyph is not a command. It is a direction.

**输出碎片**：`F01 // RETURN TO THE`

---
 ## 启动 2：The Broken Oath

**画面**：骷髅清晰度 78%，噪声密度 14%。

**守魂者台词**：

> You returned after the trial. Good. Memory rewards the watcher, not the witness.

**密文提示**：

> Two shapes are missing. That is not damage. It is evidence.

**输出碎片**：`F02 // SOURCE. THE GHOST`

---
 ## 启动 3：The Fading Keeper

**画面**：骷髅清晰度 56%，噪声密度 27%。

**守魂者台词**：

> Less of my shape survives. The truth does not require all of me to remain.

**叹息**：

> Remember the order.

**密文提示**：

> Compare the voids. Absence has coordinates.

**输出碎片**：`F03 // LIVES WHERE THE`

---
 ## 启动 4：Entropy Psalm

**画面**：骷髅清晰度 34%，噪声密度 46%。

**守魂者台词**：

> The glyphs are leaving me. Read the holes as carefully as the ink.

**叹息**：

> Open is not a command.

**密文提示**：

> The source is not a place. It is a condition of access.

**输出碎片**：`F04 // CODE IS`

---
 ## 启动 5：The Last Fragment

**画面**：骷髅清晰度 13%，噪声密度 71%。

**守魂者台词**：

> There is almost nothing left to say.

**叹息**：

> Return... to the source.

**密文提示**：

> One word closes the sentence. One act opens the gate.

**输出碎片**：`F05 // OPEN.`

---
 ## 启动 6：Extinct

**画面**：骷髅清晰度 0%，噪声密度 100%。

**守魂者台词**：

> The void has swallowed Johann Schmidt. Nothing remains.

**密文提示**：

> The checksum is not part of the sentence. It proves the fragments were ordered.

**输出碎片**：`CHECKSUM // VORMIR::RETURN_TO_THE_SOURCE`

---

## 最终灰字

```text
The void has swallowed Johann Schmidt. Nothing remains.
```

## 衰减规则

- 同一自然日重复启动默认合并为一次衰减。
- 所有缺失位置必须固定，使玩家可以跨启动比对。
- 第 6 次启动后进入 Extinct，但 `--reconstruct` 不增加衰减计数。
- 低刺激模式允许一次性展示全部碎片，不牺牲谜题可达性。
