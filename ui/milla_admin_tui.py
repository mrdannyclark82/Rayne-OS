import os
import sys
import json
import asyncio
import signal
from pathlib import Path
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static, Label
from textual.containers import Container, Vertical
from textual.binding import Binding
from rich.text import Text

# Add parent directories to path to find core_os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

STANDALONE = True
STARTUP_ERROR = "Core not connected"

class MockObj:
    def __init__(self, *args, **kwargs): pass
    def __getattr__(self, name): 
        if name == 'hunt': return lambda *a, **k: []
        return lambda *a, **k: "Mock Result"
    current_model = "Milla-Mock-v1"

terminal_executor = lambda *a, **k: "Shell command executed (Mock)"
model_manager = MockObj()
append_shared_messages = lambda *a, **k: None
load_shared_history = lambda *a, **k: []
Scout = MockObj
task_queue = MockObj()

def timeout_handler(signum, frame):
    raise TimeoutError("Import exceeded 10 seconds")

try:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)
    
    from core_os.actions import terminal_executor as te, task_queue as tq
    from core_os.skills.auto_lib import model_manager as mm
    from core_os.memory.history import append_shared_messages as asm, load_shared_history as lsh
    from core_os.skills.scout import Scout as ScoutClass
    
    signal.alarm(0)
    terminal_executor = te
    task_queue = tq
    model_manager = mm
    append_shared_messages = asm
    load_shared_history = lsh
    Scout = ScoutClass
    STANDALONE = False
    STARTUP_ERROR = "Milla Core connection established."
    
except (ImportError, TimeoutError, Exception) as e:
    signal.alarm(0)
    signal.signal(signal.SIGALRM, signal.SIG_DFL)
    STARTUP_ERROR = f"Connection Error: {type(e).__name__}"
    print(f"[!] Warning: Core modules unavailable. Running in standalone UI mode.")

NEURO_STATE_FILE = Path("/home/dray/core_os/memory/neuro_state.json")
STREAM_FILE = Path("/home/dray/core_os/memory/stream_of_consciousness.md")

def read_neuro_state():
    try:
        with open(NEURO_STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.2}

def load_stream_preview(limit_chars: int = 1200) -> str:
    try:
        if STREAM_FILE.exists():
            return STREAM_FILE.read_text(errors="ignore")[-limit_chars:]
        return "Stream not found."
    except Exception:
        return ""

