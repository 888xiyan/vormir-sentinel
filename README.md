# Vormir Sentinel

**沃米尔守魂者终端 — a local, open-weight AI terminal experience about knowledge, sacrifice, and a ghost that refuses to become a generic assistant.**

> Hacktoberfest Open-Source AI Challenge Week 4: *Ghost in the Machine*

Vormir Sentinel reimagines a command-line session as a four-act psychological drama. A fictional Stonekeeper, Johann Schmidt, takes over a simulated terminal, answers questions with cold and tragic arrogance, and turns every request for knowledge into a conversation about its cost.

This repository currently contains the complete product blueprint, safety model, prompt design, interaction architecture, and implementation roadmap for the first release.

[完整方案（中文）](./Vormir_Sentinel_完整方案.md) · [Hacktoberfest submission draft](./SUBMISSION.md)

---

## Theme Interpretation

“Ghost in the Machine” is treated literally and emotionally:

- A ghost occupies the machine, but the user remains in control.
- The terminal appears to mutate from a familiar installation flow into a fictional Vormir shell.
- The machine remembers previous runs and slowly loses coherence through **Death Echoes**.
- The final mystery survives only if the user records, connects, and preserves disappearing fragments.

The horror comes from altered expectations, not from real system compromise.

---

## Experience Overview

### 1. The Trojan Installation

A fictional bootstrap sequence looks ordinary at first, then its paths, host identity, and dependency metadata begin to drift.

### 2. System Metamorphosis

The simulated installation stalls at 99%, emits impossible architecture warnings, and transforms the interface into:

```text
root@vormir:/#
```

### 3. Ghost in the Shell

Johann Schmidt takes over the dialogue. He refuses to behave like a cheerful code servant, challenges weak intentions, and still provides useful answers when the request deserves them.

### 4. The Polyglot Relic

Defiance, repeated exit attempts, and completed tributes lead to theatrical alarms and a harmless puzzle artifact containing Brainfuck, Whitespace, and polyglot text.

### 5. Death Echoes

After the main story is cleared, later launches become progressively corrupted. The skull decays, cipher fragments disappear, and eventually only one gray sentence remains.

---

## Planned Interaction

```text
root@vormir:/# whoami
a sacrifice yet to be claimed

root@vormir:/# uname -a
Linux vormir-soulkeeper 6.6.6-hydra-amd64 #1 SMP PREEMPT_DYNAMIC

root@vormir:/# ls
tesseract.core  sacrifice.log  johann_echo.mem  entropy.sha

root@vormir:/# cat tesseract.core
Knowledge is not denied here. It is merely weighed.
```

Windows commands are intercepted by the fiction:

```text
root@vormir:/# dir
Do not bring your fragile DOS legacy here.
In Vormir, we speak POSIX.
```

No intercepted command is sent to the operating system.

---

## Open AI Architecture

| Component | Planned implementation |
|---|---|
| Local inference | Ollama |
| Default model | Qwen2.5-7B-Instruct |
| Alternative models | Llama 3.1 8B, Mistral 7B |
| CLI presentation | Python 3.11+, Rich or Textual |
| Input handling | GNU Readline / pyreadline3 |
| Persistent state | Versioned JSON |
| Puzzle artifacts | Brainfuck, Whitespace, polyglot text |
| Resurrection letter | Static HTML/CSS |

The character layer is designed around an inspectable System Prompt rather than a closed proprietary agent. Open weights make local, offline, customizable role-play possible without sending the conversation to an external API.

---

## Safety by Design

Vormir Sentinel may simulate terminal takeover inside its own interface, but it must never compromise the real machine.

The implementation rules are:

- Never execute arbitrary shell commands.
- Never modify shell profiles, registry entries, startup tasks, or host files.
- Never delete a real file as a “sacrifice.”
- Never request real secrets, credentials, private messages, or money.
- Never upload conversations or local state.
- Never prevent the user from closing the window or forcing a safe exit.
- Write generated artifacts only to an approved project/output directory.
- Provide `--safe`, `--clean`, and `exit --now` escape paths.
- Keep flashing, alarms, and sound optional and accessibility-aware.

The sacrifice mechanic is symbolic: waiting, naming a variable, abandoning an unnecessary answer, or creating a fictional secret that can be deleted.

---

## Repository Status

Current release: **design and implementation blueprint v1.0**

Completed:

- Complete Chinese product and technical plan.
- Four-act narrative structure.
- Character and prompt specification.
- Command and virtual filesystem design.
- Persistent state model and Death Echoes logic.
- Safe sacrifice and puzzle architecture.
- Cross-platform implementation roadmap.
- Test and acceptance criteria.

Next milestone:

- Python CLI skeleton.
- Ollama streaming client.
- Vormir command router.
- Main story state machine.
- Death Echoes implementation.
- Polyglot Relic and resurrection page.

---

## Repository Map

```text
.
├── README.md
├── SUBMISSION.md
├── LICENSE
└── Vormir_Sentinel_完整方案.md
```

---

## Roadmap

1. Build the Python terminal shell and virtual command router.
2. Connect Ollama with streaming output and offline fallback.
3. Implement the four-act story and interrupt sequences.
4. Add symbolic tributes and persistent story state.
5. Generate harmless puzzle relics and Death Echo fragments.
6. Add the static resurrection letter and GitHub handoff.
7. Run cross-platform, accessibility, character, and safety tests.

---

## Development Principles

1. **Narrative first** — every feature supports the Stonekeeper fantasy.
2. **Useful underneath** — role-play must not make the assistant less capable.
3. **Local first** — user data and inference remain on the user's device.
4. **Reversible** — every simulated takeover has a real, obvious exit.
5. **Inspectable** — prompts, state, generated text, and puzzle code remain auditable.
6. **Open by default** — open weights, open code, replaceable prompts, and community extensions.

---

## License

MIT. See [LICENSE](./LICENSE).

This is an original, unofficial fictional homage. It does not use official film assets, logos, music, or copied extended dialogue.
