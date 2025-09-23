from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout, QTextEdit, QComboBox, QGroupBox, QFormLayout
from civic_desktop.blockchain.blockchain import Blockchain
import os
import json

class BlockchainTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.summary_group = QGroupBox("Blockchain Summary")
        self.summary_layout = QVBoxLayout()
        self.summary_group.setLayout(self.summary_layout)
        self.vbox.addWidget(self.summary_group)
        self.filter_box = QComboBox()
        self.filter_box.addItems(["All", "Page", "Chapter", "Book", "Part", "Series"])
        self.filter_box.currentIndexChanged.connect(self.load_blocks)
        self.vbox.addWidget(QLabel("Blockchain Explorer"))
        self.vbox.addWidget(self.filter_box)
        self.refresh_button = QPushButton("Refresh Blockchain")
        self.refresh_button.clicked.connect(self.load_blocks)
        self.vbox.addWidget(self.refresh_button)
        self.block_list = QListWidget()
        self.block_details = QTextEdit()
        self.block_details.setReadOnly(True)
        hbox = QHBoxLayout()
        hbox.addWidget(self.block_list, 2)
        hbox.addWidget(self.block_details, 3)
        self.vbox.addLayout(hbox)
        self.block_list.currentRowChanged.connect(self.display_block)
        self.load_blocks()

        # Auto-refresh every 10 seconds
        from PyQt5.QtCore import QTimer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_blocks)
        self.refresh_timer.start(10000)

    def load_blocks(self):
        self.block_list.clear()
        chain = Blockchain.load_chain()
        block_types = ["pages", "chapters", "books", "parts", "series"]
        filter_map = {
            "All": block_types,
            "Page": ["pages"],
            "Chapter": ["chapters"],
            "Book": ["books"],
            "Part": ["parts"],
            "Series": ["series"]
        }
        selected = self.filter_box.currentText() if hasattr(self, 'filter_box') else "All"
        blocks = []
        block_type_labels = []
        if isinstance(chain, dict):
            for level in block_types:
                if level in filter_map[selected]:
                    for b in chain.get(level, []):
                        blocks.append(b)
                        block_type_labels.append(level[:-1].capitalize())
        else:
            blocks = chain
            block_type_labels = ["Block"] * len(blocks)
        # Update summary (clear and repopulate QVBoxLayout)
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item:
                w = item.widget()
                if w:
                    w.deleteLater()
        total_blocks = sum(len(chain.get(level, [])) for level in block_types) if isinstance(chain, dict) else len(blocks)
        last_block_time = None
        for level in block_types:
            if isinstance(chain, dict) and chain.get(level):
                last_block_time = chain[level][-1].get('timestamp')
        self.summary_layout.addWidget(QLabel(f"Total Blocks: {total_blocks}"))
        self.summary_layout.addWidget(QLabel(f"Last Block Time: {str(last_block_time) if last_block_time else 'N/A'}"))
        # Populate list
        for i, (block, btype) in enumerate(zip(blocks, block_type_labels)):
            if isinstance(block, dict):
                ts = block.get('timestamp', 'N/A')
                action = block.get('data', {}).get('action', 'N/A')
                self.block_list.addItem(f"[{btype}] {i}: {action} @ {ts}")
            else:
                self.block_list.addItem(f"[{btype}] {i}: {str(block)}")
        if blocks:
            self.block_list.setCurrentRow(len(blocks)-1)

    def display_block(self, idx):
        chain = Blockchain.load_chain()
        if isinstance(chain, dict):
            blocks = []
            for level in ['pages', 'chapters', 'books', 'parts', 'series']:
                blocks.extend(chain.get(level, []))
        else:
            blocks = chain
        if 0 <= idx < len(blocks):
            block = blocks[idx]
            self.block_details.setPlainText(json.dumps(block, indent=2))
        else:
            self.block_details.clear()
