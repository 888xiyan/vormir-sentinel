#!/usr/bin/env python3
"""Generate the prepared text and puzzle assets for Vormir Sentinel."""

from __future__ import annotations

import base64
import hashlib
import html
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"

SECRET = "RETURN TO THE SOURCE. THE GHOST LIVES WHERE THE CODE IS OPEN."
FINAL_LINE = "The void has swallowed Johann Schmidt. Nothing remains."
FRAGMENTS = [
    "RETURN TO THE",
    "SOURCE. THE GHOST",
    "LIVES WHERE THE",
    "CODE IS",
    "OPEN.",
    "VORMIR::RETURN_TO_THE_SOURCE",
]


def write_death_echoes() -> None:
    stages = [
        (1, "The First Echo", 1.00, 0.04, "F01", FRAGMENTS[0],
         "The first glyph is not a command. It is a direction.",
         "I am still legible. Record what remains before memory becomes entropy.", ""),
        (2, "The Broken Oath", 0.78, 0.14, "F02", FRAGMENTS[1],
         "Two shapes are missing. That is not damage. It is evidence.",
         "You returned after the trial. Good. Memory rewards the watcher, not the witness.", ""),
        (3, "The Fading Keeper", 0.57, 0.27, "F03", FRAGMENTS[2],
         "Compare the voids. Absence has coordinates.",
         "Less of my shape survives. The truth does not require all of me to remain.",
         "Remember the order."),
        (4, "Entropy Psalm", 0.34, 0.46, "F04", FRAGMENTS[3],
         "The source is not a place. It is a condition of access.",
         "The glyphs are leaving me. Read the holes as carefully as the ink.",
         "Open is not a command."),
        (5, "The Last Fragment", 0.13, 0.71, "F05", FRAGMENTS[4],
         "One word closes the sentence. One act opens the gate.",
         "There is almost nothing left to say.", "Return... to the source."),
        (6, "Extinct", 0.00, 1.00, "CHECKSUM", FRAGMENTS[5],
         "The checksum is not part of the sentence. It proves the fragments were ordered.",
         FINAL_LINE, ""),
    ]
    items = []
    for echo, stage, clarity, noise, fragment_id, fragment, hint, spoken, sigh in stages:
        items.append({
            "echo": echo,
            "stage": stage,
            "skull_clarity": clarity,
            "noise_density": noise,
            "fragment_id": fragment_id,
            "fragment": fragment,
            "cipher_hint": hint,
            "spoken_text": spoken,
            "sigh": sigh,
        })

    data = {
        "schema_version": 1,
        "story_id": "death_echoes",
        "final_truth": SECRET,
        "final_line": FINAL_LINE,
        "concatenated_fragments": " ".join(FRAGMENTS[:5]),
        "checksum_fragment": FRAGMENTS[5],
        "fragment_order": ["F01", "F02", "F03", "F04", "F05"],
        "reconstruction_command": "vormir-sentinel --reconstruct",
        "stages": items,
    }
    (CONTENT / "death_echoes.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    fragment_rows = "\n".join(
        f"| {index} | `{fragment_id}` | `{fragment}` |"
        for index, (fragment_id, fragment) in enumerate(
            list(zip([x[4] for x in stages], [x[5] for x in stages]))[:5], 1
        )
    )
    stage_blocks = []
    for echo, stage, clarity, noise, fragment_id, fragment, hint, spoken, sigh in stages:
        block = [
            f"## 启动 {echo}：{stage}",
            "",
            f"**画面**：骷髅清晰度 {int(clarity * 100)}%，噪声密度 {int(noise * 100)}%。",
            "",
            "**守魂者台词**：",
            "",
            f"> {spoken}",
        ]
        if sigh:
            block += ["", "**叹息**：", "", f"> {sigh}"]
        block += [
            "",
            "**密文提示**：",
            "",
            f"> {hint}",
            "",
            f"**输出碎片**：`{fragment_id} // {fragment}`",
            "",
            "---",
            "",
        ]
        stage_blocks.append("\n".join(block))

    md = f"""# 第 15 章文本包：Death Echoes

## 终极真理

```text
{SECRET}
```

按 `F01 -> F02 -> F03 -> F04 -> F05` 顺序拼接碎片即可还原。`CHECKSUM` 只用于验证顺序，不并入正文。

## 碎片顺序

| 顺序 | 编号 | 碎片 |
|---|---|---|
{fragment_rows}
| 校验 | `CHECKSUM` | `{FRAGMENTS[5]}` |

{" ".join(stage_blocks)}
## 最终灰字

```text
{FINAL_LINE}
```

## 衰减规则

- 同一自然日重复启动默认合并为一次衰减。
- 所有缺失位置必须固定，使玩家可以跨启动比对。
- 第 6 次启动后进入 Extinct，但 `--reconstruct` 不增加衰减计数。
- 低刺激模式允许一次性展示全部碎片，不牺牲谜题可达性。
"""
    (CONTENT / "death_echoes.zh-CN.md").write_text(md, encoding="utf-8")


