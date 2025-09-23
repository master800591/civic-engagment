from PyQt5.QtCore import QTimer, QObject
from datetime import datetime, timezone
from .blockchain import Blockchain
from .p2p import broadcast_block

class BlockchainTimer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.create_periodic_block)
        self.timer.start(30 * 1000)  # 30 seconds in milliseconds (for testing)

    def create_periodic_block(self):
        block_hash = Blockchain.add_page(
            data={
                'action': 'periodic_block',
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'note': 'Periodic block created by timer.'
            },
            validator='SYSTEM',
            signature='PERIODIC'
        )
        # Broadcast the latest block to peers (find most recent from hierarchical chain)
        chain = Blockchain.load_chain()
        latest_block = None
        if isinstance(chain, dict):
            for level in ['series', 'parts', 'books', 'chapters', 'pages']:
                blocks = chain.get(level, [])
                if blocks:
                    latest_block = blocks[-1]
                    break
        elif isinstance(chain, list) and chain:
            latest_block = chain[-1]
        if latest_block:
            broadcast_block(latest_block)
        # Try to refresh the BlockchainTab if it exists
        try:
            from ..main_window import MainWindow
            mw = [w for w in QApplication.topLevelWidgets() if isinstance(w, MainWindow)]
            if mw:
                tabs = mw[0].centralWidget()
                for i in range(tabs.count()):
                    if tabs.tabText(i) == "Blockchain":
                        widget = tabs.widget(i)
                        if hasattr(widget, 'load_blocks'):
                            widget.load_blocks()
        except Exception:
            pass
