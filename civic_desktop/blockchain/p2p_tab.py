"""
P2P Network Dashboard Tab
=========================

This module provides a GUI tab for monitoring and managing the P2P network:
- Network status and statistics
- Peer management (add/remove peers)
- Blockchain synchronization controls
- Network diagnostics and monitoring
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QListWidget, QGroupBox, QGridLayout,
    QProgressBar, QMessageBox, QScrollArea, QListWidgetItem
)
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
from typing import Dict, Any, Optional

class P2PNetworkTab(QWidget):
    """P2P Network monitoring and management tab"""
    
    # Signals
    status_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.p2p_manager = None
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        self.init_ui()
        self.connect_p2p_manager()
    
    def connect_p2p_manager(self):
        """Connect to P2P manager"""
        try:
            from ..blockchain.p2p_manager import get_p2p_manager
            self.p2p_manager = get_p2p_manager()
        except Exception as e:
            print(f"Failed to connect to P2P manager: {e}")
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📡 P2P Network Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Create main content in a scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Network Status Section
        scroll_layout.addWidget(self.create_status_section())
        
        # Peer Management Section
        scroll_layout.addWidget(self.create_peer_management_section())
        
        # Synchronization Section
        scroll_layout.addWidget(self.create_sync_section())
        
        # Network Diagnostics Section
        scroll_layout.addWidget(self.create_diagnostics_section())
        
        # Set up scroll area
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
    
    def create_status_section(self) -> QGroupBox:
        """Create network status display section"""
        group = QGroupBox("🌐 Network Status")
        layout = QGridLayout()
        
        # Status labels
        self.status_labels = {
            'server_running': QLabel("❌ Offline"),
            'sync_running': QLabel("❌ Offline"),
            'network_connected': QLabel("❌ Disconnected"),
            'peer_count': QLabel("0"),
            'healthy_peers': QLabel("0"),
            'blockchain_height': QLabel("0"),
            'node_id': QLabel("Not Available"),
            'server_url': QLabel("Not Available"),
            'last_sync': QLabel("Never")
        }
        
        # Create status grid
        row = 0
        status_items = [
            ("P2P Server:", 'server_running'),
            ("Synchronization:", 'sync_running'),
            ("Network:", 'network_connected'),
            ("Total Peers:", 'peer_count'),
            ("Healthy Peers:", 'healthy_peers'),
            ("Blockchain Height:", 'blockchain_height'),
            ("Node ID:", 'node_id'),
            ("Server URL:", 'server_url'),
            ("Last Sync:", 'last_sync')
        ]
        
        for label_text, key in status_items:
            layout.addWidget(QLabel(label_text), row, 0)
            layout.addWidget(self.status_labels[key], row, 1)
            row += 1
        
        group.setLayout(layout)
        return group
    
    def create_peer_management_section(self) -> QGroupBox:
        """Create peer management section"""
        group = QGroupBox("👥 Peer Management")
        layout = QVBoxLayout()
        
        # Add peer controls
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("Add Peer:"))
        self.peer_input = QLineEdit()
        self.peer_input.setPlaceholderText("http://peer-url:8000")
        add_layout.addWidget(self.peer_input)
        
        self.add_peer_button = QPushButton("➕ Add Peer")
        self.add_peer_button.clicked.connect(self.add_peer)
        add_layout.addWidget(self.add_peer_button)
        
        layout.addLayout(add_layout)
        
        # Peer list
        peer_list_layout = QHBoxLayout()
        
        # Healthy peers
        healthy_group = QGroupBox("✅ Healthy Peers")
        healthy_layout = QVBoxLayout()
        self.healthy_peers_list = QListWidget()
        healthy_layout.addWidget(self.healthy_peers_list)
        
        remove_healthy_button = QPushButton("🗑️ Remove Selected")
        remove_healthy_button.clicked.connect(lambda: self.remove_selected_peer(self.healthy_peers_list))
        healthy_layout.addWidget(remove_healthy_button)
        healthy_group.setLayout(healthy_layout)
        
        # Unhealthy peers
        unhealthy_group = QGroupBox("❌ Unhealthy Peers")
        unhealthy_layout = QVBoxLayout()
        self.unhealthy_peers_list = QListWidget()
        unhealthy_layout.addWidget(self.unhealthy_peers_list)
        
        remove_unhealthy_button = QPushButton("🗑️ Remove Selected")
        remove_unhealthy_button.clicked.connect(lambda: self.remove_selected_peer(self.unhealthy_peers_list))
        unhealthy_layout.addWidget(remove_unhealthy_button)
        unhealthy_group.setLayout(unhealthy_layout)
        
        peer_list_layout.addWidget(healthy_group)
        peer_list_layout.addWidget(unhealthy_group)
        layout.addLayout(peer_list_layout)
        
        # Peer actions
        actions_layout = QHBoxLayout()
        
        self.discover_button = QPushButton("🔍 Discover Peers")
        self.discover_button.clicked.connect(self.discover_peers)
        actions_layout.addWidget(self.discover_button)
        
        self.cleanup_button = QPushButton("🧹 Cleanup Unhealthy")
        self.cleanup_button.clicked.connect(self.cleanup_peers)
        actions_layout.addWidget(self.cleanup_button)
        
        layout.addLayout(actions_layout)
        group.setLayout(layout)
        return group
    
    def create_sync_section(self) -> QGroupBox:
        """Create synchronization controls section"""
        group = QGroupBox("🔄 Blockchain Synchronization")
        layout = QVBoxLayout()
        
        # Sync status
        self.sync_status_label = QLabel("Status: Not syncing")
        layout.addWidget(self.sync_status_label)
        
        self.sync_progress = QProgressBar()
        self.sync_progress.setVisible(False)
        layout.addWidget(self.sync_progress)
        
        # Sync controls
        controls_layout = QHBoxLayout()
        
        self.sync_now_button = QPushButton("🔄 Sync Now")
        self.sync_now_button.clicked.connect(self.sync_now)
        controls_layout.addWidget(self.sync_now_button)
        
        self.manual_sync_input = QLineEdit()
        self.manual_sync_input.setPlaceholderText("http://peer-url:8000")
        controls_layout.addWidget(self.manual_sync_input)
        
        self.manual_sync_button = QPushButton("🎯 Sync with Peer")
        self.manual_sync_button.clicked.connect(self.manual_sync)
        controls_layout.addWidget(self.manual_sync_button)
        
        layout.addLayout(controls_layout)
        group.setLayout(layout)
        return group
    
    def create_diagnostics_section(self) -> QGroupBox:
        """Create network diagnostics section"""
        group = QGroupBox("🔧 Network Diagnostics")
        layout = QVBoxLayout()
        
        # Diagnostics display
        self.diagnostics_text = QTextEdit()
        self.diagnostics_text.setMaximumHeight(200)
        self.diagnostics_text.setReadOnly(True)
        layout.addWidget(self.diagnostics_text)
        
        # Diagnostic controls
        controls_layout = QHBoxLayout()
        
        self.test_network_button = QPushButton("🧪 Test Network")
        self.test_network_button.clicked.connect(self.test_network)
        controls_layout.addWidget(self.test_network_button)
        
        self.clear_diagnostics_button = QPushButton("🗑️ Clear Log")
        self.clear_diagnostics_button.clicked.connect(self.clear_diagnostics)
        controls_layout.addWidget(self.clear_diagnostics_button)
        
        layout.addLayout(controls_layout)
        group.setLayout(layout)
        return group
    
    def refresh_status(self):
        """Refresh P2P network status"""
        if not self.p2p_manager:
            self.connect_p2p_manager()
            return
        
        try:
            status = self.p2p_manager.get_status()
            self.update_status_display(status)
            self.update_peer_lists()
            
        except Exception as e:
            self.log_diagnostic(f"❌ Status refresh error: {e}")
    
    def update_status_display(self, status: Dict[str, Any]):
        """Update status display with current P2P status"""
        # Server status
        if status.get('server_running', False):
            self.status_labels['server_running'].setText("✅ Online")
            self.status_labels['server_running'].setStyleSheet("color: green;")
        else:
            self.status_labels['server_running'].setText("❌ Offline")
            self.status_labels['server_running'].setStyleSheet("color: red;")
        
        # Sync status
        if status.get('sync_running', False):
            self.status_labels['sync_running'].setText("✅ Active")
            self.status_labels['sync_running'].setStyleSheet("color: green;")
        else:
            self.status_labels['sync_running'].setText("❌ Inactive")
            self.status_labels['sync_running'].setStyleSheet("color: red;")
        
        # Network status
        if status.get('network_connected', False):
            self.status_labels['network_connected'].setText("✅ Connected")
            self.status_labels['network_connected'].setStyleSheet("color: green;")
        else:
            self.status_labels['network_connected'].setText("❌ Disconnected")
            self.status_labels['network_connected'].setStyleSheet("color: orange;")
        
        # Numeric status
        self.status_labels['peer_count'].setText(str(status.get('peer_count', 0)))
        self.status_labels['healthy_peers'].setText(str(status.get('healthy_peers', 0)))
        
        # Node info
        self.status_labels['node_id'].setText(status.get('node_id', 'Not Available'))
        self.status_labels['server_url'].setText(status.get('server_url', 'Not Available'))
        
        # Last sync
        last_sync = status.get('last_sync')
        if last_sync:
            try:
                sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                self.status_labels['last_sync'].setText(sync_time.strftime('%Y-%m-%d %H:%M:%S'))
            except:
                self.status_labels['last_sync'].setText(str(last_sync))
        else:
            self.status_labels['last_sync'].setText("Never")
        
        # Sync progress
        if status.get('is_syncing', False):
            self.sync_status_label.setText("🔄 Syncing in progress...")
            self.sync_progress.setVisible(True)
        else:
            self.sync_status_label.setText("✅ Sync complete")
            self.sync_progress.setVisible(False)
    
    def update_peer_lists(self):
        """Update peer lists"""
        try:
            from ..blockchain.p2p import get_network_status
            network_status = get_network_status()
            
            # Clear lists
            self.healthy_peers_list.clear()
            self.unhealthy_peers_list.clear()
            
            # Add healthy peers
            for peer in network_status.get('peer_list', {}).get('healthy', []):
                self.healthy_peers_list.addItem(peer)
            
            # Add unhealthy peers
            for peer in network_status.get('peer_list', {}).get('unhealthy', []):
                self.unhealthy_peers_list.addItem(peer)
                
        except Exception as e:
            self.log_diagnostic(f"❌ Peer list update error: {e}")
    
    def add_peer(self):
        """Add a new peer"""
        peer_url = self.peer_input.text().strip()
        if not peer_url:
            QMessageBox.warning(self, "Invalid Input", "Please enter a peer URL")
            return
        
        if self.p2p_manager:
            try:
                success = self.p2p_manager.add_peer(peer_url)
                if success:
                    self.log_diagnostic(f"✅ Added peer: {peer_url}")
                    self.peer_input.clear()
                    self.refresh_status()
                else:
                    self.log_diagnostic(f"⚠️ Peer already exists or failed health check: {peer_url}")
            except Exception as e:
                self.log_diagnostic(f"❌ Error adding peer {peer_url}: {e}")
        else:
            QMessageBox.warning(self, "P2P Unavailable", "P2P manager not available")
    
    def remove_selected_peer(self, list_widget: QListWidget):
        """Remove selected peer from list"""
        current_item = list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a peer to remove")
            return
        
        peer_url = current_item.text()
        
        if self.p2p_manager:
            try:
                success = self.p2p_manager.remove_peer(peer_url)
                if success:
                    self.log_diagnostic(f"🗑️ Removed peer: {peer_url}")
                    self.refresh_status()
                else:
                    self.log_diagnostic(f"⚠️ Failed to remove peer: {peer_url}")
            except Exception as e:
                self.log_diagnostic(f"❌ Error removing peer {peer_url}: {e}")
    
    def discover_peers(self):
        """Discover new peers"""
        if self.p2p_manager:
            try:
                count = self.p2p_manager.discover_peers()
                self.log_diagnostic(f"🔍 Peer discovery: {count} new peers found")
                self.refresh_status()
            except Exception as e:
                self.log_diagnostic(f"❌ Peer discovery error: {e}")
    
    def cleanup_peers(self):
        """Clean up unhealthy peers"""
        if self.p2p_manager:
            try:
                count = self.p2p_manager.cleanup_peers()
                self.log_diagnostic(f"🧹 Peer cleanup: {count} unhealthy peers removed")
                self.refresh_status()
            except Exception as e:
                self.log_diagnostic(f"❌ Peer cleanup error: {e}")
    
    def sync_now(self):
        """Trigger immediate synchronization"""
        if self.p2p_manager:
            try:
                self.log_diagnostic("🔄 Starting blockchain synchronization...")
                success = self.p2p_manager.sync_now()
                if success:
                    self.log_diagnostic("✅ Synchronization completed successfully")
                else:
                    self.log_diagnostic("⚠️ Synchronization failed or no updates needed")
                self.refresh_status()
            except Exception as e:
                self.log_diagnostic(f"❌ Sync error: {e}")
    
    def manual_sync(self):
        """Manually sync with specific peer"""
        peer_url = self.manual_sync_input.text().strip()
        if not peer_url:
            QMessageBox.warning(self, "Invalid Input", "Please enter a peer URL")
            return
        
        try:
            from ..blockchain.sync import sync_with_peer
            self.log_diagnostic(f"🎯 Syncing with peer: {peer_url}")
            success = sync_with_peer(peer_url)
            if success:
                self.log_diagnostic(f"✅ Manual sync with {peer_url} completed")
            else:
                self.log_diagnostic(f"⚠️ Manual sync with {peer_url} failed")
            self.manual_sync_input.clear()
            self.refresh_status()
        except Exception as e:
            self.log_diagnostic(f"❌ Manual sync error: {e}")
    
    def test_network(self):
        """Test network connectivity"""
        self.log_diagnostic("🧪 Testing network connectivity...")
        
        try:
            from ..blockchain.p2p import get_network_status, check_peer_health
            network_status = get_network_status()
            
            self.log_diagnostic(f"📊 Network Status:")
            self.log_diagnostic(f"   Total peers: {network_status['total_peers']}")
            self.log_diagnostic(f"   Healthy peers: {network_status['healthy_peers']}")
            self.log_diagnostic(f"   Unhealthy peers: {network_status['unhealthy_peers']}")
            
            # Test a few healthy peers
            healthy_peers = network_status['peer_list']['healthy'][:3]
            for peer in healthy_peers:
                health = check_peer_health(peer)
                status_icon = "✅" if health else "❌"
                self.log_diagnostic(f"   {status_icon} {peer}")
                
        except Exception as e:
            self.log_diagnostic(f"❌ Network test error: {e}")
    
    def clear_diagnostics(self):
        """Clear diagnostics log"""
        self.diagnostics_text.clear()
    
    def log_diagnostic(self, message: str):
        """Add message to diagnostics log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.diagnostics_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.diagnostics_text.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())