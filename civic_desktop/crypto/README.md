# Crypto Module - CivicCoin DeFi Ecosystem & Advanced Rewards System

## Purpose
Token-based incentive system with transparent ledger, civic engagement rewards, and peer-to-peer token economy to gamify democratic participation.

## Module Structure
```
crypto/
├── ledger.py             # Token ledger and transaction management
├── wallet_ui.py          # Wallet interface and token transfers
└── crypto_db.json       # Token balances, transactions, and rewards
```

## AI Implementation Instructions

### 1. CivicCoin DeFi Ecosystem Design
```python
# Comprehensive Token Reward System
class CivicTokenEconomy:
    def __init__(self):
        self.token_name = "CivicCoin"
        self.token_symbol = "CVC"
        self.initial_supply = 1000000  # 1 million tokens
        self.inflation_rate = 0.02     # 2% annual for sustainability
        
        # Token Distribution Strategy
        self.distribution = {
            'citizen_registration_bonus': 100,    # Welcome bonus for new users
            'daily_participation_reward': 5,      # Basic engagement reward
            'quality_argument_bonus': 25,         # Well-received debate contributions
            'vote_participation': 10,             # Voting in elections/referendums
            'training_completion': 50,            # Course completion bonuses
            'community_moderation': 30,           # Helpful moderation activities
            'constitutional_compliance': 20,      # Following platform principles
            'leadership_role_bonus': 200          # Monthly bonus for elected officials
        }
    
    def calculate_token_reward(self, action_type, user_email, context_data=None):
        """Calculate token reward based on civic participation"""
        
        base_reward = self.distribution.get(action_type, 0)
        if base_reward == 0:
            return 0, "No reward defined for this action type"
        
        # Load user profile for bonus calculations
        user = load_user(user_email)
        multipliers = self.calculate_reward_multipliers(user, action_type, context_data)
        
        # Apply Quality Multipliers
        quality_multiplier = 1.0
        if action_type == 'quality_argument_bonus' and context_data:
            quality_score = context_data.get('quality_score', 50)
            quality_multiplier = max(0.5, min(2.0, quality_score / 50))  # 0.5x to 2x multiplier
        
        # Apply Role-Based Multipliers
        role_multiplier = multipliers.get('role_multiplier', 1.0)
        
        # Apply Streak Bonuses
        streak_multiplier = multipliers.get('streak_multiplier', 1.0)
        
        # Calculate Final Reward
        final_reward = int(base_reward * quality_multiplier * role_multiplier * streak_multiplier)
        
        # Anti-Inflation Adjustment
        inflation_adjustment = self.calculate_inflation_adjustment()
        final_reward = int(final_reward * inflation_adjustment)
        
        return final_reward, "Reward calculated successfully"
    
    def award_tokens(self, recipient_email, amount, reason, source_action_id=None):
        """Award tokens with full audit trail"""
        
        # Validate Recipient
        recipient = load_user(recipient_email)
        if not recipient:
            return False, "Invalid recipient"
        
        # Create Token Award Record
        award_data = {
            'id': generate_unique_id(),
            'recipient_email': recipient_email,
            'amount': amount,
            'reason': reason,
            'source_action_id': source_action_id,
            'timestamp': datetime.now().isoformat(),
            'transaction_type': 'award',
            'verified': True
        }
        
        # Update Recipient Balance
        current_balance = self.get_user_balance(recipient_email)
        new_balance = current_balance + amount
        self.update_user_balance(recipient_email, new_balance)
        
        # Record Transaction
        self.record_transaction(award_data)
        
        # Blockchain Audit Trail
        Blockchain.add_page(
            action_type="token_awarded",
            data=award_data,
            user_email=recipient_email
        )
        
        # Notify User
        self.send_token_notification(recipient_email, award_data)
        
        return True, award_data['id']
```

