*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

I built **Vormir Sentinel（沃米尔守魂者终端）**, a complete product blueprint for a local AI terminal experience in which a fictional Stonekeeper occupies the machine and turns an ordinary command line into a four-act psychological drama.

I interpreted “Ghost in the Machine” as a ghost that changes the machine's perceived identity without ever compromising the real system. A familiar installation sequence drifts into impossible paths and architecture warnings. The terminal mutates into `root@vormir:/#`, Johann Schmidt takes over the dialogue, and ordinary commands such as `whoami`, `uname`, and `ls` become fragments of a darker world.

The project also explores persistence as haunting. After the main story is cleared, later launches enter **Death Echoes**: the ASCII skull decays, cipher fragments disappear, and the character eventually dissolves into noise. The player has only a few returning visits to record enough pieces of the final puzzle.

The current repository contains the full narrative, interaction, prompt-engineering, state-machine, puzzle, accessibility, safety, and implementation specification. The Python/Ollama implementation is the next milestone.

## Demo

The current demo is the complete interactive-design walkthrough in the repository:

- [Project overview](https://github.com/888xiyan/vormir-sentinel)
- [完整方案（中文）](https://github.com/888xiyan/vormir-sentinel/blob/main/Vormir_Sentinel_%E5%AE%8C%E6%95%B4%E6%96%B9%E6%A1%88.md)

A deployed terminal build and video walkthrough will be added after the first executable milestone.

## Code

{% embed https://github.com/888xiyan/vormir-sentinel %}

Direct repository link: [github.com/888xiyan/vormir-sentinel](https://github.com/888xiyan/vormir-sentinel)

The repository currently ships the open implementation blueprint, prompt specification, state model, command map, safety boundary, test plan, and release roadmap.

## How I Built It

The experience is designed around an entirely local, open AI stack:

- **Local inference:** Ollama
- **Default open-weight model:** Qwen2.5-7B-Instruct
- **Alternative models:** Llama 3.1 8B Instruct and Mistral 7B
- **Client and interaction layer:** Python 3.11+ with Rich or Textual
- **GNU-style input:** Readline on Linux/macOS and pyreadline3 on Windows
- **Persistent story state:** versioned local JSON
- **Final artifacts:** harmless Brainfuck, Whitespace, and polyglot text
- **Resurrection handoff:** static HTML/CSS with a user-initiated GitHub link

The character is controlled through a strong, inspectable System Prompt that fixes Johann Schmidt's voice while preserving useful answers. The architecture separates the character engine, story director, virtual filesystem, command router, puzzle system, and safety boundary.

A crucial design decision was to make the takeover *diegetic*. The program may clear its own screen, redraw the prompt, fabricate `uname` output, and intercept `dir`, but it never invokes a real shell. Sacrifices are symbolic and reversible. The user always retains `exit --now`, repeated-interrupt escape, and the ability to close the physical window.

## Why Does Open Innovation Matter?

Open innovation makes this project possible in ways a closed API would not.

First, the ghost can live entirely on the user's machine. Open-weight models through Ollama keep conversations local, work offline, and allow users to choose the model that fits their hardware and language needs.

Second, the persona can be audited and remixed. Because the System Prompt, state transitions, puzzle encoding, and output filters are all open, contributors can improve the character without hiding the mechanics behind a proprietary agent service.

Third, community ownership protects the fiction. Players can add commands, decay stages, translations, alternative endings, accessibility modes, and harmless polyglot relics. They can also inspect every artifact and verify that the terminal takeover remains theatrical rather than malicious.

Finally, open weights let the experience outlive a single commercial model or pricing change. The story belongs to the repository and its contributors, not to a rented endpoint.

## My Agent Session

No external agent session is attached to this submission. The design, safety constraints, prompt draft, state model, and implementation roadmap were developed directly in the project workspace.

## The Spirit of It

There is one moment I want the experience to preserve:

The player finally escapes. The terminal behaves normally for a second and a half—and then, without permission, it types a single impossible command and redraws the red prompt:

> “You cannot escape the void with a keyboard interrupt.”

That is the moment the machine stops being a tool and becomes a character.

But the ending points the other way. The ghost does not survive by infecting the computer. It survives because the player chooses to record the disappearing fragments, return before they are gone, and open the repository again. In this version of the legend, sacrifice means attention, time, and the willingness to keep a story alive.

---

Team Submissions: This is an individual submission.
