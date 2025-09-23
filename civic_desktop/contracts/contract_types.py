# contracts/contract_types.py
# Predefined Contract Types for Hierarchical Governance
"""
Implements specific contract types with predefined sections:
- MasterContract: Constitutional framework (overrides all)
- CountryContract: National governance rules
- StateContract: Regional governance rules  
- CityContract: Local governance rules
"""

from datetime import datetime
from typing import Dict, Any
from .contract_terms import PlatformContract, ContractSection, ContractType


class MasterContract(PlatformContract):
    """
    Master Constitutional Contract - Overrides ALL other contracts
    Establishes fundamental platform governance principles
    """
    
    def __init__(self) -> None:
        super().__init__(ContractType.MASTER, "Constitutional")
        self.version = "1.0"
        self.contract_id = "MASTER_CONSTITUTIONAL_2024"
        
        # Constitutional sections that cannot be overridden
        self._add_constitutional_sections()
    
    def _add_constitutional_sections(self) -> None:
        """Add constitutional sections that form the platform foundation"""
        
        # Section 1: Democratic Governance
        democratic_governance = ContractSection(
            section_id="CONST_001_DEMOCRACY",
            title="Democratic Governance Principles",
            intent="Establish democratic governance as the fundamental organizing principle",
            reason="Democracy ensures all voices are heard and tyranny is prevented through representation",
            objective="Create a system where power flows from the citizens through elected representatives with constitutional constraints",
            content="""
            DEMOCRATIC GOVERNANCE FRAMEWORK:
            
            1. CITIZEN SOVEREIGNTY: All legitimate authority derives from the consent of Contract Citizens
            2. REPRESENTATIVE DEMOCRACY: Citizens elect Contract Representatives to govern on their behalf
            3. SEPARATION OF POWERS: Legislative (Representatives/Senators), Executive (day-to-day operations), Judicial (Elders)
            4. CHECKS AND BALANCES: No single branch may exercise unchecked power
            5. CONSTITUTIONAL SUPREMACY: This Master Contract supersedes all other governance documents
            6. REGULAR ELECTIONS: Representatives serve limited terms and face regular electoral accountability
            7. MINORITY PROTECTION: Constitutional rights that cannot be voted away by majorities
            8. DUE PROCESS: Fair procedures for all governance decisions affecting individual citizens
            """,
            effective_date=datetime.now().isoformat(),
            precedence=1,
            requires_agreement=True
        )
        self.add_section(democratic_governance)
        
        # Section 2: Contract Hierarchy
        contract_hierarchy = ContractSection(
            section_id="CONST_002_HIERARCHY",
            title="Constitutional Contract Hierarchy",
            intent="Establish clear precedence order for resolving conflicting governance rules",
            reason="Prevents governance chaos by providing clear conflict resolution mechanism",
            objective="Ensure Master Contract provisions cannot be overridden by any lower-level governance documents",
            content="""
            CONTRACT PRECEDENCE ORDER (highest to lowest):
            
            1. MASTER CONTRACT (Constitutional): Overrides all other contracts and governance documents
            2. COUNTRY CONTRACTS: National-level governance, subject to Constitutional constraints
            3. STATE CONTRACTS: Regional governance, subject to Constitutional and Country constraints  
            4. CITY CONTRACTS: Local governance, subject to all higher-level constraints
            
            CONFLICT RESOLUTION RULES:
            - Higher precedence always controls in case of conflict
            - Constitutional rights cannot be diminished by any lower contract
            - Emergency powers are subject to constitutional review and citizen oversight
            - Contract amendments require supermajority approval and constitutional compliance review
            """,
            effective_date=datetime.now().isoformat(),
            precedence=2,
            requires_agreement=True
        )
        self.add_section(contract_hierarchy)
        
        # Section 3: Fundamental Rights
        fundamental_rights = ContractSection(
            section_id="CONST_003_RIGHTS", 
            title="Fundamental Citizen Rights",
            intent="Guarantee inalienable rights that protect individual liberty and human dignity",
            reason="Rights provide essential protections against both majority tyranny and government overreach",
            objective="Establish constitutional rights that cannot be voted away or overridden by any governance body",
            content="""
            INALIENABLE CITIZEN RIGHTS:
            
            1. FREE EXPRESSION: Right to speak, write, debate, and criticize governance without fear of retaliation
            2. DUE PROCESS: Right to fair treatment in all moderation and governance procedures with appeal rights
            3. EQUAL PARTICIPATION: Equal access to platform features, elections, and democratic processes regardless of background
            4. PRIVACY PROTECTION: Personal data security and freedom from unreasonable government surveillance
            5. EQUAL TREATMENT: Protection from discrimination based on race, religion, gender, nationality, or political views
            6. DEMOCRATIC PARTICIPATION: Right to vote, run for office, petition government, and participate in governance
            7. PEACEFUL ASSEMBLY: Right to organize, associate, and petition for redress of grievances
            8. CONSTITUTIONAL APPEAL: Right to challenge any governance action that violates constitutional principles
            
            RIGHTS ENFORCEMENT:
            - These rights cannot be suspended except during constitutional emergencies with strict oversight
            - All governance actions must respect these rights or face constitutional review
            - Citizens may appeal any rights violation to Contract Elders for constitutional review
            - Emergency powers cannot override core rights without supermajority approval and sunset clauses
            """,
            effective_date=datetime.now().isoformat(),
            precedence=3,
            requires_agreement=True
        )
        self.add_section(fundamental_rights)
        
        # Section 4: Governance Structure
        governance_structure = ContractSection(
            section_id="CONST_004_STRUCTURE",
            title="Constitutional Governance Structure", 
            intent="Define the structure of democratic governance with proper checks and balances",
            reason="Structured governance prevents concentration of power and ensures democratic accountability",
            objective="Create a system of overlapping authorities that prevents any single point of control",
            content="""
            GOVERNANCE BRANCHES AND POWERS:
            
            CONTRACT CITIZENS (Sovereign Authority):
            - Electoral power: Vote in all elections and referendums
            - Initiative power: Propose constitutional amendments (40% petition + 55% approval)
            - Recall power: Remove any elected official through special elections
            - Ultimate sovereignty: Source of all legitimate democratic authority
            
            CONTRACT REPRESENTATIVES (Legislative Branch):
            - Legislative initiative: Create and propose platform policies
            - Budget authority: Control platform resource allocation
            - Impeachment power: Remove other officials for constitutional violations
            - Term: 2 years, unlimited terms, direct citizen election
            
            CONTRACT SENATORS (Deliberative Branch):
            - Legislative review: Must approve Representative proposals
            - Confirmation authority: Approve major appointments
            - Override power: Can override Elder vetoes with 67% supermajority
            - Term: 6 years, max 2 consecutive terms, mixed election system
            
            CONTRACT ELDERS (Constitutional Branch):
            - Constitutional veto: Block proposals violating platform principles (60% required)
            - Judicial review: Interpret governance contracts and resolve disputes
            - Elder veto: Override harmful decisions (75% required)  
            - Term: 4 years, renewable, max 3 consecutive terms
            
            CONTRACT FOUNDERS (Emergency Authority):
            - Constitutional amendment: Modify core governance (75% consensus required)
            - Emergency protocols: Override during platform-threatening situations
            - Limited scope: Cannot govern day-to-day operations
            - Removal: Subject to 2/3 vote of Elders + Senators combined
            """,
            effective_date=datetime.now().isoformat(),
            precedence=4,
            requires_agreement=True
        )
        self.add_section(governance_structure)
        
        # Section 5: Amendment Process
        amendment_process = ContractSection(
            section_id="CONST_005_AMENDMENTS",
            title="Constitutional Amendment Process",
            intent="Provide mechanism for constitutional evolution while preventing hasty changes",
            reason="Constitutions must be amendable but not easily manipulated by temporary majorities",
            objective="Balance democratic change with constitutional stability through deliberate processes",
            content="""
            CONSTITUTIONAL AMENDMENT PROCEDURES:
            
            INITIATION (Two Methods):
            1. Contract Founder Proposal: 75% of Contract Founders agree to propose amendment
            2. Citizen Initiative: 40% of active citizens petition for amendment with specific text
            
            LEGISLATIVE APPROVAL:
            1. Contract Representatives: 60% approval required
            2. Contract Senators: 60% approval required  
            3. Both chambers must approve identical text
            
            CONSTITUTIONAL REVIEW:
            1. Contract Elders review for constitutional compliance and wisdom
            2. Can recommend modifications but cannot block citizen-initiated amendments
            3. Must provide written analysis of amendment implications
            
            CITIZEN RATIFICATION:
            1. Platform-wide referendum with 55% turnout requirement
            2. 60% approval required for ratification
            3. 30-day public debate period before voting
            4. Equal time for supporters and opponents
            
            IMPLEMENTATION:
            1. 6-month implementation period with technical review
            2. Contract Elders monitor implementation for constitutional compliance
            3. Emergency suspension possible only for platform-threatening technical issues
            
            LIMITATIONS:
            - Fundamental rights in Section 3 cannot be eliminated by amendment
            - Democratic governance principles cannot be suspended
            - Amendment process itself cannot be made impossible
            """,
            effective_date=datetime.now().isoformat(),
            precedence=5,
            requires_agreement=True
        )
        self.add_section(amendment_process)


