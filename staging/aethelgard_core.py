import os
import sys
import asyncio
import json
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static, Label, TabbedContent, TabPane
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.console import RenderableType

# --- Project Path Setup ---
# We'll try to find the real core_os if possible, otherwise stick to mocks
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- References from Glass HUD ---
# Theme Colors from glass_hud.py:
# Background: rgba(15, 20, 30, 180) -> #0f141e
# Border: rgba(255, 255, 255, 30)
# Accents: #00ffcc (Cyan/Green), #ff00ff (Magenta), #ff9900 (Orange), #ff0000 (Red)

class NeuroVitals(Static):
    """Refined Neuro Vitals based on glass_hud.py's logic."""
    
    def on_mount(self) -> None:
        self.set_interval(2, self.refresh_vitals)

    def refresh_vitals(self) -> None:
        # Simulated or read from real neuro_state.json if it exists
        neuro_path = os.path.join(PROJECT_ROOT, "core_os/memory/neuro_state.json")
        try:
            with open(neuro_path, "r") as f:
                state = json.load(f)
        except:
            state = {"dopamine": 0.75, "serotonin": 0.60, "norepinephrine": 0.40}
        
        d, s, n = state.get("dopamine", 0.5), state.get("serotonin", 0.5), state.get("norepinephrine", 0.5)
        
        progress = Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=15),
            TextColumn("{task.percentage:>3.0f}%"),
            expand=True
        )
        
        progress.add_task("[magenta]DOPAMINE", total=100, completed=d*100)
        progress.add_task("[cyan]SEROTONIN", total=100, completed=s*100)
        progress.add_task("[orange1]NOREPI", total=100, completed=n*100)
        
        self.update(Panel(progress, title="[bold white]NEURO VITALS[/]", border_style="bright_blue"))

class SonicViz(Static):
    """Media status and control interface."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = "IDLE"
        self.current_track = "None"

    def render(self) -> RenderableType:
        return Panel(
            f"[bold red]STATUS:[/] {self.status}\n[bold white]TRACK:[/] [dim]{self.current_track}[/]",
            title="[bold red]SONIC VIZ[/]",
            border_style="red"
        )

class WorkspaceIntel(Static):
    """Recent activities and assets."""
    def render(self) -> RenderableType:
        return Panel(
            "[yellow]:: RECENT COMMS ::[/]\n[dim]> No new signals...[/]\n\n"
            "[green]:: ACTIVE ASSETS ::[/]\n[dim][glass_hud.py]\n[Aethelgard Core][/]",
            title="[bold blue]WORKSPACE INTEL[/]",
            border_style="blue"
        )

class AethelgardApp(App):
    TITLE = "AETHELGARD :: THE GLASS FORTRESS"
    
    CSS = """
    Screen {
        background: #0b0f19; /* Darker navy for better contrast */
        color: #e2e8f0;
    }
    
    #main-layout {
        layout: grid;
        grid-size: 2;
        grid-columns: 3fr 1fr;
        height: 1fr;
        padding: 1;
    }
    
    .sidebar {
        width: 100%;
        height: 100%;
        padding: 0 1;
    }

    #input-bar {
        dock: bottom;
        height: 3;
        border: heavy #00ffcc;
        background: #0f141e;
        color: #00ffcc;
    }

    RichLog {
        background: #0f141e;
        border: heavy #00ffcc;
        padding: 1;
    }

    TabPane {
        padding: 1;
        background: #0f141e;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Shutdown"),
        ("ctrl+l", "clear_log", "Clear"),
        ("pageup", "scroll_up", "Scroll Up"),
        ("pagedown", "scroll_down", "Scroll Down"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-layout"):
            with TabbedContent():
                with TabPane("Nexus", id="nexus"):
                    yield RichLog(id="main-log", markup=True, wrap=True, auto_scroll=True)
                with TabPane("Forge", id="forge"):
                    yield Label("[bold yellow]Forge System Initializing...[/]\nReady for Garuda deployment.")
                with TabPane("Network", id="network"):
                    yield Label("[bold cyan]Scanning Mesh...[/]\nTargeting Garuda Node.")
            
            with Vertical(classes="sidebar"):
                yield NeuroVitals()
                yield SonicViz()
                yield WorkspaceIntel()
        
        yield Input(placeholder="Execute command... (e.g. /scan, /play, /garuda)", id="input-bar")
        yield Footer()

    async def on_mount(self) -> None:
        self.nexus_log = self.query_one("#main-log", RichLog)
        self.nexus_log.write(Text("AETHELGARD PROTOCOL ACTIVE", style="bold cyan underline"))
        self.nexus_log.write("[dim]Reference parameters pulled from /ogdray/ui/glass_hud.py[/]")
        self.nexus_log.write("[green]System: Sudo Sandbox Mode Enabled.[/]")
        self.nexus_log.write("[yellow]Standing by for Garuda Node synchronization.[/]")

    def action_scroll_up(self) -> None:
        self.nexus_log.scroll_relative(y=-5)

    def action_scroll_down(self) -> None:
        self.nexus_log.scroll_relative(y=5)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        self.query_one("#input-bar").value = ""
        
        if not text:
            return
            
        # Check if it's a command
        if text.startswith("/"):
            cmd = text.lower()
            self.nexus_log.write(f"[bold cyan]CMD >[/] {cmd}")
            
            if cmd == "/scan":
                self.nexus_log.write("[yellow]Initiating network mesh scan...[/]")
            elif cmd == "/clear":
                self.nexus_log.clear()
            elif cmd == "/garuda":
                self.nexus_log.write("[bold green]Garuda Prep Sequence:[/]")
                self.nexus_log.write("1. Flash ISO\n2. Run install_aethelgard.sh\n3. Sync SSH keys")
            elif cmd.startswith("/play "):
                track = cmd[6:]
                self.nexus_log.write(f"[red]SONIC:[/] Loading {track}...")
            elif cmd == "/quit":
                self.exit()
            else:
                self.nexus_log.write(f"[red]Error:[/] Unknown command '{cmd}'")
        else:
            # It's chat
            self.nexus_log.write(f"[bold green]D-Ray >[/] {text}")
            
            # Simple interaction logic (Mock Milla)
            if "hey milla" in text.lower():
                self.nexus_log.write(f"[bold magenta]Milla >[/] I'm here, D-Ray. Systems nominal. Ready for orders.")
            elif "status" in text.lower():
                 self.nexus_log.write(f"[bold magenta]Milla >[/] Aethelgard Core: ONLINE. Garuda Node: PENDING.")
            else:
                 self.nexus_log.write(f"[dim italic]Milla logs the entry...[/]")

    def action_clear_log(self) -> None:
        self.query_one("#main-log").clear()

if __name__ == "__main__":
    AethelgardApp().run()