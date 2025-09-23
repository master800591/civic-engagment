import pytest
from civic_desktop.contracts.contract_terms import ContractManager, PlatformContract, ContractType, ContractSection
from civic_desktop.contracts.contract_types import MasterContract, CountryContract, StateContract, CityContract

@pytest.fixture
def contract_manager():
    return ContractManager(data_dir=':memory:')

def test_master_contract_hierarchy():
    master = MasterContract()
    assert master.contract_type == ContractType.MASTER
    assert any('Democratic Governance' in s.title for s in master.sections)

def test_country_contract_creation():
    country = CountryContract('United States')
    assert country.contract_type == ContractType.COUNTRY
    assert country.jurisdiction == 'United States'

def test_state_contract_creation():
    state = StateContract('California', 'United States')
    assert state.contract_type == ContractType.STATE
    assert state.jurisdiction == 'California'

def test_city_contract_creation():
    city = CityContract('San Francisco', 'California', 'United States')
    assert city.contract_type == ContractType.CITY
    assert city.jurisdiction == 'San Francisco'

def test_contract_acceptance_flow(contract_manager):
    master = MasterContract()
    master.activate()
    contract_manager.add_contract(master)
    user_email = 'test@example.com'
    user_location = {'country': '', 'state': '', 'city': ''}
    # Should require acceptance
    all_accepted, missing = contract_manager.check_all_required_accepted(user_email, user_location)
    assert not all_accepted
    assert len(missing) == 1
    # Accept contract
    contract_manager.record_acceptance(user_email, master.contract_id)
    all_accepted, missing = contract_manager.check_all_required_accepted(user_email, user_location)
    assert all_accepted
    assert missing == []
