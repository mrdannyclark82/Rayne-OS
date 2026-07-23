import sys
import threading
import time
import os
import json
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QGraphicsDropShadowEffect,
    QFrame,
    QSizeGrip,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPoint, QSize, QTimer
from PyQt6.QtGui import QColor, QFont, QCursor

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure CWD is project root so helpers find credentials.json
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Try to import helpers, fallback to mock if they fail
try:
    from core_os.skills.auto_lib import fetch_recent_emails, fetch_recent_files
except ImportError:
    def fetch_recent_emails(n):
        return [{"error": "Module not found"}]
    def fetch_recent_files(n):
        return [{"error": "Module not found"}]

# Paths
NEURO_STATE_FILE = Path(__file__).parent.parent / "core_os/memory/neuro_state.json"

class GlassSignals(QObject):
    data_updated = pyqtSignal(list, list) # emails, files
    neuro_updated = pyqtSignal(float, float, float) # d, s, n
    status_msg = pyqtSignal(str, str) # widget_id, message

class BaseGlassWidget(QMainWindow):
    def __init__(self, title="Glass Widget", width=300, height=200, color_theme="#00ffcc"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(width, height)
        self.color_theme = color_theme
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.container = QFrame()
        self.container.setObjectName("GlassPane")
        self.setCentralWidget(self.container)
        
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        self.update_style()

        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {self.color_theme}; letter-spacing: 1px;")
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        self.main_layout.addWidget(self.header)
        
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 5, 0, 5)
        self.main_layout.addWidget(self.content_area)
        
        self.footer = QWidget()
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(0,0,0,0)
        footer_layout.addStretch()
        self.sizegrip = QSizeGrip(self.container)
        footer_layout.addWidget(self.sizegrip)
        self.main_layout.addWidget(self.footer)

        self.oldPos = None

    def update_style(self):
        self.container.setStyleSheet(f"""
            #GlassPane {{
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(15, 20, 30, 180), 
                    stop:1 rgba(10, 15, 20, 230)
                );
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 20px;
            }}
            QSizeGrip {{ background-color: transparent; }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

class NeuroVitalsWidget(BaseGlassWidget):
    def __init__(self):
        super().__init__(title="[NEURO VITALS]", width=250, height=180, color_theme="#ff00ff")
        self.signals = GlassSignals()
        self.signals.neuro_updated.connect(self.update_bars)
        self.last_data = (0.5, 0.5, 0.5)
        
        self.d_bar = self.create_vital("DOPAMINE", "#ff00ff")
        self.s_bar = self.create_vital("SEROTONIN", "#00ffcc")
        self.n_bar = self.create_vital("NOREPI", "#ff9900")
        
        self.start_poller()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_bars(*self.last_data)

    def create_vital(self, name, color):
        layout = QVBoxLayout()
        lbl = QLabel(name)
        lbl.setStyleSheet("color: rgba(255,255,255,150); font-size: 9px; font-family: Consolas;")
        bar_bg = QFrame()
        bar_bg.setFixedHeight(6)
        bar_bg.setStyleSheet("background: rgba(255,255,255,20); border-radius: 3px;")
        bar_fill = QFrame(bar_bg)
        bar_fill.setFixedHeight(6)
        bar_fill.setStyleSheet(f"background: {color}; border-radius: 3px;")
        bar_fill.setFixedWidth(50) # Initial
        
        layout.addWidget(lbl)
        layout.addWidget(bar_bg)
        self.content_layout.addLayout(layout)
        return bar_fill

    def update_bars(self, d, s, n):
        max_w = self.container.width() - 60
        self.d_bar.setFixedWidth(int(d * max_w))
        self.s_bar.setFixedWidth(int(s * max_w))
        self.n_bar.setFixedWidth(int(n * max_w))

    def start_poller(self):
        threading.Thread(target=self._poll, daemon=True).start()

    def _poll(self):
        while True:
            try:
                if NEURO_STATE_FILE.exists():
                    data = json.loads(NEURO_STATE_FILE.read_text())
                    self.signals.neuro_updated.emit(
                        data.get('dopamine', 0.5),
                        data.get('serotonin', 0.5),
                        data.get('norepinephrine', 0.5)
                    )
            except:
                pass
            time.sleep(1)

class YouTubeWidget(BaseGlassWidget):
    def __init__(self):
        super().__init__(title="[SONIC VIZ]", width=350, height=160, color_theme="#ff0000")
        
        self.process = None
        self.signals = GlassSignals()
        self.signals.status_msg.connect(self.update_status)

        layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search or URL...")
        self.search_input.setStyleSheet("""
            background: rgba(255,255,255,15); 
            border: 1px solid rgba(255,255,255,30);
            border-radius: 5px;
            color: white;
            padding: 5px;
            font-family: Consolas;
        """)
        self.search_input.returnPressed.connect(self.run_search)
        layout.addWidget(self.search_input)
        
        controls_layout = QHBoxLayout()
        self.stop_btn = QPushButton("■ STOP")
        self.stop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 50, 50, 50);
                border: 1px solid rgba(200, 50, 50, 100);
                color: white;
                border-radius: 4px;
                padding: 4px;
                font-size: 10px;
                font-family: Consolas;
            }
            QPushButton:hover { background: rgba(200, 50, 50, 100); }
        """)
        self.stop_btn.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_btn)
        
        layout.addLayout(controls_layout)

        self.status = QLabel("Idle...")
        self.status.setStyleSheet("color: #888; font-size: 10px; margin-top: 5px; font-family: Consolas;")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        
        self.content_layout.addLayout(layout)

    def update_status(self, widget_id, msg):
        if widget_id == "sonic":
            self.status.setText(msg)

    def run_search(self):
        query = self.search_input.text()
        if not query: return
        
        self.status.setText(f"Searching: {query}...")
        self.search_input.clear()
        
        threading.Thread(target=self._play_thread, args=(query,), daemon=True).start()

    def _play_thread(self, query):
        self.stop_playback()
        
        try:
            # 1. Get URL/Title via yt-dlp
            cmd = [
                "yt-dlp", 
                "--default-search", "ytsearch", 
                "--get-title", 
                "--get-url", 
                "--no-playlist",
                "-f", "bestaudio[ext=m4a]/best[ext=mp4]/best",
                query
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.signals.status_msg.emit("sonic", "Error: Search failed")
                return

            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                self.signals.status_msg.emit("sonic", "Error: No results found")
                return
                
            title = lines[0]
            stream_url = lines[1]
            
            self.signals.status_msg.emit("sonic", f"▶ {title[:40]}...")
            
            # 2. Play with mpv
            self.process = subprocess.Popen([
                "mpv", 
                "--no-video", 
                "--term-playing-msg='SO_PLAYING'", 
                stream_url
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.process.wait()
            self.signals.status_msg.emit("sonic", "Playback finished.")
            self.process = None

        except Exception as e:
            self.signals.status_msg.emit("sonic", f"Error: {str(e)}")

    def stop_playback(self):
        if self.process:
            self.process.terminate()
            self.process = None
            self.status.setText("Stopped.")

class IntelWidget(BaseGlassWidget):
    def __init__(self):
        super().__init__(title="[WORKSPACE INTEL]", width=350, height=250, color_theme="#00ccff")
        self.signals = GlassSignals()
        self.signals.data_updated.connect(self.refresh_ui)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0,0,0,0)
        self.scroll.setWidget(self.scroll_content)
        self.content_layout.addWidget(self.scroll)
        self.status_label = QLabel("Scanning...")
        self.status_label.setStyleSheet("color: rgba(255,255,255,100); font-size: 10px;")
        self.content_layout.addWidget(self.status_label)
        self.start_worker()

    def start_worker(self):
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        while True:
            try:
                creds_path = Path("credentials.json")
                if not creds_path.exists():
                    self.signals.data_updated.emit([{"error": "Missing credentials.json"}], [{"error": "Run setup"}])
                else:
                    emails = fetch_recent_emails(3)
                    files = fetch_recent_files(3)
                    self.signals.data_updated.emit(emails, files)
            except Exception as e:
                self.signals.data_updated.emit([{"error": str(e)}], [{"error": "Fetch failed"}])
            time.sleep(60)

    def refresh_ui(self, emails, files):
        for i in reversed(range(self.scroll_layout.count())):
            if self.scroll_layout.itemAt(i).widget():
                self.scroll_layout.itemAt(i).widget().setParent(None)
        
        # UI Construction logic (Comms & Assets)
        sec1 = QLabel(":: RECENT COMMS ::")
        sec1.setStyleSheet("color: #ff9900; font-weight: bold;")
        self.scroll_layout.addWidget(sec1)
        for e in emails:
            txt = e.get('snippet', e.get('error', '...'))
            self.scroll_layout.addWidget(QLabel(f"> {txt[:40]}...", styleSheet="color: #eee; font-size: 11px;"))
            
        sec2 = QLabel("\n:: ACTIVE ASSETS ::")
        sec2.setStyleSheet("color: #00ffcc; font-weight: bold;")
        self.scroll_layout.addWidget(sec2)
        for f in files:
            txt = f.get('name', f.get('error', '...'))
            self.scroll_layout.addWidget(QLabel(f"[{txt[:40]}]", styleSheet="color: #eee; font-size: 11px;"))
        
        self.scroll_layout.addStretch()
        self.status_label.setText(f"Last Sync: {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    screen = QApplication.primaryScreen().geometry()
    
    # 1. Workspace Intel (Right Side)
    intel = IntelWidget()
    intel.move(screen.width() - 380, 50)
    intel.show()
    
    # 2. Neuro Vitals (Below Intel)
    vitals = NeuroVitalsWidget()
    vitals.move(screen.width() - 380, 320)
    vitals.show()
    
    # 3. Sonic Viz / YouTube (Bottom Right)
    sonic = YouTubeWidget()
    sonic.move(screen.width() - 380, 520)
    sonic.show()
    
    sys.exit(app.exec())