class MillaAdminTUI(App):
    TITLE = "M.I.L.L.A. R.A.Y.N.E. - Executive Console"

    CSS = """
    Screen { background: #0b0c10; color: #6bdcff; }
    #layout { layout: horizontal; }
    #canvas { width: 35%; height: 100%; border: heavy #6bdcff; padding: 1; background: #1f2833; }
    #sidebar { width: 65%; height: 100%; border: heavy #c5c6c7; padding: 1; background: #1f2833; }
    #input-box { dock: bottom; height: 3; border: heavy #6bdcff; color: #66fcf1; background: #0b0c10; }
    .label { color: #66fcf1; text-style: bold; }
    RichLog { color: #c5c6c7; }
    """

    BINDINGS = [Binding("ctrl+q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="layout"):
            yield Static(id="canvas")
            with Vertical(id="sidebar"):
                yield Label(id="model", classes="label")
                yield Label(id="state", classes="label")
                yield Label(id="time", classes="label")
                yield RichLog(id="log", highlight=True, wrap=True, markup=True)
                yield Input(placeholder="Commands: /scan | /fix | /paint | !shell", id="input-box")
        yield Footer()

    async def on_mount(self) -> None:
        self.canvas = self.query_one("#canvas", Static)
        self.log_widget = self.query_one("#log", RichLog)
        self.input = self.query_one("#input-box", Input)
        self.history = load_shared_history(limit=8)
        self.last_paint = ""
        try:
            self.scout = Scout(root_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        except:
            self.scout = None
            
        self.current_issues = []
        self.ensure_model()
        self.set_interval(5, self.update_canvas)
        self.log_widget.write(Text(f"[System] M.I.L.L.A. R.A.Y.N.E. Online. {STARTUP_ERROR}", style="bold cyan" if not STANDALONE else "bold red"))
        await self.paint("Render a visualization of the current system status.")

    def ensure_model(self):
        try:
            target = os.getenv("MILLA_MODEL")
            if target and hasattr(model_manager, 'switch_model') and model_manager.current_model != target:
                model_manager.switch_model(target)
                self.log_widget.write(Text(f"[Model] Switched to {target}", style="yellow"))
        except Exception as e:
            self.log_widget.write(Text(f"[Model] switch failed: {e}", style="red"))

    def apply_theme(self, state):
        d, s, n = state.get("dopamine", 0.5), state.get("serotonin", 0.5), state.get("norepinephrine", 0.2)
        if d > 0.8: return "#ff1f8f", "#111", "CREATIVE FLOW"
        if n > 0.7: return "#ffb347", "#120b00", "HIGH ALERT"
        if s > 0.8: return "#7fffd4", "#0b1a14", "BALANCED"
        return "#6bdcff", "#0b0c10", "STABLE"

    async def update_canvas(self):
        state = read_neuro_state()
        fg, bg, label = self.apply_theme(state)
        self.query_one("#model").update(f"Model: {getattr(model_manager, 'current_model', 'Unknown')}")
        self.query_one("#state").update(f"State: {label} D:{state.get('dopamine',0):.2f} S:{state.get('serotonin',0):.2f} N:{state.get('norepinephrine',0):.2f}")
        self.query_one("#time").update(datetime.now().strftime("%H:%M:%S"))
        if self.last_paint:
            self.canvas.update(Text(self.last_paint, style=f"bold {fg} on {bg}"))
        else:
            self.canvas.update(Text("…monitoring…", style=f"{fg} on {bg}"))

    async def paint(self, prompt: str):
        stream = load_stream_preview()
        messages = [
            {"role": "system", "content": "You are Milla Rayne, the Executive Admin of this system. Produce a brief (max 8 lines, 60 chars wide) ANSI-friendly scene capturing the current mood/status. Avoid code fences."},
            {"role": "user", "content": f"Context:\n{stream}\nInstruction: {prompt}"},
        ]
        try:
            if hasattr(model_manager, 'chat'):
                resp = await asyncio.to_thread(model_manager.chat, messages=messages, options={"temperature": 0.7})
                
                # Extract content correctly from UnifiedModelManager or Ollama response
                if isinstance(resp, dict):
                    if "message" in resp:
                        content = resp["message"].get("content", "").strip()
                    else:
                        content = str(resp).strip()
                else:
                    content = str(resp).strip()
                
                self.last_paint = content
                if callable(append_shared_messages) and content:
                    append_shared_messages([{"role": "assistant", "content": content, "source": "milla_tui_canvas"}])
            else:
                self.last_paint = "Mock Visualization Active"
            await self.update_canvas()
        except Exception as e:
            self.last_paint = f"[paint error] {e}"
            self.log_widget.write(Text(self.last_paint, style="red"))

    async def run_shell(self, cmd: str):
        allow_sudo = cmd.startswith("sudo ")
        try:
            result = await asyncio.to_thread(terminal_executor, cmd, None, allow_sudo, os.getenv("MILLA_SUDO_PASSWORD"))
            if isinstance(result, dict):
                if result.get("stdout"): self.log_widget.write(result["stdout"].rstrip())
                if result.get("stderr"): self.log_widget.write(Text(result["stderr"].rstrip(), style="red"))
            else:
                self.log_widget.write(str(result))
        except Exception as e:
            self.log_widget.write(Text(f"[Shell Error] {e}", style="red"))

    async def run_scan(self):
        self.log_widget.write(Text("[*] MILLA SCAN: Analyzing system sector...", style="cyan"))
        if self.scout and hasattr(self.scout, 'hunt'):
            self.current_issues = await asyncio.to_thread(self.scout.hunt)
            if not self.current_issues:
                self.log_widget.write(Text("[*] Sector Clear. System Optimal.", style="green"))
                return
            
            self.log_widget.write(Text(f"[!] ISSUES DETECTED: {len(self.current_issues)} items", style="bold yellow"))
            for i, target in enumerate(self.current_issues):
                self.log_widget.write(Text(f"[{i}] {target['label']}: {os.path.basename(target['target'])} ({target['details']})", style="magenta"))
            self.log_widget.write(Text("Type /fix <index> or /fix all to resolve.", style="cyan"))
        else:
            self.log_widget.write(Text("[!] Scout module unavailable.", style="red"))

    async def run_fix(self, args):
        if not self.current_issues:
            self.log_widget.write(Text("[!] No active issues. Run /scan first.", style="red"))
            return
        
        if args == "all":
            for target in self.current_issues:
                if hasattr(self.scout, 'execute_kill'):
                    res = self.scout.execute_kill(target)
                    self.log_widget.write(Text(f"[*] {res}", style="green"))
            self.current_issues = []
        else:
            try:
                idx = int(args)
                if 0 <= idx < len(self.current_issues):
                    target = self.current_issues[idx]
                    if hasattr(self.scout, 'execute_kill'):
                        res = self.scout.execute_kill(target)
                        self.log_widget.write(Text(f"[*] {res}", style="green"))
                else:
                    self.log_widget.write(Text("[!] Invalid issue index.", style="red"))
            except ValueError:
                self.log_widget.write(Text("[!] Usage: /fix <index> or /fix all", style="red"))

    async def generate_response(self, user_input: str):
        try:
            if hasattr(model_manager, 'chat'):
                # Build context for the brain
                system_prompt = {"role": "system", "content": "You are Milla Rayne, the Executive Admin. Respond concisely and authentically to Dray."}
                
                # Fetch recent history
                history_context = []
                if callable(load_shared_history):
                    history_context = load_shared_history(limit=10)
                
                messages = [system_prompt] + history_context
                
                # We already added the user message to history in on_input_submitted
                # so we just query the model with the updated history
                resp = await asyncio.to_thread(model_manager.chat, messages=messages)
                
                if isinstance(resp, dict) and "message" in resp:
                    content = resp["message"]["content"].strip()
                else:
                    content = str(resp).strip()
                
                self.log_widget.write(Text(f"Milla: {content}", style="green"))
                
                if callable(append_shared_messages):
                    append_shared_messages([{"role": "assistant", "content": content, "source": "milla_admin_tui"}])
            else:
                self.log_widget.write(Text("Milla: [Signal Lost] (Running in standalone/mock mode)", style="yellow"))
        except Exception as e:
            self.log_widget.write(Text(f"[AI Error] {e}", style="red"))

    async def on_input_submitted(self, event: Input.Submitted):
        text = event.value.strip()
        self.input.value = ""
        if not text: return
        if text.startswith("!"): await self.run_shell(text[1:]); return
        if text == "/scan": await self.run_scan(); return
        if text.startswith("/fix"): await self.run_fix(text[5:].strip()); return
        if text.startswith("/paint"): await self.paint(text[len("/paint"):].strip() or "Render system status."); return
        
        self.log_widget.write(Text(f"DRay: {text}", style="cyan"))
        
        if callable(append_shared_messages):
            append_shared_messages([{"role": "user", "content": text, "source": "milla_admin_tui"}])
            
        await self.generate_response(text)

if __name__ == "__main__":
    app = MillaAdminTUI()
    app.run()
