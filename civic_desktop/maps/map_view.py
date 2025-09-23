from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import os

class MapView(QWidget):
    def __init__(self, lat=33.4484, lon=-112.0740, zoom_start=10, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.webview = QWebEngineView(self)
        self.layout.addWidget(self.webview)
        self.setLayout(self.layout)
        self._init_map(lat, lon, zoom_start)

    def _init_map(self, lat, lon, zoom_start):
        # Create a folium map centered at the given coordinates
        fmap = folium.Map(location=[lat, lon], zoom_start=zoom_start)
        # Save to temporary HTML file
        map_path = os.path.join(os.path.dirname(__file__), 'map.html')
        fmap.save(map_path)
        self.webview.load(QUrl.fromLocalFile(map_path))

    def set_location(self, lat, lon, zoom_start=10):
        self._init_map(lat, lon, zoom_start)