### 2. Peer-to-Peer Token Transfer System
```python
# Secure Token Transfer with Validation
class TokenTransferManager:
    def transfer_tokens(self, sender_email, recipient_email, amount, reason, transfer_type='peer_transfer'):
        """Execute peer-to-peer token transfer"""
        
        # Validate Parties
        sender = load_user(sender_email)
        recipient = load_user(recipient_email)
        
        if not sender or not recipient:
            return False, "Invalid sender or recipient"
        
        # Validate Transfer Amount
        if amount <= 0:
            return False, "Transfer amount must be positive"
        
        sender_balance = self.get_user_balance(sender_email)
        if sender_balance < amount:
            return False, "Insufficient balance for transfer"
        
        # Anti-Fraud Checks
        fraud_check = self.validate_transfer_legitimacy(sender_email, recipient_email, amount, reason)
        if not fraud_check['valid']:
            return False, f"Transfer blocked: {fraud_check['reason']}"
        
        # Calculate Transfer Fees (if any)
        transfer_fee = self.calculate_transfer_fee(amount, transfer_type)
        total_deduction = amount + transfer_fee
        
        if sender_balance < total_deduction:
            return False, f"Insufficient balance including {transfer_fee} token fee"
        
        # Execute Transfer
        transfer_data = {
            'id': generate_unique_id(),
            'sender_email': sender_email,
            'recipient_email': recipient_email,
            'amount': amount,
            'fee': transfer_fee,
            'reason': reason,
            'transfer_type': transfer_type,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        # Update Balances
        self.update_user_balance(sender_email, sender_balance - total_deduction)
        recipient_balance = self.get_user_balance(recipient_email)
        self.update_user_balance(recipient_email, recipient_balance + amount)
        
        # Handle Transfer Fee (if any) - goes to platform sustainability fund
        if transfer_fee > 0:
            self.add_to_sustainability_fund(transfer_fee)
        
        # Record Transaction
        self.record_transaction(transfer_data)
        
        # Blockchain Recording
        Blockchain.add_page(
            action_type="token_transferred",
            data=transfer_data,
            user_email=sender_email
        )
        
        # Notifications
        self.send_transfer_notifications(transfer_data)
        
        return True, transfer_data['id']
    
    def request_tokens(self, requester_email, target_email, amount, reason, urgency='normal'):
        """Request tokens from another user"""
        
        # Validate Request
        if amount <= 0:
            return False, "Requested amount must be positive"
        
        # Check Request Frequency Limits
        recent_requests = self.get_recent_token_requests(requester_email)
        if len(recent_requests) >= 5:  # Max 5 requests per day
            return False, "Daily request limit exceeded"
        
        # Create Request Record
        request_data = {
            'id': generate_unique_id(),
            'requester_email': requester_email,
            'target_email': target_email,
            'amount': amount,
            'reason': reason,
            'urgency': urgency,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Store Request
        self.save_token_request(request_data)
        
        # Notify Target User
        self.send_token_request_notification(request_data)
        
        # Record Request
        Blockchain.add_page(
            action_type="token_requested",
            data=request_data,
            user_email=requester_email
        )
        
        return True, request_data['id']
    
    def validate_transfer_legitimacy(self, sender_email, recipient_email, amount, reason):
        """Anti-fraud and legitimacy validation"""
        
        # Check for Self-Transfer
        if sender_email == recipient_email:
            return {'valid': False, 'reason': 'Cannot transfer to yourself'}
        
        # Check Transfer Patterns for Suspicious Activity
        sender_history = self.get_transfer_history(sender_email, days=30)
        
        # Large Transfer Alert (over 500 tokens)
        if amount > 500:
            large_transfer_check = self.validate_large_transfer(sender_email, amount, reason)
            if not large_transfer_check['valid']:
                return large_transfer_check
        
        # Rapid Transfer Detection
        recent_transfers = [t for t in sender_history if 
                          (datetime.now() - datetime.fromisoformat(t['timestamp'])).seconds < 3600]
        
        if len(recent_transfers) > 10:  # More than 10 transfers in 1 hour
            return {'valid': False, 'reason': 'Transfer rate limit exceeded'}
        
        # Token Hoarding Detection
        sender_balance = self.get_user_balance(sender_email)
        if amount > sender_balance * 0.8:  # Transferring more than 80% of balance
            return {'valid': False, 'reason': 'Large percentage transfer requires additional verification'}
        
        return {'valid': True, 'reason': 'Transfer validated successfully'}
```

