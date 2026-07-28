# Future Crash Oracle — Operator Cheat Sheet

## Main controls

| Key | Function |
|---|---|
| `A` | Ask the Oracle |
| `F` | Follow up after an Oracle answer |
| `S` | Save the current exchange after an answer; from Home, enter Signal Room |
| `Space` | Request a new fortune |
| `M` | Open Machine Memory |
| `T` | Open Terminal Constellation |
| `D` | Enter Dream Mode |
| `:` | Open the internal command console |
| `P` | PANIC |
| `O` | Toggle Ollama |
| `Esc` | Cancel, dismiss, wake, return, or quit from Home |
| `Q` | Quit |

## Official console commands

Open the console with `:` and type:

| Command | Result |
|---|---|
| `help` or `?` | Show the documented command list |
| `status` | Show load, memory use, and uptime |
| `model` | Show the configured Ollama model and link state |
| `fortune` | Run the real Unix `fortune` command, with built-in fallback |
| `memory` | Show launches, inquiries, and panic count |
| `locate cow` | Request the classified location of the cow |
| `diagnose causality` | Run the causality self-test |
| `clear` | Clear the console transcript |

Press `Esc` to leave the console.

## Undocumented console vocabulary

These are exact commands. Capitalization does not matter.

| Secret command | Machine response |
|---|---|
| `xyzzy` | A hollow voice says: wrong cave, excellent terminal. |
| `plugh` | A distant relay clicks in recognition. |
| `42` | Answer confirmed. Question remains under construction. |
| `hello` | Hello, operator. Your presence has been entered into the minutes. |
| `hi` | Acknowledged with minimal but sincere voltage. |
| `whoami` | Operator, provisional custodian of this timeline. |
| `coffee` | Coffee reserves are conceptually abundant and physically absent. |
| `status coffee` | COFFEE 0% // morale compensating. |
| `sing` | The terminal emits one sustained 60 Hz note and calls it experimental. |
| `dance` | Three cursors move one column left. Reviews are mixed. |
| `moo` | The cow acknowledges your credentials. |
| `please` | Politeness override accepted. Nothing else changed. |
| `sorry` | Apology archived and immediately forgiven. |
| `sudo panic` | Operator is already in the panic group. |
| `help help` | Help is receiving help. Please remain unhelped briefly. |
| `why` | Because the alternative failed self-test. |
| `when` | Shortly after now, but before the paperwork. |
| `where` | Approximately here, modulo terminal geometry. |
| `reality` | Mounted read-write with several warnings. |
| `future` | Present, but poorly documented. |
| `past` | Read-only. Mostly. |
| `love` | Unsupported protocol detected. Signal strength: encouraging. |
| `meaning` | Meaning service is running locally on an undocumented port. |

## Oracle conversation behavior

- The Oracle keeps the six most recent completed exchanges in active context.
- Older exchanges are folded into a compact rolling summary.
- After an answer, press `F` for a contextual follow-up.
- After an answer, press `S` to save that exchange into Machine Memory.
- Saved exchanges are voluntary and stored locally in `~/.monan_oracle_memory.json`.

## Panic protocol

Press `P` from the Home screen.

The machine may refuse the request. Otherwise it freezes normal operation, escalates beyond 100% panic, corrupts the display, collapses the CRT, reboots, and returns to Home without losing persistent state.

Typing `sudo panic` in the console does **not** trigger Panic. The operator already has sufficient privileges; use the actual `P` key.

## Notes for archivists

- Unknown console commands receive one of several randomized rejection messages.
- Unix `fortune`, `cowsay`, and Ollama are optional; built-in content keeps the workstation alive without them.
- The release contains no implemented Konami-code mode. Rumors to the contrary are unsupported by the Archive.