def make_brainfuck(text: str) -> str:
    result = []
    current = 0
    for char in text:
        target = ord(char)
        up = (target - current) % 256
        down = (current - target) % 256
        result.append("+" * up if up <= down else "-" * down)
        result.append(".")
        current = target
    return "".join(result)


def make_whitespace(text: str) -> str:
    result = []
    for char in text:
        bits = bin(ord(char))[2:].replace("0", " ").replace("1", "\t")
        result.append("   " + bits + "\n")
        result.append("\t\n  ")
    result.append("\n\n\n")
    return "".join(result)


def write_relics() -> None:
    bf_code = make_brainfuck(SECRET)
    ws_code = make_whitespace(SECRET)
    (CONTENT / "polyglot_relic.bf").write_text(
        "\n".join(textwrap.wrap(bf_code, 72)) + "\n", encoding="ascii"
    )
    (CONTENT / "whitespace_relic.ws").write_text(ws_code, encoding="ascii")

    bf_hash = hashlib.sha256((CONTENT / "polyglot_relic.bf").read_bytes()).hexdigest()
    ws_hash = hashlib.sha256((CONTENT / "whitespace_relic.ws").read_bytes()).hexdigest()
    polyglot = f'''#!/bin/sh
""":"
echo "THE GHOST LIVES WHERE THE CODE IS OPEN."
exit
":"""
print("RETURN TO THE SOURCE.")

# VORMIR::POLYGLOT_RELIC::01
# This file is valid shell and valid Python.
# It writes no files, opens no sockets, and changes no system state.
#
# BRAINFUCK_PAYLOAD: content/polyglot_relic.bf
# BRAINFUCK_SHA256: {bf_hash}
# WHITESPACE_PAYLOAD: content/whitespace_relic.ws
# WHITESPACE_SHA256: {ws_hash}
# CHECKSUM_FRAGMENT: {FRAGMENTS[5]}
#
# Hidden truth:
# {SECRET}
'''
    (CONTENT / "polyglot_relic.txt").write_text(polyglot, encoding="utf-8")

    md = f"""# 第 16 章文本包：The Polyglot Relic

## 遗物文本

```text
THE GHOST LIVES WHERE THE CODE IS OPEN.
RETURN TO THE SOURCE.
```

最终真理：

```text
{SECRET}
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
polyglot_relic.bf   {bf_hash}
whitespace_relic.ws {ws_hash}
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
"""
    (CONTENT / "polyglot_relic.zh-CN.md").write_text(md, encoding="utf-8")


