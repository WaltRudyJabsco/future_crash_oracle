<img width="1353" height="813" alt="Screenshot 2026-07-28 at 5 52 09 PM" src="https://github.com/user-attachments/assets/fb7b077f-61b3-4bd0-88ce-5d72e2a5b143" />

Future Crash Oracle

A tiny fictional operating system for your terminal.

Future Crash Oracle is a single Python program that turns a terminal window into a living retro-futuristic workstation.

It watches your machine, generates observations, dispenses Unix fortunes, talks through a local AI model, occasionally dreams, occasionally panics, and generally behaves like a slightly malfunctioning computer from an alternate 1980s.

<img width="1353" height="813" alt="Screenshot 2026-07-28 at 5 52 54 PM" src="https://github.com/user-attachments/assets/130932c2-9fa2-4e79-b7b0-81db072e58df" />

Features

* Matrix rain
* Live system telemetry
* Ask the Oracle (local AI)
* Machine Memory
* Dream Mode
* Signal Room
* Panic button
* CRT reboot animations
* Unix fortune + cowsay
* One Python file

Installation

Use Homebrew (or your preferred package manager):

brew install fortune cowsay ollama

Download a model for Ollama.

A great all-around choice:

ollama pull qwen3:8b

If you prefer a model with fewer built-in guardrails, you can also experiment with community models such as Wizard Vicuna Uncensored or other compatible Ollama models. Different models have different capabilities, personalities, and safety characteristics, so choose one that matches how you want to use the Oracle.

Clone this repository:

git clone https://github.com/WaltRudyJabsco/future_crash_oracle.git
cd future-crash-oracle

Run it:

python3 future_crash_oracle.py --ollama --model qwen3:8b

The program expects standard Homebrew locations by default (for example /opt/homebrew/bin on Apple Silicon), but it will also work if the utilities are available on your shell’s PATH.

Optional: create a shortcut

Add an alias to your ~/.zshrc:

alias rzt='python3 "/path/to/future_crash_oracle.py" --ollama --model qwen3:8b'

Reload your shell:

source ~/.zshrc

Now simply type:

rzt

from anywhere.

<img width="1353" height="813" alt="Screenshot 2026-07-28 at 5 53 21 PM" src="https://github.com/user-attachments/assets/74830e45-0c0b-457a-b649-b5dae9f71909" />

Keyboard

Key	Action
A	Ask the Oracle
Space	New Fortune
M	Machine Memory
S	Signal Room
T	Terminal Constellation
D	Dream Mode
:	Command Console
P	Panic
O	Toggle Ollama
Esc	Return
Q	Quit

Philosophy

Future Crash Oracle isn’t trying to simulate a real operating system.

It’s trying to feel like you found a forgotten workstation from an alternate future—part system monitor, part AI companion, part science-fiction movie prop.

Leave it running on a spare monitor. Ask it questions. Press Panic only when absolutely necessary.

(You will press Panic.)

<img width="1353" height="813" alt="Screenshot 2026-07-28 at 5 53 55 PM" src="https://github.com/user-attachments/assets/bbd54feb-62b1-430f-a7f6-a64eea125686" />