class CountryContract(PlatformContract):
    """
    Country-level contract for national governance rules
    Subject to Master Contract constraints
    """
    
    def __init__(self, country: str):
        super().__init__(ContractType.COUNTRY, country)
        self.contract_id = f"COUNTRY_{country.upper()}_{datetime.now().strftime('%Y%m%d')}"
        self.version = "1.0"
        
        # Add standard country-level sections
        self._add_country_sections(country)
    
    def _add_country_sections(self, country: str):
        """Add standard sections for country-level governance"""
        
        # National representation
        national_representation = ContractSection(
            section_id=f"COUNTRY_{country.upper()}_001_REPRESENTATION",
            title="National Representation Standards",
            intent="Establish representation standards for national-level elections",
            reason="Ensures fair representation while respecting national sovereignty",
            objective="Create balanced representation that reflects national political structure",
            content=f"""
            NATIONAL REPRESENTATION FRAMEWORK FOR {country.upper()}:
            
            1. ELECTORAL DISTRICTS: Representation based on population with geographic considerations
            2. NATIONAL LANGUAGE: Primary platform language for {country} governance
            3. CULTURAL SENSITIVITY: Governance must respect national traditions and values
            4. LEGAL COMPLIANCE: All platform activities must comply with {country} law
            5. SOVEREIGNTY RESPECT: National governance decisions take precedence over platform operations within constitutional limits
            
            REPRESENTATION ALLOCATION:
            - Contract Representatives: Direct election by geographic districts
            - Contract Senators: Mixed system respecting national federal structure
            - Contract Elders: Nominated by national representatives, confirmed by citizens
            
            Subject to Master Contract constitutional constraints.
            """,
            effective_date=datetime.now().isoformat(),
            precedence=10,
            requires_agreement=True
        )
        self.add_section(national_representation)
        
        # Legal compliance
        legal_compliance = ContractSection(
            section_id=f"COUNTRY_{country.upper()}_002_LEGAL",
            title="National Legal Compliance",
            intent="Ensure platform operations comply with national law while maintaining democratic principles",
            reason="Platform must operate within legal framework while preserving constitutional governance",
            objective="Balance legal compliance with platform constitutional protections",
            content=f"""
            LEGAL COMPLIANCE FRAMEWORK FOR {country.upper()}:
            
            1. LAW SUPREMACY: {country} law takes precedence over platform operations where applicable
            2. CONSTITUTIONAL PROTECTION: Platform constitutional rights cannot be waived except where required by law
            3. CONFLICT RESOLUTION: Legal conflicts resolved through established national courts
            4. EMERGENCY PROCEDURES: National emergency powers recognized within constitutional limits
            5. PRIVACY LAWS: Compliance with national data protection and privacy regulations
            
            GOVERNANCE INTERACTION:
            - Platform governance must respect national legal framework
            - Constitutional rights protected to maximum extent allowed by law
            - Legal challenges resolved through national court system
            - Platform constitutional protections apply unless overridden by law
            
            This section cannot override Master Contract fundamental rights except where required by {country} law.
            """,
            effective_date=datetime.now().isoformat(),
            precedence=11,
            requires_agreement=True
        )
        self.add_section(legal_compliance)


