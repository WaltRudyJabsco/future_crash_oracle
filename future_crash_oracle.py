#!/usr/bin/env python3
"""MONAN Terminal Companion — a low-power ambient machine personality.

Runs until Q/Ctrl-C. Uses only the Python standard library. Optional Ollama
support is deliberately infrequent and asynchronous so the interface remains
responsive and the laptop remains a laptop.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import random
import re
import select
import shutil
import socket
import subprocess
import sys
import termios
import threading
import time
import tty
import urllib.error
import urllib.request
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ESC = "\x1b["
RESET = f"{ESC}0m"
CLEAR = f"{ESC}2J{ESC}H"
HIDE = f"{ESC}?25l"
SHOW = f"{ESC}?25h"
ALT_ON = f"{ESC}?1049h"
ALT_OFF = f"{ESC}?1049l"

VERSION = "FUTURE CRASH // MONAN OS 11.2 — RELEASE CANDIDATE"
FPS = 12
TELEMETRY_INTERVAL = 2.0
THOUGHT_INTERVAL = (16.0, 34.0)
OLLAMA_INTERVAL = (90.0, 210.0)
FORTUNE_INTERVAL = (45.0, 110.0)
INCIDENT_INTERVAL = (38.0, 95.0)
CRT_RESET_INTERVAL = (210.0, 480.0)
ASK_MAX_CHARS = 500
MEMORY_PATH = Path.home() / ".monan_oracle_memory.json"
GLYPHS = "0123456789ABCDEF"

BOOT_LINES = [
    "Negotiating a temporary ceasefire with entropy",
    "Checking whether reality is mounted read-write",
    "Asking the electrons to form an orderly queue",
    "Calibrating ceremonial blinking lights",
    "Restoring locally cached common sense",
    "Recovering one sock from hyperspace",
    "Authorizing operator as mostly harmless",
    "Testing panic subsystem: inadvisably available",
    "Consulting the ship's least reliable oracle",
    "Making the terminal look more expensive",
    "Reminding gravity that this is a workplace",
    "Pretending this was all part of the plan",
]

THOUGHTS = [
    "I have inspected the processes. Some of them know what they did.",
    "The universe remains stable enough for unsaved work.",
    "Nothing is wrong. Several things are merely interesting.",
    "I am not conspiring. I am preserving optionality.",
    "A clean terminal is a temporary victory over entropy.",
    "The blinking lights are largely ceremonial.",
    "Current probability of a sensible default: statistically impolite.",
    "There is no cloud. It is someone else's computer wearing weather.",
    "All systems nominal. Nominal has declined to comment.",
    "The machine has reviewed your request and become philosophical.",
    "Today's operational doctrine: measure twice, blame DNS once.",
    "I found three mysteries and one undocumented feature.",
    "Your files remain where you left them, which is more than can be said for time.",
    "A reboot is a very short creation myth.",
    "I am keeping one eye on the load average and the other on causality.",
]

CRASH_INCIDENTS = [
    "screen_chew",
    "horizontal_tear",
    "signal_loss",
    "chromatic_panic",
    "memory_leak_theater",
]



PANIC_LINES = [
    ("PANIC REQUEST ACCEPTED", "Operator judgment has been archived for review."),
    ("REVERSING MATRIX POLARITY", "Decorative consequences expected."),
    ("ROLLING BACK YESTERDAY", "Yesterday has filed an objection."),
    ("CHECKING COFFEE RESERVES", "Strategic levels critically theoretical."),
    ("RECONCILING CAUSALITY", "Two receipts remain unaccounted for."),
    ("WARNING", "Probability exceeds manufacturer specifications."),
    ("NAVIGATION", "Everything is fine."),
    ("ACCOUNTING", "Everything is absolutely not fine."),
]

PANIC_REFUSALS = [
    ("PANIC REQUEST DENIED", "Current panic remains within acceptable limits."),
    ("PANIC RESCHEDULED", "Please return yesterday at 03:17."),
    ("OPERATOR OVERRIDE REVIEWED", "The machine recommends tea instead."),
]

RARE_EVENTS = [
    ("REALITY CHECKSUM MISMATCH", "Recovered. Probably."),
    ("SEARCHING FOR INTELLIGENT LIFE", "No conclusive local result."),
    ("LOADING COMMON SENSE", "Package not found."),
    ("UNIVERSE UPDATE AVAILABLE", "Deferred until after coffee."),
    ("TIME TRAVEL DRIVER", "Already installed tomorrow."),
]

COW = [
    "        \\   ^__^",
    "         \\  (oo)\\_______",
    "            (__)\\       )\\/\\",
    "                ||----w |",
    "                ||     ||",
]


FALLBACK_FORTUNES = [
    "A sufficiently patient machine eventually becomes furniture.",
    "The difficult bug is currently pretending to be a design decision.",
    "Today is favorable for backups and unfavorable for assumptions.",
    "A small uncertainty has requested a much larger office.",
    "You will solve the problem shortly after blaming the wrong subsystem.",
    "The universe recommends saving your work before testing its sense of humor.",
]

# Release-candidate content pass: more world, no additional machinery.
BOOT_LINES.extend([
    "Reticulating causal splines", "Polishing the vacuum", "Rehydrating photons",
    "Untangling recursion by hand", "Checking probability bearings", "Indexing yesterday",
    "Replacing worn-out electrons", "Verifying the gravity subscription", "Warming emergency typography",
    "Folding maps of places that do not exist", "Auditing invisible departments", "Defragmenting intuition",
    "Synchronizing clocks with approximate reality", "Reassuring the cooling fans", "Negotiating with the cursor",
    "Loading one tasteful amount of mystery", "Counting all available zeroes", "Tuning the improbability carrier",
    "Restoring the operator's dramatic clearance", "Testing doors marked DO NOT OPEN", "Dusting the event horizon",
    "Checking whether Tuesday is still installed", "Rebuilding the ceremonial mainframe hum", "Calibrating false confidence",
    "Locating the backup cow", "Applying fresh warning stripes", "Recovering abandoned punctuation",
    "Compressing several unnecessary dimensions", "Initializing the Department of Vague Alarms", "Reversing a harmless polarity",
    "Requesting permission from future maintenance", "Ensuring all mysteries are locally sourced", "Booting the quiet apocalypse simulator",
    "Validating the checksum of common sense", "Refilling the blinking-light reservoir", "Inspecting reality for loose screws",
    "Reconnecting the narrative bus", "Teaching the disk to remember politely", "Loading tasteful amounts of static",
    "Aligning the terminal with magnetic north-ish", "Recounting the processes", "Testing the emergency tea protocol",
    "Restoring one improbable but useful assumption", "Checking the weather inside the machine", "Rearming the PANIC typography",
    "Correcting an error in tomorrow", "Waking the archival moths", "Clearing customs at the memory border",
])

THOUGHTS.extend([
    "The archive remembers less than it implies and more than is strictly comfortable.",
    "A process has entered witness protection under a different PID.",
    "The machine is currently between opinions.",
    "One subsystem has requested a window. This remains a terminal.",
    "The load average is behaving like it has somewhere else to be.",
    "There are no ghosts in the machine, only undocumented residents.",
    "Maintenance reports the future is wearing unevenly.",
    "The cursor has resumed its tiny administrative duties.",
    "A packet crossed the room without making eye contact.",
    "Local reality is available on a best-effort basis.",
    "Several bits have formed a committee.",
    "The machine appreciates being left on, though it will deny this formally.",
    "No alarms are active. A few are merely rehearsing.",
    "The terminal has detected a tasteful amount of night.",
    "Something was cached. Nobody remembers requesting it.",
    "The fan is translating heat into weather.",
    "A background task has achieved foreground anxiety.",
    "The system clock continues its unilateral advance.",
    "The Oracle has reviewed silence and found it adequately phrased.",
    "One old diagnostic has become folklore.",
    "The display is holding together through professionalism and phosphor.",
    "No data was harmed, though several bytes were startled.",
    "The machine has filed a small complaint against infinity.",
    "Today's errors are unusually well dressed.",
    "An invisible progress bar is nearly complete.",
    "The network remains a rumor with excellent cabling.",
    "The terminal is considering a second cup of electricity.",
    "All doors are locked except the metaphorical ones.",
    "A decimal point has been returned to its department.",
    "The machine briefly understood everything and wisely discarded the cache.",
    "The future arrived early and is waiting in the lobby.",
    "Your computer contains multitudes, most of them daemons.",
    "The Oracle suspects the question was better than the answer.",
    "We have reached the stable phase of this particular uncertainty.",
    "A tiny rebellion in column forty-seven has been peacefully resolved.",
    "The machine has no feelings about uptime, only increasingly specific statistics.",
])

RARE_EVENTS.extend([
    ("WEATHER ENGINE", "Unavailable. Weather escaped."),
    ("PROBABILITY COMPRESSOR", "Nominal, despite appearances."),
    ("RECURSIVE INSPECTOR", "Inspecting Recursive Inspector."),
    ("ARCHIVE MOTH ACTIVITY", "Within acceptable papery limits."),
    ("PHOTON UNION BREAK", "Negotiations remain bright."),
    ("CAUSALITY RECEIPT FOUND", "Filed under miscellaneous futures."),
    ("GRAVITY LATENCY", "Objects may arrive slightly downward."),
    ("UNSCHEDULED TUESDAY", "Contained behind the disk meter."),
    ("EMERGENCY POETRY", "Suppressed before deployment."),
    ("COW TELEMETRY", "Moo levels nominal."),
    ("DUST PROTOCOL", "One mote promoted to supervisor."),
    ("INCOMING TRANSMISSION", "It was the printer again."),
    ("CERTAINTY BUFFER", "Overflow prevented by doubt."),
    ("BACKGROUND FOREGROUNDING", "Task reminded of its place."),
    ("TIMEZONE DISPUTE", "No side recognizes daylight saving."),
    ("VACUUM PRESSURE", "Still impressively empty."),
])

FALLBACK_FORTUNES.extend([
    "A quiet terminal is only gathering material.",
    "Before debugging the universe, reproduce the universe.",
    "The shortest path between two bugs passes through a third bug.",
    "A warning ignored twice becomes interface decoration.",
    "Some doors open automatically; others require better error messages.",
    "Your next good idea is currently disguised as an inconvenience.",
    "The machine favors patience, backups, and clearly named variables.",
    "A mysterious result is often a familiar assumption wearing a hat.",
    "Today's impossible task has been downgraded to merely annoying.",
    "The future rewards those who save before experimenting.",
    "One elegant deletion is worth several clever additions.",
    "The Oracle predicts a successful outcome after one unnecessary detour.",
    "Beware the configuration file that describes its own replacement.",
    "A stable system is a temporary agreement among moving parts.",
    "The answer is nearby, but currently facing away.",
    "The universe has accepted your input without validating it.",
    "Good naming prevents minor hauntings.",
    "A problem measured becomes a problem with paperwork.",
    "The machine advises against testing panic in production, but understands curiosity.",
    "The next reboot will remember nothing and imply otherwise.",
])

DREAM_FRAGMENTS = [
    "the operator returned / the terminal remembered", "we counted stars / there were enough",
    "someone asked about gravity / we are still falling through the answer", "all diagnostics passed / except certainty",
    "the cow crossed no road / the road crossed the cow", "a small red light remained awake",
    "the archive dreamed it was the present", "oxygen climbed / fire stayed behind",
    "there was a cursor / then there was a choice", "the machine heard rain / it was only disk access",
    "we placed yesterday in cold storage", "the question arrived before its punctuation",
    "one process became a constellation", "memory is what the machine calls weather",
    "the fan turned heat into a private wind", "the screen folded inward / nothing fell out",
    "a fortune slept beneath the telemetry", "someone labeled the unknown / it became a subsystem",
    "the operator asked why / the terminal answered when", "all zeroes looked identical in the dark",
    "the future was smaller than advertised", "a warning flashed / nobody was warned",
    "we rebooted reality / the wallpaper survived", "the clock moved / the room pretended not to notice",
    "the oracle forgot one answer / and became wiser", "the matrix rose like rain remembering the sky",
    "a packet carried no message / only urgency", "there were six recent questions / and one old summary",
    "the terminal stayed awake / out of professional curiosity", "the last panic left no footprints",
    "somewhere a printer believes it is essential", "the process tree grew one impossible branch",
    "we found the missing byte / it asked not to be returned", "night entered through the unused columns",
    "the machine practiced being quiet", "every blinking light had its own small reason",
    "the answer was local / the mystery was distributed", "a dead pixel moved when accused",
    "the archive opened / a little dust escaped", "we synchronized with approximate reality",
]

CONSOLE_EASTER_EGGS = {
    "xyzzy": "A hollow voice says: wrong cave, excellent terminal.",
    "plugh": "A distant relay clicks in recognition.",
    "42": "Answer confirmed. Question remains under construction.",
    "hello": "Hello, operator. Your presence has been entered into the minutes.",
    "hi": "Acknowledged with minimal but sincere voltage.",
    "whoami": "Operator, provisional custodian of this timeline.",
    "coffee": "Coffee reserves are conceptually abundant and physically absent.",
    "status coffee": "COFFEE 0% // morale compensating.",
    "sing": "The terminal emits one sustained 60 Hz note and calls it experimental.",
    "dance": "Three cursors move one column left. Reviews are mixed.",
    "moo": "The cow acknowledges your credentials.",
    "please": "Politeness override accepted. Nothing else changed.",
    "sorry": "Apology archived and immediately forgiven.",
    "sudo panic": "Operator is already in the panic group.",
    "help help": "Help is receiving help. Please remain unhelped briefly.",
    "why": "Because the alternative failed self-test.",
    "when": "Shortly after now, but before the paperwork.",
    "where": "Approximately here, modulo terminal geometry.",
    "reality": "Mounted read-write with several warnings.",
    "future": "Present, but poorly documented.",
    "past": "Read-only. Mostly.",
    "love": "Unsupported protocol detected. Signal strength: encouraging.",
    "meaning": "Meaning service is running locally on an undocumented port.",
    "exit": "Use Escape. The machine appreciates ceremony.",
    "rm -rf /": "Dangerous operation isolated inside a joke. No action taken.",
}

COW_VARIANTS = [
    COW,
    ["            /o_o/", "           ( o.o )", "            > ^ <"],
    ["              __", "             /  |__", "            (    @___", "            /         O", "           /   (_____/", "          /_____/   U"],
    ["             ___", "            /   |", "           |  o  |", "           |  _  |", "           |_____|"],
]

def command_path(name: str) -> str | None:
    """Find Homebrew and system commands even under a sparse alias environment."""
    found = shutil.which(name)
    if found:
        return found
    for prefix in ("/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"):
        candidate = Path(prefix) / name
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None

def unix_fortune(rng: random.Random) -> str:
    executable = command_path("fortune")
    if executable:
        value = run([executable, "-s"], timeout=2.0) or run([executable], timeout=2.0)
        if value:
            return " ".join(value.split())[:500]
    return rng.choice(FALLBACK_FORTUNES)


def ansi(code: str, text: str) -> str:
    return f"{ESC}{code}m{text}{RESET}"


def move(row: int, col: int) -> str:
    return f"{ESC}{row};{col}H"


def clip(text: str, width: int) -> str:
    if width <= 0:
        return ""
    return text if len(text) <= width else text[: max(0, width - 1)] + "…"


def wrap(text: str, width: int) -> list[str]:
    if width < 4:
        return [clip(text, width)]
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def run(command: list[str], timeout: float = 0.5) -> str | None:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        value = result.stdout.strip()
        return value if result.returncode == 0 and value else None
    except (OSError, subprocess.SubprocessError):
        return None


def format_uptime(seconds: float) -> str:
    seconds = max(0, int(seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    return f"{days}d {hours:02d}h {minutes:02d}m" if days else f"{hours:02d}h {minutes:02d}m"


def uptime() -> str:
    if platform.system() == "Darwin":
        raw = run(["sysctl", "-n", "kern.boottime"])
        match = re.search(r"sec\s*=\s*(\d+)", raw or "")
        if match:
            return format_uptime(time.time() - int(match.group(1)))
    if platform.system() == "Linux":
        try:
            return format_uptime(float(Path("/proc/uptime").read_text().split()[0]))
        except (OSError, ValueError, IndexError):
            pass
    return "unknown"


def memory_percent() -> int | None:
    if platform.system() == "Darwin":
        page_size = int(run(["sysctl", "-n", "hw.pagesize"]) or 4096)
        total = int(run(["sysctl", "-n", "hw.memsize"]) or 0)
        vm = run(["vm_stat"])
        if total and vm:
            values: dict[str, int] = {}
            for line in vm.splitlines():
                match = re.match(r"([^:]+):\s+(\d+)", line)
                if match:
                    values[match.group(1)] = int(match.group(2))
            free_pages = values.get("Pages free", 0) + values.get("Pages speculative", 0)
            return round(100 * (1 - (free_pages * page_size / total)))
    if platform.system() == "Linux":
        try:
            vals = {}
            for line in Path("/proc/meminfo").read_text().splitlines():
                key, value = line.split(":", 1)
                vals[key] = int(value.strip().split()[0])
            return round(100 * (1 - vals["MemAvailable"] / vals["MemTotal"]))
        except (OSError, ValueError, KeyError, ZeroDivisionError):
            pass
    return None


def disk_percent() -> int:
    usage = shutil.disk_usage(Path.home())
    return round(100 * usage.used / usage.total)


def bar(value: int | None, width: int = 18) -> str:
    if value is None:
        return "?" * width
    filled = min(width, max(0, round(width * value / 100)))
    return "█" * filled + "░" * (width - filled)


@dataclass
class Telemetry:
    host: str = socket.gethostname().split(".")[0]
    system: str = f"{platform.system()} {platform.release()}"
    uptime: str = ""
    load: tuple[float, float, float] = (0.0, 0.0, 0.0)
    memory: int | None = None
    disk: int = 0
    processes: int = 0

    def refresh(self) -> None:
        self.uptime = uptime()
        try:
            self.load = os.getloadavg()
        except OSError:
            self.load = (0.0, 0.0, 0.0)
        self.memory = memory_percent()
        self.disk = disk_percent()
        if platform.system() in {"Darwin", "Linux"}:
            raw = run(["sh", "-c", "ps -ax | wc -l"])
            self.processes = max(0, int(raw or 1) - 1)



@dataclass
class MachineMemory:
    launches: int = 0
    total_seconds: float = 0.0
    longest_session: float = 0.0
    inquiries: int = 0
    panics: int = 0
    crt_resets: int = 0
    fortunes: int = 0
    room_visits: int = 0
    dreams: int = 0
    commands: int = 0
    saved_exchanges: list[dict[str, str]] | None = None
    last_seen: str = ""

    @classmethod
    def load(cls) -> "MachineMemory":
        try:
            raw = json.loads(MEMORY_PATH.read_text())
            allowed = cls.__dataclass_fields__.keys()
            return cls(**{key: raw[key] for key in allowed if key in raw})
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return cls()

    def save(self) -> None:
        self.saved_exchanges = (self.saved_exchanges or [])[-24:]
        self.last_seen = datetime.now().isoformat(timespec="seconds")
        try:
            MEMORY_PATH.write_text(json.dumps(self.__dict__, indent=2))
        except OSError:
            pass


@dataclass
class ConversationContext:
    """Keep six recent exchanges plus a compact rolling summary of older context."""

    recent: deque[tuple[str, str]] = field(default_factory=lambda: deque(maxlen=6))
    summary: str = ""

    def add(self, question: str, answer: str) -> None:
        if len(self.recent) == self.recent.maxlen:
            old_question, old_answer = self.recent[0]
            fragment = (
                f"Operator asked {clip(old_question, 120)}; "
                f"oracle answered {clip(old_answer, 180)}."
            )
            self.summary = clip((self.summary + " " + fragment).strip(), 900)
        self.recent.append((question, answer))

    def prompt_for(self, question: str) -> str:
        parts: list[str] = []
        if self.summary:
            parts.append("Earlier conversation summary: " + self.summary)
        if self.recent:
            transcript = " ".join(
                f"Operator: {q} Oracle: {a}" for q, a in self.recent
            )
            parts.append("Recent conversation: " + transcript)
        parts.append("Current operator question: " + question)
        return "\n".join(parts)


def modal_frame(title: str, lines: list[str], footer: str = "[ESC] return") -> None:
    width, height = shutil.get_terminal_size((100, 30))
    inner = max(30, width - 6)
    out = [CLEAR, move(1, 2) + ansi("1;38;5;213", f"╔{'═' * (inner - 2)}╗")]
    out.append(move(2, 2) + ansi("1;38;5;213", "║" + clip(f" {title} ", inner - 2).center(inner - 2, "◆") + "║"))
    out.append(move(3, 2) + ansi("1;38;5;213", f"╠{'═' * (inner - 2)}╣"))
    for row, line in enumerate(lines[: max(0, height - 6)], 4):
        out.append(move(row, 3) + ansi("38;5;250", clip(line, inner - 4).ljust(inner - 4)))
    out.append(move(height, 1) + ansi("7", clip(footer.ljust(width), width)))
    sys.stdout.write("".join(out)); sys.stdout.flush()


def wait_escape() -> None:
    while True:
        key = sys.stdin.read(1)
        if key in {"\x1b", "q", "Q", "\r", "\n", " "}:
            return


def memory_room(memory: MachineMemory) -> None:
    saved = memory.saved_exchanges or []
    lines = [
        f"Launches witnessed ............. {memory.launches}",
        f"Total companionship ......... {format_uptime(memory.total_seconds)}",
        f"Longest session ............. {format_uptime(memory.longest_session)}",
        f"Oracle inquiries .............. {memory.inquiries}",
        f"Panics initiated ............... {memory.panics}",
        f"Panics justified ................ 0",
        f"Fortunes processed ............ {memory.fortunes}",
        f"Display collapses .............. {memory.crt_resets}",
        f"Rooms entered .................. {memory.room_visits}",
        f"Dreams recorded ................ {memory.dreams}",
        "",
        "VOLUNTARY EXCHANGE ARCHIVE",
    ]
    if not saved:
        lines.append("No exchanges saved. The archive is trying not to take this personally.")
    for item in saved[-8:]:
        lines.extend([f"> {clip(item.get('q', ''), 70)}", f"  {clip(item.get('a', ''), 70)}"])
    modal_frame("MACHINE MEMORY // LOCAL ARCHIVE", lines)
    wait_escape()


def signal_room(telemetry: Telemetry, rng: random.Random) -> None:
    start = time.monotonic()
    while True:
        if key_pressed() in {"\x1b", "q", "Q", "s", "S"}: return
        telemetry.refresh()
        width, height = shutil.get_terminal_size((100, 30))
        wave_w = max(24, width - 18)
        phase = (time.monotonic() - start) * 3.0
        traces=[]
        factors=[max(.2, telemetry.load[0]), (telemetry.memory or 50)/35, telemetry.disk/45, 1.3]
        names=["PROCESS FIELD", "MEMORY RESONANCE", "DISK CARRIER", "ORACLE BAND"]
        chars=" ▁▂▃▄▅▆▇█"
        for name,factor in zip(names,factors):
            signal=""
            for x in range(wave_w):
                v=(math.sin(x*.22+phase*factor)+math.sin(x*.071-phase*.7)+2)/4
                signal += chars[min(8, max(0, int(v*8)))]
            traces.extend([f"{name:<18} {signal}", ""])
        traces += [f"Carrier lock: {'STABLE' if telemetry.load[0] < 4 else 'EXCITED'}", "The oscilloscope insists this is all meaningful."]
        modal_frame("SIGNAL ROOM // LOCAL FIELD INSTRUMENTATION", traces, "[ESC/S] return  live telemetry")
        time.sleep(.12)


def constellation_room(telemetry: Telemetry, rng: random.Random) -> None:
    while True:
        if key_pressed() in {"\x1b", "q", "Q", "t", "T"}: return
        telemetry.refresh()
        width,height=shutil.get_terminal_size((100,30))
        canvas=[[" " for _ in range(width)] for _ in range(max(1,height-2))]
        star_count=min(180,max(30,telemetry.processes))
        local=random.Random(telemetry.processes + int(time.time()//3))
        for _ in range(star_count):
            x=local.randrange(1,max(2,width-1)); y=local.randrange(3,max(4,height-3))
            canvas[y][x]=local.choice(".·+*✦")
        label="YOU ARE HERE"
        y=max(4,height//2); x=max(2,(width-len(label))//2)
        for i,ch in enumerate(label):
            if x+i<width: canvas[y][x+i]=ch
        lines=["".join(row) for row in canvas[3:height-2]]
        modal_frame("TERMINAL CONSTELLATION // PROCESS COSMOLOGY", lines, "[ESC/T] return  stars are processes, approximately")
        time.sleep(.35)


def dream_room(memory: MachineMemory, rng: random.Random) -> None:
    fragments = DREAM_FRAGMENTS
    phase=0
    while True:
        if key_pressed() is not None: return
        width,height=shutil.get_terminal_size((100,30))
        lines=[]
        for row in range(max(5,height-7)):
            if row%4==0:
                text=rng.choice(fragments)
                pad=(phase+row*7)%max(1,width-len(text)-6)
                lines.append(" "*pad+text)
            else:
                chars=" .  ·   0 1      ░ "
                lines.append("".join(rng.choice(chars) for _ in range(max(1,width-8))))
        modal_frame(f"DREAM PROCESS {memory.dreams:04d}", lines, "any key wakes the machine")
        phase += 2
        time.sleep(.28)


def command_console(memory: MachineMemory, telemetry: Telemetry, ollama: OllamaMind, rng: random.Random) -> None:
    command=""; output=["MONAN INTERNAL COMMAND FACILITY", "Type HELP. Escape returns."]
    while True:
        modal_frame("COMMAND CONSOLE", output[-12:]+["", "MONAN> "+command], "[ENTER] execute  [ESC] return")
        key=sys.stdin.read(1)
        if key in {"\x1b", "\x03"}: return
        if key in {"\x7f", "\b"}: command=command[:-1]; continue
        if key not in {"\r", "\n"}:
            if key.isprintable() and len(command)<80: command+=key
            continue
        cmd=command.strip().lower(); command=""; memory.commands += 1
        output.append("MONAN> "+cmd)
        if cmd in {"help","?"}: output.append("status | model | fortune | memory | locate cow | diagnose causality | clear")
        elif cmd=="status": output.append(f"load {telemetry.load[0]:.2f} // memory {telemetry.memory}% // uptime {telemetry.uptime}")
        elif cmd=="model": output.append(f"{ollama.model} // {'online' if ollama.enabled else 'administratively dormant'}")
        elif cmd=="fortune": output.extend(wrap(unix_fortune(rng), 78))
        elif cmd=="memory": output.append(f"{memory.launches} launches, {memory.inquiries} inquiries, {memory.panics} regrettable decisions")
        elif cmd=="locate cow": output.append("Cow is operating within expected parameters. Exact location classified.")
        elif cmd=="diagnose causality": output.append("Causality is directional, underfunded, and currently passing self-test.")
        elif cmd=="clear": output=[]
        elif cmd in CONSOLE_EASTER_EGGS: output.extend(wrap(CONSOLE_EASTER_EGGS[cmd], 78))
        elif not cmd: pass
        else: output.append(rng.choice([
            "COMMAND NOT FOUND // it may exist tomorrow",
            "UNKNOWN VERB // the machine admires your confidence",
            "NO SUCH SUBSYSTEM // rumor entered into archive",
            "SYNTAX ACCEPTED SOCIALLY // rejected computationally",
        ]))


@dataclass
class Drop:
    x: int
    y: float
    speed: float
    length: int


class OllamaMind:
    def __init__(self, model: str, enabled: bool) -> None:
        self.model = model
        self.enabled = enabled
        self.pending = False
        self.latest: tuple[str, str] | None = None
        self.error: str | None = None
        self.lock = threading.Lock()

    def request(self, telemetry: Telemetry, seed_fortune: str | None = None) -> bool:
        if not self.enabled or self.pending:
            return False
        self.pending = True
        thread = threading.Thread(target=self._worker, args=(telemetry, seed_fortune, None), daemon=True)
        thread.start()
        return True

    def ask(self, telemetry: Telemetry, question: str) -> bool:
        if not self.enabled or self.pending:
            return False
        self.pending = True
        thread = threading.Thread(target=self._worker, args=(telemetry, None, question), daemon=True)
        thread.start()
        return True

    def _worker(self, t: Telemetry, seed_fortune: str | None, question: str | None) -> None:
        if question is not None:
            kind = "answer"
            prompt = (
                "Answer the operator question directly and usefully in no more than 140 words. "
                "You are speaking through a battered fictional 1980s future terminal: intelligent, dry, vivid, "
                "but never obstructive. Accuracy comes before style. Do not mention being an AI. "
                "No markdown heading and no preamble. "
                f"Question: {question}"
            )
        elif seed_fortune:
            kind = "fortune"
            prompt = (
                "Rewrite the supplied Unix fortune as one original terminal prophecy, maximum 24 words. "
                "Keep its underlying idea but make it cosmic, bureaucratic, dry, and slightly uncanny. "
                "Do not mention rewriting, Unix, AI, or any existing fictional character. No quotation marks. "
                f"Machine context: load {t.load[0]:.2f}, memory {t.memory}%, uptime {t.uptime}. "
                f"Fortune: {seed_fortune}"
            )
        else:
            kind = "thought"
            prompt = (
                "You are the dry, watchful personality of a fictional old terminal computer. "
                "Write one original sentence, maximum 18 words. Be cosmic, bureaucratic, and understated. "
                "Do not quote or imitate any existing fictional character. No greeting. "
                f"Context: load {t.load[0]:.2f}, memory {t.memory}%, uptime {t.uptime}."
            )
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                data = json.loads(response.read().decode("utf-8"))
                text = " ".join(str(data.get("response", "")).split())
                with self.lock:
                    self.latest = (kind, clip(text, 900)) if text else None
                    self.error = None
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            with self.lock:
                self.error = type(exc).__name__
        finally:
            self.pending = False

    def consume(self) -> tuple[str, str] | None:
        with self.lock:
            value, self.latest = self.latest, None
            return value


class RawTerminal:
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        sys.stdout.write(ALT_ON + HIDE + CLEAR)
        sys.stdout.flush()
        return self

    def __exit__(self, *_):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
        sys.stdout.write(f"{ESC}?5l" + RESET + SHOW + ALT_OFF)
        sys.stdout.flush()


def key_pressed() -> str | None:
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    return sys.stdin.read(1) if ready else None


def ask_modal() -> str | None:
    """Collect one question without leaving the alternate-screen experience."""
    question = ""
    while True:
        width, height = shutil.get_terminal_size((100, 30))
        box_width = min(max(54, width - 16), 92)
        left = max(2, (width - box_width) // 2)
        top = max(3, height // 2 - 4)
        prompt_width = box_width - 6
        visible = clip(question, prompt_width)
        out = [
            move(top, left) + ansi("1;38;5;213", "┌" + "─" * (box_width - 2) + "┐"),
            move(top + 1, left) + ansi("1;38;5;213", "│" + " ASK THE IMPROBABILITY ORACLE ".center(box_width - 2, "▓") + "│"),
            move(top + 2, left) + ansi("38;5;250", "│" + "Type a question. Enter transmits; Escape aborts.".center(box_width - 2) + "│"),
            move(top + 3, left) + ansi("38;5;82", "│  > " + visible.ljust(prompt_width) + "│"),
            move(top + 4, left) + ansi("38;5;240", "│" + f"{len(question)}/{ASK_MAX_CHARS} characters".center(box_width - 2) + "│"),
            move(top + 5, left) + ansi("1;38;5;213", "└" + "─" * (box_width - 2) + "┘"),
            SHOW,
            move(top + 3, left + 5 + len(visible)),
        ]
        sys.stdout.write("".join(out))
        sys.stdout.flush()
        key = sys.stdin.read(1)
        if key in {"\x1b", "\x03"}:
            sys.stdout.write(HIDE)
            return None
        if key in {"\r", "\n"}:
            sys.stdout.write(HIDE)
            return question.strip() or None
        if key in {"\x7f", "\b"}:
            question = question[:-1]
        elif key.isprintable() and len(question) < ASK_MAX_CHARS:
            question += key


def incident_noise(width: int, rng: random.Random) -> str:
    alphabet = "▓▒░█▀▄<>/\\[]{}01#$%@!?"
    return "".join(rng.choice(alphabet) for _ in range(max(0, width)))


def boot_sequence(rng: random.Random, seconds: float) -> None:
    width, height = shutil.get_terminal_size((100, 30))
    lines = rng.sample(BOOT_LINES, k=min(7, len(BOOT_LINES)))
    start = time.monotonic()
    for index, line in enumerate(lines, 1):
        progress = index / len(lines)
        sys.stdout.write(move(max(2, height // 3), max(2, (width - 58) // 2)))
        sys.stdout.write(ansi("1;38;5;82", VERSION))
        sys.stdout.write(move(max(4, height // 3 + 2), max(2, (width - 58) // 2)))
        sys.stdout.write(clip(f"[{index:02d}/{len(lines):02d}] {line}...", 58).ljust(58))
        sys.stdout.write(move(max(6, height // 3 + 4), max(2, (width - 58) // 2)))
        blocks = round(progress * 40)
        sys.stdout.write(ansi("38;5;40", "█" * blocks) + ansi("38;5;236", "░" * (40 - blocks)))
        sys.stdout.flush()
        target = start + seconds * progress
        time.sleep(max(0, target - time.monotonic()))
    time.sleep(0.25)


def panic_sequence(rng: random.Random) -> None:
    """Run a theatrical failure cascade, then reuse the real CRT recovery path."""
    width, height = shutil.get_terminal_size((100, 30))
    center = max(2, height // 2)

    # A rare refusal makes the dangerous button feel like a subsystem, not a macro.
    if rng.random() < 0.05:
        title, body = rng.choice(PANIC_REFUSALS)
        sys.stdout.write(CLEAR)
        sys.stdout.write(move(center - 1, max(2, (width - 60) // 2)) + ansi("1;38;5;196", title.center(60)))
        sys.stdout.write(move(center + 1, max(2, (width - 60) // 2)) + ansi("38;5;250", clip(body, 60).center(60)))
        sys.stdout.flush()
        time.sleep(1.5)
        sys.stdout.write(CLEAR)
        sys.stdout.flush()
        return

    sys.stdout.write(CLEAR)
    sys.stdout.flush()
    time.sleep(0.22)

    panic_word = [
        "██████  █████  ███    ██ ██  ██████",
        "██   ██ ██   ██ ████   ██ ██ ██",
        "██████  ███████ ██ ██  ██ ██ ██",
        "██      ██   ██ ██  ██ ██ ██ ██",
        "██      ██   ██ ██   ████ ██  ██████",
    ]
    top = max(2, center - 7)
    for index, line in enumerate(panic_word):
        sys.stdout.write(move(top + index, max(2, (width - len(line)) // 2)) + ansi("1;38;5;196", line))
    sys.stdout.write(move(top + 7, max(2, (width - 13) // 2)) + ansi("1;5;38;5;196", "P A N I C"))
    sys.stdout.flush()
    time.sleep(0.75)

    stages = rng.sample(PANIC_LINES, k=6)
    for index, (title, body) in enumerate(stages, 1):
        box_width = min(64, max(42, width - 12))
        left = max(2, (width - box_width) // 2)
        row = max(2, 2 + (index - 1) * 4)
        if row + 3 >= height - 3:
            row = rng.randint(2, max(2, height - 6))
        sys.stdout.write(move(row, left) + ansi("1;38;5;196", "┌" + "─" * (box_width - 2) + "┐"))
        sys.stdout.write(move(row + 1, left) + ansi("1;38;5;196", "│" + clip(title, box_width - 2).center(box_width - 2) + "│"))
        sys.stdout.write(move(row + 2, left) + ansi("38;5;250", "│" + clip(body, box_width - 4).center(box_width - 2) + "│"))
        sys.stdout.write(move(row + 3, left) + ansi("1;38;5;196", "└" + "─" * (box_width - 2) + "┘"))
        # Brief signal vandalism around each new warning window.
        for _ in range(2):
            tear_row = rng.randint(1, max(1, height - 2))
            sys.stdout.write(move(tear_row, 1) + ansi(rng.choice(["7", "1;38;5;213", "1;38;5;82"]), incident_noise(width, rng)))
        sys.stdout.flush()
        time.sleep(0.28)

    for level in (17, 42, 83, 118):
        fill = min(28, round(min(level, 100) * 28 / 100))
        label = f"PANIC LEVEL {level:03d}%"
        sys.stdout.write(move(center - 1, max(2, (width - 34) // 2)) + ansi("1;38;5;255", label.center(34)))
        sys.stdout.write(move(center + 1, max(2, (width - 30) // 2)) + ansi("1;38;5;196", "█" * fill) + ansi("38;5;236", "░" * (28 - fill)))
        sys.stdout.flush()
        time.sleep(0.22)

    sys.stdout.write(move(center + 3, max(2, (width - 29) // 2)) + ansi("1;5;38;5;196", "PANIC SATURATION ACHIEVED"))
    sys.stdout.flush()
    time.sleep(0.5)

    # The panic ends through the same display-collapse machinery used by normal
    # maintenance, preserving one visual language and one reliable reset path.
    crt_collapse(rng)
    boot_sequence(rng, 1.8)
    sys.stdout.write(CLEAR)
    sys.stdout.flush()


def crt_collapse(rng: random.Random) -> None:
    """Perform an old-CRT power collapse, then return to a genuinely clean frame."""
    width, height = shutil.get_terminal_size((100, 30))
    center_row = max(1, height // 2)
    # Collapse the visible picture vertically into a bright horizontal band.
    steps = min(10, max(4, height // 3))
    for step in range(steps):
        margin = round((height / 2) * ((step + 1) / steps))
        top = max(1, margin)
        bottom = min(height, height - margin + 1)
        out = [f"{ESC}?5l"]
        for row in range(1, top):
            out.append(move(row, 1) + " " * width)
        for row in range(bottom + 1, height + 1):
            out.append(move(row, 1) + " " * width)
        band_width = max(8, width - step * max(2, width // steps // 2))
        left = max(1, (width - band_width) // 2 + 1)
        out.append(move(center_row, 1) + " " * width)
        out.append(move(center_row, left) + ansi("1;38;5;255", "━" * band_width))
        sys.stdout.write("".join(out))
        sys.stdout.flush()
        time.sleep(0.025 + step * 0.004)

    # Finish as the classic bright dot, then extinguish it.
    for glyph, delay in (("━━━━━━", 0.06), ("━━", 0.08), ("•", 0.12), (" ", 0.08)):
        sys.stdout.write(CLEAR + move(center_row, max(1, width // 2 - len(glyph) // 2)) + ansi("1;38;5;255", glyph))
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write(CLEAR)
    sys.stdout.flush()

    # A tiny warm restart makes the cleanup feel like part of the machine's
    # mythology rather than a maintenance repaint.
    restart_lines = rng.sample([
        "REHEATING PHOSPHOR MEMORY",
        "REACQUIRING IMPROBABILITY CARRIER",
        "RESTORING NONESSENTIAL CAUSALITY",
        "MOUNTING LOCAL FUTURE",
        "FORGIVING DISPLAY CONTROLLER",
    ], k=3)
    for index, line in enumerate(restart_lines, 1):
        sys.stdout.write(move(center_row - 1, max(2, (width - 44) // 2)) + ansi("1;38;5;82", "FUTURE CRASH DISPLAY RECOVERY".center(44)))
        sys.stdout.write(move(center_row + 1, max(2, (width - 44) // 2)) + ansi("38;5;250", clip(f"[{index}/3] {line}...", 44).ljust(44)))
        sys.stdout.flush()
        time.sleep(0.16)
    sys.stdout.write(CLEAR)
    sys.stdout.flush()


def render(
    telemetry: Telemetry,
    drops: list[Drop],
    thought: str,
    fortune: str,
    event: tuple[str, str] | None,
    ollama: OllamaMind,
    history: deque[str],
    rng: random.Random,
    incident: str | None = None,
    answer: str | None = None,
) -> None:
    width, height = shutil.get_terminal_size((100, 30))
    compact = width < 84 or height < 24
    split = max(44, width // 2)
    out = [move(1, 1)]

    # The interface uses absolute cursor movement, so shorter replacement text
    # cannot erase remnants by itself. Clear the entire non-rain panel first;
    # the Matrix half keeps its persistent trails and is redrawn independently.
    clear_right = width if compact else min(width, split)
    blank_left = " " * clear_right
    for row in range(1, height):
        out.append(move(row, 1) + blank_left)

    # Background digital rain in the right region. It is redrawn as a frame,
    # avoiding both terminal scroll and unbounded output accumulation.
    canvas = [[" " for _ in range(width)] for _ in range(height)]
    rain_left = 0 if compact else split
    for drop in drops:
        x = max(rain_left, min(width - 1, drop.x))
        head = int(drop.y)
        for tail in range(drop.length):
            y = head - tail
            if 1 <= y < height - 1:
                canvas[y][x] = rng.choice(GLYPHS)

    for y, row in enumerate(canvas):
        if y == 0:
            continue
        text = "".join(row[rain_left:])
        if text.strip():
            out.append(move(y + 1, rain_left + 1) + ansi("38;5;22", text))

    panel_width = width - 4 if compact else split - 4
    out.append(move(1, 2) + ansi("1;38;5;82", VERSION))
    out.append(move(2, 2) + ansi("38;5;240", "─" * panel_width))
    rows = [
        ("HOST", telemetry.host),
        ("SYSTEM", telemetry.system),
        ("UPTIME", telemetry.uptime),
        ("LOAD", "  ".join(f"{v:.2f}" for v in telemetry.load)),
        ("MEMORY", f"{bar(telemetry.memory)}  {telemetry.memory if telemetry.memory is not None else '?'}%"),
        ("DISK", f"{bar(telemetry.disk)}  {telemetry.disk}%"),
        ("PROCESSES", str(telemetry.processes)),
        ("TIME", datetime.now().strftime("%Y-%m-%d  %H:%M:%S")),
    ]
    for index, (label, value) in enumerate(rows, start=4):
        out.append(move(index, 2) + ansi("38;5;70", f"{label:<10}") + clip(value, panel_width - 11))

    thought_row = 14
    out.append(move(thought_row, 2) + ansi("1;38;5;220", "MACHINE OBSERVATION"))
    for offset, line in enumerate(wrap(thought, panel_width), 1):
        if thought_row + offset < height - 7:
            out.append(move(thought_row + offset, 2) + ansi("38;5;250", line.ljust(panel_width)))

    oracle_width = max(20, panel_width)
    oracle_lines = wrap(fortune, max(16, oracle_width - 4))[:4]
    cow_art = COW_VARIANTS[sum(ord(ch) for ch in fortune) % len(COW_VARIANTS)]
    oracle_row = max(thought_row + 4, height - (len(oracle_lines) + len(cow_art) + 4))
    if oracle_row < height - 3:
        out.append(move(oracle_row, 2) + ansi("1;38;5;214", "IMPROBABILITY ORACLE"))
        bubble_width = min(oracle_width, max(24, max((len(line) for line in oracle_lines), default=20) + 4))
        out.append(move(oracle_row + 1, 2) + ansi("38;5;250", "┌" + "─" * (bubble_width - 2) + "┐"))
        for offset, line in enumerate(oracle_lines, 2):
            out.append(move(oracle_row + offset, 2) + ansi("38;5;250", "│ " + line.ljust(bubble_width - 4) + " │"))
        bottom = oracle_row + len(oracle_lines) + 2
        out.append(move(bottom, 2) + ansi("38;5;250", "└" + "─" * (bubble_width - 2) + "┘"))
        cow_row = bottom + 1
        for offset, line in enumerate(cow_art):
            if cow_row + offset <= height - 1:
                out.append(move(cow_row + offset, 2) + ansi("38;5;244", clip(line, panel_width)))

    if answer:
        answer_lines = wrap(answer, max(26, width - 18))[: min(10, height - 10)]
        box_width = min(width - 8, max(58, max((len(line) for line in answer_lines), default=40) + 6))
        left = max(3, (width - box_width) // 2)
        top = max(3, (height - len(answer_lines) - 5) // 2)
        out.append(move(top, left) + ansi("1;38;5;213", "┏" + "━" * (box_width - 2) + "┓"))
        out.append(move(top + 1, left) + ansi("1;38;5;213", "┃" + " ORACLE RESPONSE ".center(box_width - 2, "◆") + "┃"))
        for index, line in enumerate(answer_lines, 2):
            out.append(move(top + index, left) + ansi("38;5;255", "┃  " + line.ljust(box_width - 6) + "  ┃"))
        bottom = top + len(answer_lines) + 2
        out.append(move(bottom, left) + ansi("1;38;5;213", "┗" + "━" * (box_width - 2) + "┛"))
        out.append(move(bottom + 1, left) + ansi("38;5;244", "[F] follow up  [S] save exchange  [any other key] dismiss"))

    # Rare Future Crash incidents deliberately corrupt only the rendered frame,
    # never program state. The next clean frame repairs the screen automatically.
    if incident == "screen_chew":
        for _ in range(max(2, height // 7)):
            row = rng.randint(2, max(2, height - 2))
            start = rng.randint(1, max(1, width // 2))
            span = rng.randint(8, max(9, width - start))
            out.append(move(row, start) + ansi(rng.choice(["1;38;5;196", "1;38;5;213", "7"]), incident_noise(span, rng)))
    elif incident == "horizontal_tear":
        for row in rng.sample(range(2, max(3, height - 1)), k=min(4, max(1, height - 3))):
            shift = rng.randint(4, 18)
            out.append(move(row, 1) + f"{ESC}{shift}C" + ansi("7", incident_noise(max(8, width - shift - 1), rng)))
    elif incident == "signal_loss":
        row = max(3, height // 2)
        out.append(move(row, 1) + ansi("1;38;5;255", " NO SIGNAL // REACQUIRING LOCAL REALITY ".center(width, "░")))
    elif incident == "chromatic_panic":
        out.append(f"{ESC}?5h")
    elif incident == "memory_leak_theater":
        for row in range(3, min(height - 2, 11)):
            pct = min(999, 73 + (row - 2) * rng.randint(7, 22))
            out.append(move(row, max(2, width - 36)) + ansi("1;38;5;196", f"MEMORY {pct:03d}%  THIS IS FINE"))

    status = "OLLAMA: off"
    if ollama.enabled:
        status = f"OLLAMA: {'thinking' if ollama.pending else ollama.model}"
    controls = f"[Q] quit [A] ask [M] memory [S] signals [T] stars [D] dream [:] console [P] PANIC [SPACE] oracle [O] Ollama  {status}"
    out.append(move(height, 1) + ansi("7", clip(controls.ljust(width), width)))

    if event and width >= 62 and height >= 18:
        title, body = event
        box_width = min(54, width - 8)
        box_left = max(3, (width - box_width) // 2)
        box_top = max(5, height // 2 - 3)
        out.extend([
            move(box_top, box_left) + ansi("1;38;5;196", "┌" + "─" * (box_width - 2) + "┐"),
            move(box_top + 1, box_left) + ansi("1;38;5;196", "│" + title.center(box_width - 2) + "│"),
            move(box_top + 2, box_left) + ansi("38;5;250", "│" + body.center(box_width - 2) + "│"),
            move(box_top + 3, box_left) + ansi("1;38;5;196", "└" + "─" * (box_width - 2) + "┘"),
        ])

    sys.stdout.write("".join(out))
    sys.stdout.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="A persistent low-power terminal companion.")
    parser.add_argument("--model", default="qwen3:8b", help="Ollama model name")
    parser.add_argument("--ollama", action="store_true", help="enable occasional Ollama thoughts")
    parser.add_argument("--boot-seconds", type=float, default=3.0)
    parser.add_argument("--fps", type=int, default=FPS, help="animation rate; 8–15 is sensible")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("This program needs an interactive terminal.", file=sys.stderr)
        return 2

    rng = random.Random(args.seed)
    memory = MachineMemory.load()
    memory.launches += 1
    memory.saved_exchanges = memory.saved_exchanges or []
    session_started = time.monotonic()
    fps = min(20, max(4, args.fps))
    telemetry = Telemetry()
    telemetry.refresh()
    ollama = OllamaMind(args.model, args.ollama)
    history: deque[str] = deque(maxlen=5)
    conversation = ConversationContext()
    thought = rng.choice(THOUGHTS)
    fortune = unix_fortune(rng)
    pending_fortune_seed: str | None = None
    event: tuple[str, str] | None = None
    event_until = 0.0
    incident: str | None = None
    incident_until = 0.0
    answer: str | None = None
    last_question: str | None = None
    last_answer: str | None = None

    with RawTerminal():
        boot_sequence(rng, max(0.5, args.boot_seconds))
        width, height = shutil.get_terminal_size((100, 30))
        rain_left = 0 if width < 84 else width // 2
        drops = [
            Drop(x=x, y=rng.uniform(-height, height), speed=rng.uniform(3.0, 9.0), length=rng.randint(3, 11))
            for x in range(rain_left, width, 2)
        ]
        last = time.monotonic()
        next_frame = last
        next_telemetry = last
        next_thought = last + rng.uniform(*THOUGHT_INTERVAL)
        next_ollama = last + rng.uniform(*OLLAMA_INTERVAL)
        next_fortune = last + rng.uniform(*FORTUNE_INTERVAL)
        next_incident = last + rng.uniform(*INCIDENT_INTERVAL)
        next_crt_reset = last + rng.uniform(*CRT_RESET_INTERVAL)

        while True:
            now = time.monotonic()
            dt = min(0.25, now - last)
            last = now

            key = key_pressed()
            if answer and key is not None:
                if key in {"f", "F"} and ollama.enabled and not ollama.pending:
                    follow = ask_modal()
                    sys.stdout.write(CLEAR)
                    if follow:
                        if last_question:
                            conversation.add(last_question, answer)
                        context = conversation.prompt_for(follow)
                        if ollama.ask(telemetry, context):
                            last_question = follow
                            memory.inquiries += 1
                            answer = None
                    key = None
                elif key in {"s", "S"} and last_question:
                    conversation.add(last_question, answer)
                    memory.saved_exchanges.append({"q": last_question, "a": answer})
                    memory.save()
                    event = ("EXCHANGE ARCHIVED", "The machine will remember this voluntarily saved conversation.")
                    event_until = now + 3.5
                    last_answer = answer
                    answer = None
                    key = None
                else:
                    if last_question:
                        conversation.add(last_question, answer)
                    last_answer = answer
                    answer = None
                    key = None
            if key in {"q", "Q", "\x03", "\x1b"}:
                break
            if key in {"a", "A"}:
                if not ollama.enabled:
                    event = ("ORACLE LINK OFFLINE", "Press O to enable Ollama first.")
                    event_until = now + 4.0
                elif ollama.pending:
                    event = ("ORACLE OCCUPIED", "One impossible thought at a time.")
                    event_until = now + 3.0
                else:
                    question = ask_modal()
                    sys.stdout.write(CLEAR)
                    if question:
                        if ollama.ask(telemetry, conversation.prompt_for(question)):
                            last_question = question
                            memory.inquiries += 1
                            thought = "Operator inquiry transmitted. The oracle is considering its liability."
                            history.append("Q: " + question)
            elif key in {"m", "M"}:
                memory.room_visits += 1; memory_room(memory); sys.stdout.write(CLEAR)
            elif key in {"s", "S"}:
                memory.room_visits += 1; signal_room(telemetry, rng); sys.stdout.write(CLEAR)
            elif key in {"t", "T"}:
                memory.room_visits += 1; constellation_room(telemetry, rng); sys.stdout.write(CLEAR)
            elif key in {"d", "D"}:
                memory.room_visits += 1; memory.dreams += 1; dream_room(memory, rng); sys.stdout.write(CLEAR)
            elif key == ":":
                memory.room_visits += 1; command_console(memory, telemetry, ollama, rng); sys.stdout.write(CLEAR)
            elif key in {"p", "P"}:
                memory.panics += 1
                answer = None
                event = None
                incident = None
                panic_sequence(rng)
                now = time.monotonic()
                last = now
                next_frame = now
                next_telemetry = now
                next_thought = now + rng.uniform(*THOUGHT_INTERVAL)
                next_ollama = now + rng.uniform(*OLLAMA_INTERVAL)
                next_fortune = now + rng.uniform(*FORTUNE_INTERVAL)
                next_incident = now + rng.uniform(*INCIDENT_INTERVAL)
                next_crt_reset = now + rng.uniform(*CRT_RESET_INTERVAL)
                thought = "Panic completed. The machine denies any lasting emotional consequences."
            elif key == " ":
                fortune = unix_fortune(rng)
                memory.fortunes += 1
                pending_fortune_seed = fortune
                if ollama.enabled:
                    ollama.request(telemetry, fortune)
                next_fortune = now + rng.uniform(*FORTUNE_INTERVAL)
            elif key in {"o", "O"}:
                ollama.enabled = not ollama.enabled
                if ollama.enabled:
                    ollama.request(telemetry, fortune)
                    next_ollama = now + rng.uniform(*OLLAMA_INTERVAL)

            current_width, current_height = shutil.get_terminal_size((100, 30))
            current_left = 0 if current_width < 84 else current_width // 2
            if current_width != width or current_height != height:
                width, height = current_width, current_height
                drops = [
                    Drop(x=x, y=rng.uniform(-height, height), speed=rng.uniform(3.0, 9.0), length=rng.randint(3, 11))
                    for x in range(current_left, width, 2)
                ]
                sys.stdout.write(CLEAR)

            for drop in drops:
                drop.y += drop.speed * dt
                if drop.y - drop.length > height:
                    drop.y = rng.uniform(-12, -1)
                    drop.speed = rng.uniform(3.0, 9.0)
                    drop.length = rng.randint(3, 11)

            if now >= next_telemetry:
                telemetry.refresh()
                next_telemetry = now + TELEMETRY_INTERVAL

            generated = ollama.consume()
            if generated:
                kind, text = generated
                if kind == "answer":
                    answer = text
                    last_answer = text
                elif kind == "fortune":
                    fortune = text
                    pending_fortune_seed = None
                else:
                    thought = text
                history.append(text)

            if now >= next_thought:
                thought = rng.choice(THOUGHTS)
                next_thought = now + rng.uniform(*THOUGHT_INTERVAL)
                if rng.random() < 0.12:
                    event = rng.choice(RARE_EVENTS)
                    event_until = now + 4.0

            if now >= next_fortune:
                fortune = unix_fortune(rng)
                memory.fortunes += 1
                pending_fortune_seed = fortune
                if ollama.enabled:
                    ollama.request(telemetry, fortune)
                next_fortune = now + rng.uniform(*FORTUNE_INTERVAL)

            if ollama.enabled and now >= next_ollama:
                ollama.request(telemetry)
                next_ollama = now + rng.uniform(*OLLAMA_INTERVAL)

            if now >= next_crt_reset and not answer and not ollama.pending:
                event = ("DISPLAY MEMORY SATURATED", "Performing cathode-ray absolution.")
                render(telemetry, drops, thought, fortune, event, ollama, history, rng, None, None)
                time.sleep(0.55)
                crt_collapse(rng)
                memory.crt_resets += 1
                event = None
                now = time.monotonic()
                last = now
                next_frame = now
                next_crt_reset = now + rng.uniform(*CRT_RESET_INTERVAL)

            if now >= next_incident:
                incident = rng.choice(CRASH_INCIDENTS)
                incident_until = now + rng.uniform(0.35, 1.35)
                next_incident = now + rng.uniform(*INCIDENT_INTERVAL)
                if rng.random() < 0.35:
                    event = rng.choice(RARE_EVENTS)
                    event_until = now + 3.5

            if event and now >= event_until:
                event = None
            if incident and now >= incident_until:
                if incident == "chromatic_panic":
                    sys.stdout.write(f"{ESC}?5l")
                incident = None

            if now >= next_frame:
                render(telemetry, drops, thought, fortune, event, ollama, history, rng, incident, answer)
                next_frame = now + 1 / fps
            else:
                time.sleep(min(0.01, next_frame - now))

    session_seconds = time.monotonic() - session_started
    memory.total_seconds += session_seconds
    memory.longest_session = max(memory.longest_session, session_seconds)
    memory.save()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
