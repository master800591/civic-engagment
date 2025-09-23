import os
import json
from .constants import USERS_DB

ELECTIONS_DB = os.path.join(os.path.dirname(__file__), 'elections_db.json')

class ElectionManager:
    @staticmethod
    def get_jurisdiction_users(jur, value):
        # Prefer on-chain users when available
        try:
            from .backend import UserBackend  # lazy import to avoid circular
            users = UserBackend.load_users()
        except Exception:
            with open(USERS_DB, 'r', encoding='utf-8') as f:
                users = json.load(f)
        return [u for u in users if u.get(jur) == value]

    @staticmethod
    def should_trigger_election(jur, value):
        users = ElectionManager.get_jurisdiction_users(jur, value)
        return len(users) >= 50

    @staticmethod
    def start_election(jur, value, role):
        # Create a new election for the jurisdiction and role
        elections = ElectionManager.load_elections()
        election_id = f"{jur}_{value}_{role}_{len(elections)+1}"
        election = {
            'id': election_id,
            'jurisdiction': jur,
            'value': value,
            'role': role,
            'candidates': [],
            'votes': {},
            'status': 'open'
        }
        elections.append(election)
        ElectionManager.save_elections(elections)
        return election_id

    @staticmethod
    def load_elections():
        if not os.path.exists(ELECTIONS_DB):
            return []
        with open(ELECTIONS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_elections(elections):
        with open(ELECTIONS_DB, 'w', encoding='utf-8') as f:
            json.dump(elections, f, indent=2)

    @staticmethod
    def add_candidate(election_id, user_email):
        elections = ElectionManager.load_elections()
        for election in elections:
            if election['id'] == election_id and election['status'] == 'open':
                if user_email not in election['candidates']:
                    election['candidates'].append(user_email)
        ElectionManager.save_elections(elections)

    @staticmethod
    def cast_vote(election_id, voter_email, candidate_email):
        elections = ElectionManager.load_elections()
        for election in elections:
            if election['id'] == election_id and election['status'] == 'open':
                election['votes'][voter_email] = candidate_email
        ElectionManager.save_elections(elections)

    @staticmethod
    def close_election(election_id):
        elections = ElectionManager.load_elections()
        for election in elections:
            if election['id'] == election_id and election['status'] == 'open':
                election['status'] = 'closed'
        ElectionManager.save_elections(elections)

    @staticmethod
    def tally_votes(election_id):
        elections = ElectionManager.load_elections()
        for election in elections:
            if election['id'] == election_id:
                tally = {}
                for vote in election['votes'].values():
                    tally[vote] = tally.get(vote, 0) + 1
                return tally
        return {}