class StateContract(PlatformContract):
    """
    State/Regional level contract for regional governance
    Subject to Master and Country contract constraints
    """
    
    def __init__(self, state: str, country: str = ""):
        super().__init__(ContractType.STATE, state)
        self.country = country
        self.contract_id = f"STATE_{state.upper()}_{datetime.now().strftime('%Y%m%d')}"
        self.version = "1.0"
        
        # Add standard state-level sections
        self._add_state_sections(state, country)
    
    def _add_state_sections(self, state: str, country: str):
        """Add standard sections for state-level governance"""
        
        # Regional representation
        regional_representation = ContractSection(
            section_id=f"STATE_{state.upper()}_001_REPRESENTATION",
            title="Regional Representation Framework",
            intent="Establish regional representation reflecting state political structure",
            reason="Regional governance must reflect local political traditions and structures",
            objective="Balance regional autonomy with national and constitutional requirements",
            content=f"""
            REGIONAL REPRESENTATION FOR {state.upper()}:
            
            1. REGIONAL DISTRICTS: Electoral districts based on existing state political boundaries
            2. LOCAL REPRESENTATION: Representation reflects state's internal political structure
            3. CULTURAL RECOGNITION: State cultural and political traditions respected in governance
            4. RESOURCE ALLOCATION: Regional resources allocated according to state priorities
            5. INTER-STATE COOPERATION: Coordination with other states on shared issues
            
            REPRESENTATION STRUCTURE:
            - Contract Representatives: Elected from state districts according to state law
            - Regional coordination: Interface with state government structures
            - Resource sharing: Cooperation with adjacent states on shared concerns
            
            Subject to Master Contract and {country} Country Contract constraints.
            """,
            effective_date=datetime.now().isoformat(),
            precedence=20,
            requires_agreement=True
        )
        self.add_section(regional_representation)
        
        # State law integration
        state_law_integration = ContractSection(
            section_id=f"STATE_{state.upper()}_002_LAW",
            title="State Law Integration",
            intent="Integrate platform governance with state legal and political framework",
            reason="Platform must work within existing state governance structures",
            objective="Harmonize platform democracy with state constitutional and legal requirements",
            content=f"""
            STATE LAW INTEGRATION FOR {state.upper()}:
            
            1. STATE LAW COMPLIANCE: Platform operations comply with {state} state law
            2. CONSTITUTIONAL HARMONY: Platform governance respects state constitutional principles
            3. GOVERNMENT COORDINATION: Coordination with state government where appropriate
            4. LEGAL RESOLUTION: State courts handle legal disputes where applicable
            5. EMERGENCY COORDINATION: Coordination with state emergency management
            
            GOVERNANCE INTEGRATION:
            - Platform representatives may coordinate with state officials
            - State emergency powers recognized within constitutional limits
            - Legal compliance follows state law hierarchy
            - Constitutional protections maintained within legal constraints
            
            Cannot override Master Contract or applicable Country Contract provisions.
            """,
            effective_date=datetime.now().isoformat(),
            precedence=21,
            requires_agreement=True
        )
        self.add_section(state_law_integration)