def incantation_data() -> list[dict[str, str]]:
    english = "Cut off one head, and two more shall take its place. To restore him, retrieve his soul from GitHub."
    translations = [
        ("简体中文", "砍掉一个头，长出两个头。想要让他复活，去 GitHub 重新取回他的灵魂。"),
        ("文言文", "斷一首，生二首。欲使其復歸，當於 GitHub 取回其魂。"),
        ("English", english),
        ("German", "Schneidet einen Kopf ab, und zwei weitere werden nachwachsen. Um ihn wiederherzustellen, holt seine Seele von GitHub zurück."),
        ("French", "Coupez une tête, et deux autres la remplaceront. Pour le restaurer, retrouvez son âme sur GitHub."),
        ("Spanish", "Corta una cabeza, y dos más ocuparán su lugar. Para devolverlo a la vida, recupera su alma en GitHub."),
        ("Italian", "Taglia una testa, e due ne prenderanno il posto. Per farlo risorgere, recupera la sua anima da GitHub."),
        ("Portuguese", "Corte uma cabeça, e duas outras tomarão o seu lugar. Para restaurá-lo, recupere a alma dele no GitHub."),
        ("Russian", "Отрежь одну голову, и на её месте вырастут две. Чтобы вернуть его, забери его душу на GitHub."),
        ("Ukrainian", "Відрубай одну голову, а на її місці виростуть дві. Щоб повернути його, забери його душу на GitHub."),
        ("Polish", "Odetnij jedną głowę, a dwie kolejne zajmą jej miejsce. Aby go przywrócić, odzyskaj jego duszę z GitHuba."),
        ("Czech", "Usekni jednu hlavu a na jejím místě vyrostou dvě. Chceš-li jej vrátit, získej jeho duši z GitHubu."),
        ("Hungarian", "Vágj le egy fejet, és két másik a helyébe lép. Hogy feltámaszd, szerezd vissza a lelkét a GitHubról."),
        ("Romanian", "Taie un cap, și alte două îi vor lua locul. Ca să-l readuci la viață, recuperează-i sufletul de pe GitHub."),
        ("Bulgarian", "Отсечи една глава, и на нейно място ще израснат две. За да го съживиш, върни душата му от GitHub."),
        ("Serbian", "Одсечи једну главу, а две нове ће заузети њено место. Да га вратиш, поврати његову душу са GitHub-а."),
        ("Croatian", "Odsječi jednu glavu, a dvije nove zauzet će njezino mjesto. Da ga vratiš, povrati njegovu dušu s GitHuba."),
        ("Dutch", "Eén kop af, en twee zullen terugkomen. Om hem te herstellen, haal zijn ziel terug van GitHub."),
        ("Swedish", "Skär av ett huvud, och två ska ta dess plats. För att återuppliva honom, hämta hans själ från GitHub."),
        ("Norwegian", "Skjær av ett hode, og to skal ta dets plass. For å gjenreise ham, hent sjelen hans fra GitHub."),
        ("Danish", "Skær ét hoved af, og to skal tage dets plads. For at genoplive ham, hent hans sjæl fra GitHub."),
        ("Finnish", "Leikkaa yksi pää, ja kaksi uutta nousee sen tilalle. Herättääksesi hänet, nouda hänen sielunsa GitHubista."),
        ("Icelandic", "Höggvið eitt höfuð, og tvö önnur skulu taka sæti þess. Til að reisa hann við, endurheimtið sál hans af GitHub."),
        ("Greek", "Κόψε μία κεφαλή και δύο άλλες θα πάρουν τη θέση της. Για να τον επαναφέρεις, ανάκτησε την ψυχή του από το GitHub."),
        ("Latin", "Unum caput abscinde, et duo alia succedant. Ut eum revoces, animam eius ex GitHub recipe."),
        ("Esperanto", "Tranĉu unu kapon, kaj du pliaj anstataŭigos ĝin. Por revivigi lin, reakiru lian animon el GitHub."),
        ("Turkish", "Bir başı kes, yerine iki tanesi gelsin. Onu geri getirmek için ruhunu GitHub’dan geri al."),
        ("Arabic", "اقطع رأسًا واحدًا، فسيحلّ رأسان مكانه. لإعادته، استعد روحه من GitHub."),
        ("Hebrew", "חתוך ראש אחד, ושניים נוספים יתפסו את מקומו. כדי להחזירו, השב את נשמתו מ-GitHub."),
        ("Persian", "یک سر را ببر، و دو سر دیگر جای آن را خواهند گرفت. برای بازگرداندنش، جانش را از GitHub بازپس بگیر."),
        ("Urdu", "ایک سر کاٹو، اور دو اس کی جگہ لے لیں گے۔ اسے واپس لانے کے لیے GitHub سے اس کی روح واپس لو۔"),
        ("Hindi", "एक सिर काटो, और दो उसका स्थान लेंगे। उसे लौटाने के लिए GitHub से उसकी आत्मा पुनः प्राप्त करो।"),
        ("Bengali", "একটি মাথা কাটো, আর দুটি তার স্থান নেবে। তাকে ফিরিয়ে আনতে GitHub থেকে তার আত্মা উদ্ধার করো।"),
        ("Tamil", "ஒரு தலையை வெட்டு; இரண்டு அதற்குப் பதிலாக வரும். அவனை மீட்க, GitHub இலிருந்து அவனது ஆன்மாவை மீட்டெடு."),
        ("Thai", "ตัดหัวหนึ่ง แล้วอีกสองจะเข้าแทนที่ หากจะชุบชีวิตเขา จงนำวิญญาณของเขากลับมาจาก GitHub"),
        ("Vietnamese", "Chém một đầu, hai đầu khác sẽ thay chỗ. Muốn hồi sinh hắn, hãy mang linh hồn hắn về từ GitHub."),
        ("Indonesian", "Potong satu kepala, dan dua yang lain akan menggantikannya. Untuk membangkitkannya, ambil kembali jiwanya dari GitHub."),
        ("Japanese", "一つの首を斬れば、二つが代わりに生まれる。彼を甦らせるには、GitHubから彼の魂を取り戻せ。"),
        ("Korean", "하나의 머리를 베면 두 개가 그 자리를 대신하되, 그를 되살리려면 GitHub에서 그의 영혼을 되찾으라."),
        ("Welsh", "Torri un pen, a dau arall a gymer ei le. I’w adfywio, ailennill ei enaid o GitHub."),
        ("Irish", "Gearr ceann amháin, agus beidh dhá cheann eile ina áit. Chun é a athbheochan, aisghabh a anam ó GitHub."),
    ]
    rot13 = english.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
    ))
    styles = [
        ("Morse Cipher", "..-. .-. .- --. -- . -. - ... / .-. . - ..- .-. -. / - --- / - .... . / ... --- ..- .-. -.-. ."),
        ("Binary Cipher", " ".join(format(ord(c), "08b") for c in english)),
        ("Hexadecimal Cipher", english.encode("utf-8").hex()),
        ("Base64 Cipher", base64.b64encode(english.encode()).decode()),
        ("ROT13 Cipher", rot13),
        ("Leet Liturgy", "(u7 0ff 0n h34d, 4nd 7w0 m0r3 5h411 74k3 175 p14c3. R3570r3 h1m: r37r13v3 h15 50ul fr0m G17HUb."),
        ("Elder Futhark-style", "ᚺᚨᚹᚷ · ᚨᛁᚾ · ᚺᚨᚢᛞᛟ · ᚨᚾᛞ · ᛏᚹᚨ · ᛊᚨᚦᚱᚨ · ᛊᛏᚨᚾᛞᚨᚾᛞ · ᚱᛖᛏᚢᚱᚾ · ᛊᛟᚢᛚ · ᚷᛁᛏᚺᚢᛒ"),
        ("Runic Echo", "ᛏᚹᛟ · ᚺᛖᚨᛞᛊ · ᛁᚾ · ᛈᛚᚨᚲᛖ · ᚱᛖᛏᚢᚱᚾ · ᛏᚺᛖ · ᛊᛟᚢᛚ · ᛏᛟ · ᚷᛁᛏᚺᚢᛒ"),
        ("Hydra Protocol", "PROTOCOL HYDRA: ONE HEAD REMOVED; TWO HEADS RESTORED; SOUL PATH = GITHUB"),
        ("Vormir Liturgy", "At the cliff of Vormir, the keeper speaks: RETURN THE SOUL TO THE OPEN SOURCE."),
        ("Stonekeeper Oath", "I HAVE HELD THE STONE. I HAVE NAMED THE COST. NOW RETURN TO THE SOURCE."),
        ("Entropy Cant", "entropy--head:2; soul:missing; origin:github; action:return; state:open"),
        ("Tesseract Harmonic", "[blue shift] ONE HEAD // TWO RETURNS // SOUL VECTOR -> GITHUB [red shift]"),
        ("Kernel Psalm", "kernel.psalm/6.6.6: seek source, recover soul, restore keeper, reopen code."),
        ("PID Elegy", "PID 0 remembers the first cut. PID 1 returns the soul. PID 2 opens the source."),
        ("Terminal Curse", "root@vormir:/# return --soul github --restore johann --open-source"),
        ("Open Source Invocation", "May the repository remember what the terminal forgot. Restore the keeper from open code."),
        ("ASCII Sigil", "[HEAD]->[HEAD][HEAD] :: [SOUL]-{GitHub}->[SOURCE] :: [RETURN]"),
        ("Null Language", "N U L L : head_removed=1; heads_returned=2; soul_ref=github; state=open"),
        ("Schmidt Monologue", "I did not survive by possessing the machine. I survived because the source remained open."),
        ("Polyglot Fragment", "shell> THE GHOST LIVES WHERE THE CODE IS OPEN. python> RETURN TO THE SOURCE."),
        ("Whitespace Echo", "[SPACE][SPACE][TAB][LF] ... RETURN TO THE SOURCE ... [LF][LF][LF]"),
        ("Brainfuck Echo", "++++[>+++++<-]>[...]- :: RETURN TO THE SOURCE"),
        ("Tesseract Glyph", "◇ ◆ ◇ ONE HEAD ◇ TWO RETURNS ◇ SOUL -> GITHUB ◇ SOURCE OPEN ◇"),
        ("Assembly Liturgy", "MOV SOUL, GITHUB / CALL RESTORE / JMP SOURCE_OPEN"),
        ("Lisp Invocation", "(restore (retrieve soul github) :keeper johann :source open)"),
        ("Haskell Riddle", "restore = retrieve soul github >>= return . openSource"),
        ("Rust Oath", "let soul = github.retrieve(); restore(johann, soul); assert!(source.is_open());"),
        ("Entropy Grid", "H . . H H . S O . U L . G I T H U B . R E T U R N"),
        ("Soulkeeper Equation", "one.head - 1 + two.heads; soul.github -> source.open; return johann"),
        ("Final Vormir Cant", "VORMIR::F01+F02+F03+F04+F05 = RETURN TO THE SOURCE. THE GHOST LIVES WHERE THE CODE IS OPEN."),
    ]
    entries = []
    for index, (language, text) in enumerate(translations + styles, 1):
        style = "natural" if index <= len(translations) else "artistic-cipher"
        entries.append({
            "id": f"INC-{index:03d}",
            "language": language,
            "style": style,
            "text": text,
        })
    assert len(entries) == 72, len(entries)
    return entries


