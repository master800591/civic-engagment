import datetime as dt
from civic_desktop.blockchain.blockchain import Blockchain, BlockchainIntegrator
from civic_desktop.users.backend import UserBackend

class NetworkReports:
    @staticmethod
    def credit_ratio_report():
        """Report: Current credits per user and network inflation status"""
        users = UserBackend.load_users()
        total_credits = sum(BlockchainIntegrator.get_user_credits(u['email']) for u in users)
        user_count = len(users)
        ratio = round(total_credits / max(1, user_count), 2)
        return {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
            'user_count': user_count,
            'total_credits': total_credits,
            'credits_per_user': ratio,
            'target_ratio': 2000,
            'inflation_status': 'high' if ratio > 2200 else 'low' if ratio < 1800 else 'stable'
        }

    @staticmethod
    def network_pool_report():
        """Report: Current network pool and last payout"""
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        total_pool = sum(page.get('data', {}).get('amount', 0.0) for page in pages if page.get('data', {}).get('action') == 'network_fee')
        last_payout = next((page for page in reversed(pages) if page.get('data', {}).get('action') == 'network_pool_payout'), None)
        return {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
            'total_pool': total_pool,
            'last_payout': last_payout.get('data', {}) if last_payout else None
        }

    @staticmethod
    def user_balances_report():
        """Report: All user balances and credits"""
        users = UserBackend.load_users()
        report = []
        for u in users:
            report.append({
                'email': u['email'],
                'balance': BlockchainIntegrator.get_user_balance(u['email']),
                'credits': BlockchainIntegrator.get_user_credits(u['email'])
            })
        return {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
            'users': report
        }