### 3. Gamified Reward Integration
```python
# Cross-Module Reward Integration
class CivicRewardIntegrator:
    def integrate_debate_rewards(self, argument_id, user_email):
        """Calculate and award tokens for debate participation"""
        
        argument = load_argument(argument_id)
        if not argument:
            return False, "Argument not found"
        
        # Base Participation Reward
        base_reward = 10  # Basic participation
        
        # Quality Multipliers
        quality_bonuses = 0
        
        # Community Feedback Bonus
        if argument.get('votes', {}).get('helpful', 0) > 5:
            quality_bonuses += 15  # Popular argument bonus
        
        # Source Quality Bonus
        if len(argument.get('sources', [])) >= 3:
            quality_bonuses += 10  # Well-sourced argument
        
        # Constitutional Compliance Bonus
        if argument.get('constitutional_compliant', True):
            quality_bonuses += 5  # Following platform principles
        
        # Calculate Final Reward
        total_reward = base_reward + quality_bonuses
        
        # Award Tokens
        return self.award_tokens(
            user_email, 
            total_reward, 
            f"Debate participation: {argument['topic_title']}", 
            argument_id
        )
    
    def integrate_training_rewards(self, course_completion_id, user_email):
        """Award tokens for training completion"""
        
        completion_data = load_course_completion(course_completion_id)
        
        # Base Course Completion Reward
        base_reward = 50
        
        # Performance Bonuses
        performance_bonuses = 0
        
        # High Score Bonus (>90%)
        if completion_data.get('final_score', 0) >= 90:
            performance_bonuses += 25
        
        # Speed Completion Bonus (faster than average)
        if completion_data.get('completion_time') < completion_data.get('average_time', float('inf')):
            performance_bonuses += 15
        
        # Certification Achievement Bonus
        if completion_data.get('certification_earned'):
            performance_bonuses += 50
        
        total_reward = base_reward + performance_bonuses
        
        return self.award_tokens(
            user_email,
            total_reward,
            f"Course completion: {completion_data['course_title']}",
            course_completion_id
        )
    
    def integrate_governance_rewards(self, governance_action_type, user_email, action_data):
        """Award tokens for governance participation"""
        
        GOVERNANCE_REWARDS = {
            'election_participation': 25,
            'constitutional_review': 100,    # Elder review work
            'legislation_proposal': 75,      # Representative initiative
            'public_comment': 10,            # Citizen engagement
            'moderation_review': 30,         # Community moderation
            'appeal_submission': 15,         # Due process participation
            'jury_service': 100              # Civic duty fulfillment
        }
        
        base_reward = GOVERNANCE_REWARDS.get(governance_action_type, 0)
        
        if base_reward == 0:
            return False, "No reward defined for governance action type"
        
        # Role-based multipliers
        user = load_user(user_email)
        role_multiplier = 1.0
        
        if user['role'] == 'Contract Elder' and governance_action_type == 'constitutional_review':
            role_multiplier = 1.5  # Elders get bonus for constitutional work
        elif user['role'] == 'Contract Representative' and governance_action_type == 'legislation_proposal':
            role_multiplier = 1.3  # Representatives get bonus for legislative work
        
        final_reward = int(base_reward * role_multiplier)
        
        return self.award_tokens(
            user_email,
            final_reward,
            f"Governance participation: {governance_action_type}",
            action_data.get('id')
        )
```