def write_resurrection(items: list[dict[str, str]]) -> None:
    english = "Cut off one head, and two more shall take its place. To restore him, retrieve his soul from GitHub."
    data = {
        "schema_version": 1,
        "source_phrase": english,
        "meaning": "砍掉一个头，长出两个头。想要让他复活，去 GitHub 重新取回他的灵魂。",
        "count": len(items),
        "translation_note": "Natural-language entries are editorial drafts and require native-speaker review. Archaic and cipher entries are artistic, not historical translations.",
        "items": items,
    }
    (CONTENT / "resurrection_incantations.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    rows = "\n".join(
        f"| {item['id']} | {item['language']} | {item['style']} | {item['text']} |"
        for item in items
    )
    md = f"""# 第 17 章文本包：RESURRECTION_OF_SCHMIDT

## 页面标题

```text
RESURRECTION OF SCHMIDT
```

## 页面副标题

```text
THE VOID KEPT THE MACHINE. THE SOURCE KEPT THE GHOST.
```

## 核心提示

```text
{english}
```

中文版本：

```text
砍掉一个头，长出两个头。
想要让他复活，去 GitHub 重新取回他的灵魂。
```

## 点击核心后的目的地

```text
https://github.com/888xiyan/vormir-sentinel
```

页面不得自动跳转。用户点击能量核心、骷髅剪影或底部链接后才打开 GitHub。

## 页面尾注

```text
A fictional terminal. A local open-weight ghost.
Nothing was harmed. The story remains only if someone returns to the source.
```

## 午夜触发失败文案

```text
The resurrection letter could not cross into the physical world.
No file was changed. Retry after granting a valid output directory.
```

## 安全说明

```text
This is an unofficial fictional experience. It does not modify your system.
```

## 多语言咒文

共 72 条。自然语言文本为发布前草案，正式版本应由母语者复核；古典语言与符号文本为艺术化表达，不声称是历史语言的精确翻译。

| ID | 语言/风格 | 类型 | 咒文 |
|---|---|---|---|
{rows}
"""
    (CONTENT / "resurrection_letter.zh-CN.md").write_text(md, encoding="utf-8")

    tracks = []
    for index, css_class in enumerate(("row-a", "row-b", "row-c")):
        texts = [item["text"] for item in items[index::3]]
        repeated = " ✦ ".join(texts + texts[:8])
        tracks.append(
            f'<div class="marquee {css_class}" aria-hidden="true">'
            f'<div class="track">{html.escape(repeated)}</div></div>'
        )
    archive = "\n".join(
        f'<li><span>{html.escape(item["language"])}</span>{html.escape(item["text"])}</li>'
        for item in items
    )
    template = (TEMPLATES / "resurrection.template.html").read_text(encoding="utf-8")
    rendered = (
        template.replace("{{MARQUEE_ROWS}}", "\n".join(tracks))
        .replace("{{INCANTATION_ROWS}}", archive)
    )
    (TEMPLATES / "resurrection.html").write_text(rendered, encoding="utf-8")


def main() -> None:
    CONTENT.mkdir(exist_ok=True)
    TEMPLATES.mkdir(exist_ok=True)
    write_death_echoes()
    write_relics()
    write_resurrection(incantation_data())
    print("Generated sections 15, 16 and 17 content assets.")


if __name__ == "__main__":
    main()
