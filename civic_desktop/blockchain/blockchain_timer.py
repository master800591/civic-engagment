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
        # Check if blockchain has genesis block first
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        # Don't create periodic blocks if no genesis exists
        if not pages:
            print("Blockchain Timer: No genesis block found, skipping periodic block creation")
            return
            
        # Don't create periodic blocks if first block isn't genesis
        first_block = pages[0]
        if first_block.get('data', {}).get('action') != 'genesis_creation':
            print("Blockchain Timer: First block is not genesis, skipping periodic block creation")
            return
        
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
        
        # Broadcast block if P2P is enabled
        if latest_block:
            try:
                from .p2p_manager import get_p2p_manager
                p2p_manager = get_p2p_manager()
                
                if p2p_manager.running:
                    result = p2p_manager.broadcast_block(latest_block)
                    if result['sent_to']:
                        print(f"✅ Block broadcast to {len(result['sent_to'])} peers")
                    elif result['failed'] or result['unreachable']:
                        print(f"⚠️ Block broadcast issues: {len(result['failed'])} failed, {len(result['unreachable'])} unreachable")
                else:
                    print("📡 P2P not running - block not broadcast")
            except Exception as e:
                print(f"❌ Block broadcast error: {e}")
                # Fallback to old broadcast method
                try:
                    from .p2p import broadcast_block
                    broadcast_block(latest_block)
                except Exception as fallback_e:
                    print(f"❌ Fallback broadcast also failed: {fallback_e}")
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