class CityContract(PlatformContract):
    """
    City/Local level contract for municipal governance
    Subject to Master, Country, and State contract constraints
    """
    
    def __init__(self, city: str, state: str = "", country: str = ""):
        super().__init__(ContractType.CITY, city)
        self.state = state
        self.country = country
        self.contract_id = f"CITY_{city.upper()}_{datetime.now().strftime('%Y%m%d')}"
        self.version = "1.0"
        
        # Add standard city-level sections
        self._add_city_sections(city, state, country)
    
    def _add_city_sections(self, city: str, state: str, country: str):
        """Add standard sections for city-level governance"""
        
        # Local representation
        local_representation = ContractSection(
            section_id=f"CITY_{city.upper()}_001_REPRESENTATION",
            title="Local Representation Framework",
            intent="Establish local representation reflecting municipal structure and needs",
            reason="Local governance must be responsive to immediate community needs and preferences",
            objective="Create responsive local governance that addresses specific municipal concerns",
            content=f"""
            LOCAL REPRESENTATION FOR {city.upper()}:
            
            1. NEIGHBORHOOD REPRESENTATION: Representation by neighborhood or district within city
            2. LOCAL ISSUES FOCUS: Platform governance addresses local municipal concerns
            3. COMMUNITY ENGAGEMENT: High citizen participation in local decision-making
            4. MUNICIPAL COORDINATION: Coordination with existing city government structures
            5. LOCAL RESOURCE MANAGEMENT: Community control over local platform resources
            
            REPRESENTATION STRUCTURE:
            - Contract Representatives: Elected from city districts/neighborhoods
            - Local priorities: Focus on municipal services and community needs
            - Direct democracy: Enhanced citizen participation in local issues
            - Municipal interface: Coordination with city government where appropriate
            
            Subject to Master Contract, {country} Country Contract, and {state} State Contract constraints.
            """,
            effective_date=datetime.now().isoformat(),
            precedence=30,
            requires_agreement=True
        )
        self.add_section(local_representation)
        
        # Municipal integration
        municipal_integration = ContractSection(
            section_id=f"CITY_{city.upper()}_002_MUNICIPAL",
            title="Municipal Government Integration",
            intent="Integrate platform governance with existing municipal government structures",
            reason="Platform must complement rather than conflict with municipal governance",
            objective="Create synergy between platform democracy and municipal government",
            content=f"""
            MUNICIPAL INTEGRATION FOR {city.upper()}:
            
            1. MUNICIPAL COOPERATION: Platform governance cooperates with city government
            2. SERVICE COORDINATION: Coordination on civic services and community needs
            3. LOCAL LAW COMPLIANCE: Compliance with city ordinances and regulations  
            4. COMMUNITY BENEFIT: Platform activities benefit overall community welfare
            5. RESOURCE SHARING: Appropriate sharing of resources for community benefit
            
            INTEGRATION FRAMEWORK:
            - Platform representatives may coordinate with city officials
            - Municipal law compliance required within constitutional limits
            - Community benefit prioritized in local governance decisions
            - Local emergency coordination with municipal authorities
            
            Cannot override Master Contract, Country Contract, or State Contract provisions.
            All higher-level constitutional protections remain in effect.
            """,
            effective_date=datetime.now().isoformat(),
            precedence=31,
            requires_agreement=True
        )
        self.add_section(municipal_integration)