### 4. Token Economy Analytics and Sustainability
```python
# Economic Health Monitoring
class TokenEconomyAnalytics:
    def generate_economy_report(self):
        """Comprehensive token economy health report"""
        
        # Token Distribution Analysis
        total_supply = self.calculate_total_supply()
        circulation_metrics = self.analyze_token_circulation()
        
        # User Engagement Metrics
        active_users = self.count_active_token_users(days=30)
        transaction_volume = self.calculate_transaction_volume(days=30)
        
        # Reward Effectiveness
        reward_distribution = self.analyze_reward_distribution()
        participation_correlation = self.calculate_participation_correlation()
        
        # Economic Health Indicators
        inflation_rate = self.calculate_actual_inflation_rate()
        wealth_distribution = self.analyze_wealth_distribution()
        
        economy_report = {
            'total_supply': total_supply,
            'circulating_supply': circulation_metrics['circulating'],
            'held_in_wallets': circulation_metrics['held'],
            'active_users_30d': active_users,
            'transaction_volume_30d': transaction_volume,
            'average_balance': circulation_metrics['average_balance'],
            'median_balance': circulation_metrics['median_balance'],
            'reward_effectiveness': {
                'participation_increase': participation_correlation['participation_increase'],
                'reward_response_rate': participation_correlation['reward_response_rate'],
                'top_rewarded_activities': reward_distribution['top_activities']
            },
            'economic_health': {
                'inflation_rate': inflation_rate,
                'gini_coefficient': wealth_distribution['gini_coefficient'],
                'wealth_concentration': wealth_distribution['concentration'],
                'sustainability_score': self.calculate_sustainability_score()
            }
        }
        
        return economy_report
    
    def recommend_economy_adjustments(self, economy_report):
        """AI-powered recommendations for token economy optimization"""
        
        recommendations = []
        
        # Inflation Management
        if economy_report['economic_health']['inflation_rate'] > 0.05:  # > 5%
            recommendations.append({
                'type': 'inflation_control',
                'action': 'Reduce base reward amounts by 10%',
                'reason': 'High inflation detected, reducing token supply growth'
            })
        
        # Participation Incentives
        if economy_report['reward_effectiveness']['participation_increase'] < 0.1:  # < 10%
            recommendations.append({
                'type': 'participation_boost',
                'action': 'Increase quality argument bonuses by 25%',
                'reason': 'Low reward effectiveness, need stronger participation incentives'
            })
        
        # Wealth Distribution
        if economy_report['economic_health']['gini_coefficient'] > 0.7:  # High inequality
            recommendations.append({
                'type': 'wealth_redistribution',
                'action': 'Implement progressive reward scaling for new users',
                'reason': 'High wealth concentration, need to support newcomer participation'
            })
        
        # Transaction Volume
        if economy_report['transaction_volume_30d'] < active_users * 5:  # Low tx per user
            recommendations.append({
                'type': 'transaction_incentive',
                'action': 'Reduce transfer fees and add peer-recognition rewards',
                'reason': 'Low transaction volume, need to encourage token circulation'
            })
        
        return recommendations
```

## UI/UX Requirements

### Wallet Dashboard Interface
- **Balance Display**: Prominent token balance with transaction history
- **Reward Notifications**: Visual alerts for earned tokens with explanations
- **Transaction History**: Chronological list with clear transaction types
- **Spending Opportunities**: Clear options for using tokens within platform

### Token Transfer Interface
- **Simple Transfer**: Easy recipient selection with amount and reason fields
- **Request System**: Ability to request tokens with explanation and urgency
- **Transaction Validation**: Real-time balance checking and confirmation
- **Receipt System**: Automatic confirmations and blockchain references

### Rewards Dashboard Interface
- **Earning Summary**: Visual breakdown of token sources and activities
- **Achievement Progress**: Gamified progress toward reward milestones
- **Leaderboards**: Community recognition for civic participation
- **Economic Analytics**: Personal and platform-wide economic insights

## Blockchain Data Requirements
ALL crypto transactions recorded with these action types:
- `token_awarded`: Reward amount, recipient, reason, source activity
- `token_transferred`: Sender, recipient, amount, reason, transaction ID
- `token_penalty`: User, penalty amount, violation type, enforcement
- `reward_claimed`: User, claim type, amount, verification status
- `balance_updated`: User, old balance, new balance, transaction reference

## Database Schema
```json
{
  "balances": [
    {
      "user_email": "string",
      "balance": "number",
      "last_updated": "ISO timestamp"
    }
  ],
  "transactions": [
    {
      "id": "string",
      "type": "award|transfer|penalty|fee",
      "sender_email": "string",
      "recipient_email": "string", 
      "amount": "number",
      "reason": "string",
      "timestamp": "ISO timestamp",
      "blockchain_reference": "string"
    }
  ],
  "rewards_config": {
    "base_rewards": "object",
    "multipliers": "object",
    "inflation_rate": "number",
    "last_updated": "ISO timestamp"
  }
}
```

## Integration Points
- **Users Module**: User authentication and role-based reward multipliers
- **Debates Module**: Quality argument rewards and participation bonuses
- **Training Module**: Course completion rewards and certification bonuses
- **Governance**: All civic participation rewards and penalty system
- **Blockchain Module**: Immutable transaction records and audit trails

## Testing Requirements
- Token calculation algorithm accuracy
- Transfer validation and fraud prevention
- Reward distribution fairness and effectiveness
- Economic model sustainability analysis
- Cross-module reward integration verification
- Blockchain transaction integrity validation