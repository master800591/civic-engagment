from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import os

class MapView(QWidget):
    def __init__(self, lat=33.4484, lon=-112.0740, zoom_start=10, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        # Blockchain status and user role display
        from civic_desktop.users.session import SessionManager
        user = SessionManager.get_current_user()
        role = user.get('role', 'Unknown') if user else 'Unknown'
        blockchain_status = QLabel("All location saves are <b>recorded on blockchain</b> for audit and transparency.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        export_btn = QPushButton("Export Location Report")
        export_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 5px; padding: 8px 18px;")
        export_btn.clicked.connect(self.open_reports_tab)
        top_layout = QVBoxLayout()
        top_layout.addWidget(blockchain_status)
        top_layout.addWidget(role_label)
        top_layout.addWidget(export_btn)
        self.layout.addLayout(top_layout)
        self.webview = QWebEngineView(self)
        self.layout.addWidget(self.webview)
        self.setLayout(self.layout)
        self._init_map(lat, lon, zoom_start)

    def open_reports_tab(self):
        mw = self.parent()
        while mw and not hasattr(mw, 'tabs'):
            mw = mw.parent()
        if mw and hasattr(mw, 'tabs'):
            for i in range(mw.tabs.count()):
                if mw.tabs.tabText(i).lower().startswith("📊 reports") or mw.tabs.tabText(i).lower().startswith("reports"):
                    mw.tabs.setCurrentIndex(i)
                    break

    def _init_map(self, lat, lon, zoom_start):
        # Create a folium map centered at the given coordinates
        fmap = folium.Map(location=[lat, lon], zoom_start=zoom_start)
        # Save to temporary HTML file
        map_path = os.path.join(os.path.dirname(__file__), 'map.html')
        fmap.save(map_path)
        self.webview.load(QUrl.fromLocalFile(map_path))

    def set_location(self, lat, lon, zoom_start=10):
        self._init_map(lat, lon, zoom_start)