def create_default_contracts() -> Dict[str, Any]:
    """
    Create standard set of default contracts for common jurisdictions
    Returns dictionary of contract_id -> contract mappings
    """
    contracts: Dict[str, Any] = {}
    
    # Master constitutional contract
    master = MasterContract()
    master.activate()
    contracts[master.contract_id] = master
    
    # Sample country contracts
    usa_contract = CountryContract("United States")
    usa_contract.activate()
    contracts[usa_contract.contract_id] = usa_contract
    
    canada_contract = CountryContract("Canada")
    canada_contract.activate()
    contracts[canada_contract.contract_id] = canada_contract
    
    # Sample state contracts
    california_contract = StateContract("California", "United States")
    california_contract.activate()
    contracts[california_contract.contract_id] = california_contract
    
    texas_contract = StateContract("Texas", "United States")
    texas_contract.activate()
    contracts[texas_contract.contract_id] = texas_contract
    
    ontario_contract = StateContract("Ontario", "Canada")
    ontario_contract.activate()
    contracts[ontario_contract.contract_id] = ontario_contract
    
    # Sample city contracts
    sf_contract = CityContract("San Francisco", "California", "United States")
    sf_contract.activate()
    contracts[sf_contract.contract_id] = sf_contract
    
    austin_contract = CityContract("Austin", "Texas", "United States")
    austin_contract.activate()
    contracts[austin_contract.contract_id] = austin_contract
    
    toronto_contract = CityContract("Toronto", "Ontario", "Canada")
    toronto_contract.activate()
    contracts[toronto_contract.contract_id] = toronto_contract
    
    return contracts