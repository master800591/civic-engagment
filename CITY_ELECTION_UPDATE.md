# CITY/TOWN ELECTION SYSTEM - UPDATED REPRESENTATION STRUCTURE

## Overview
The city/town election system has been updated with a new representation structure as requested:
- **Base Representation**: Every city/town gets 2 senators and 2 representatives
- **Population Scaling**: Cities over 200,000 population get 1 additional representative per 100,000 population

## Updated Representation Formula

### Senators
- **All cities/towns**: Exactly **2 senators** (no variation by population)

### Representatives  
- **Base**: All cities/towns get **2 representatives**
- **Large City Bonus**: Cities over 200,000 population get additional representatives:
  - Formula: `2 + ((population - 200,000) / 100,000)` (integer division)
  
### Population Examples

| Population | Senators | Base Reps | Additional Reps | Total Reps |
|------------|----------|-----------|-----------------|------------|
| 5,000      | 2        | 2         | 0               | 2          |
| 25,000     | 2        | 2         | 0               | 2          |
| 85,000     | 2        | 2         | 0               | 2          |
| 150,000    | 2        | 2         | 0               | 2          |
| 200,000    | 2        | 2         | 0               | 2          |
| 250,000    | 2        | 2         | 0               | 2          |
| 300,000    | 2        | 2         | 1               | 3          |
| 450,000    | 2        | 2         | 2               | 4          |
| 750,000    | 2        | 2         | 5               | 7          |
| 1,200,000  | 2        | 2         | 10              | 12         |

## Key Changes Made

### 1. CityElectionConfig Updates
```python
# New configuration parameters
base_representatives: int = 2           # Every city gets 2 base representatives  
base_senators: int = 2                  # Every city gets 2 senators
large_city_threshold: int = 200000      # Population threshold for additional reps
additional_rep_per_population: int = 100000  # 1 additional rep per 100k over threshold

# New calculation methods
def calculate_total_representatives(self) -> int:
    """Calculate total representatives based on population"""
    base_reps = self.base_representatives  # Always 2
    
    if self.population_estimate > self.large_city_threshold:
        excess_population = self.population_estimate - self.large_city_threshold  
        additional_reps = excess_population // self.additional_rep_per_population
        return base_reps + additional_reps
    
    return base_reps

def calculate_total_senators(self) -> int:
    """Calculate total senators (always 2 for all cities)"""
    return self.base_senators  # Always 2 senators
```

### 2. Election Scheduling Updates
- **Initial Elections**: Use `calculate_total_representatives()` and `calculate_total_senators()` to determine offices to contest
- **Expansion Elections**: Check current office holders vs. required representation and schedule elections for additional positions as needed
- **Blockchain Integration**: Updated to properly handle blockchain return values and record total representation requirements

### 3. Election Configuration Parameters
All city election configurations now use the standardized structure:

```python
# Standard configuration for all cities
{
    "base_representatives": 2,      # Base representatives for all cities
    "base_senators": 2,            # Base senators for all cities  
    "large_city_threshold": 200000, # Population threshold for additional reps
    "additional_rep_per_population": 100000,  # Additional rep per 100k population
    "initial_threshold_percent": 0.01,  # 1% population to trigger first election
    "expansion_threshold_percent": 0.50,  # 50% population to trigger expansion
    "term_length_years": 1,             # 1-year terms
    "max_consecutive_terms": 4,         # Maximum 4 terms  
    "consecutive_term_restriction": True, # Cannot serve consecutive terms
    "campaign_period_days": 30,         # 30-day campaign period
    "voting_period_days": 7            # 7-day voting period
}
```

## Election Triggers

### Initial Election (1% Population Threshold)
- **Trigger**: When 1% of city population becomes platform members
- **Offices Contested**: All required positions (2 senators + calculated representatives)
- **Purpose**: Establish full municipal government representation

### Expansion Election (50% Population Threshold)  
- **Trigger**: When 50% of city population becomes platform members
- **Offices Contested**: Any additional representative positions required by population growth
- **Purpose**: Ensure representation keeps pace with membership growth

## Term Management

### Term Limits
- **Length**: 1 year terms
- **Maximum**: 4 total terms per person per office
- **Restriction**: Terms cannot be consecutive (must sit out at least 1 term between service)

### Eligibility Rules
- Must be city resident and platform member
- Cannot have served previous consecutive term
- Cannot exceed 4 lifetime terms for the office
- Must pass constitutional compliance checks

## Technical Implementation

### Core Files Updated
- **`governance/city_elections.py`**: Core election management system with new representation formulas
- **`governance/city_election_ui.py`**: PyQt5 user interface for election management
- **`test_city_elections.py`**: Comprehensive testing framework
- **`test_city_representation.py`**: Specific tests for new representation structure

### Database Structure
Elections are stored in JSON format with full audit trails:

```json
{
    "cities": {
        "city_id": {
            "city_name": "Democracy City",
            "state": "Liberty State", 
            "country": "Democratic Republic",
            "population_estimate": 250000,
            "base_representatives": 2,
            "base_senators": 2,
            "large_city_threshold": 200000,
            "additional_rep_per_population": 100000
        }
    },
    "scheduled_elections": {},
    "active_elections": {},
    "completed_elections": {},
    "population_tracking": {}
}
```

### Blockchain Integration
All election activities are recorded on blockchain for transparency:
- City registration with representation calculations
- Election scheduling with office requirements  
- Candidate registration and eligibility verification
- Voting results and winner determination
- Term completion and succession planning

## User Interface Integration

### Main Application
- New **🏛️ City Elections** tab in main civic platform window
- Integrated with existing user authentication and blockchain systems
- Role-based access controls for election management

### Election Management Dashboard
- City registration and configuration interface
- Population tracking and threshold monitoring
- Candidate registration and management
- Election scheduling and results display
- Term limit tracking and succession planning

## Testing and Validation

### Automated Tests
- Population threshold calculations
- Representation formula verification
- Election scheduling workflows
- Term limit enforcement
- Candidate eligibility verification

### Manual Testing
- Complete election workflows from registration to results
- Population growth scenarios and representation updates
- Term limit edge cases and succession planning
- User interface functionality across all election phases

## Future Enhancements

### Potential Improvements
- **Real-time Population Updates**: Integration with census data or membership growth tracking
- **Cross-City Coordination**: Regional cooperation between municipal governments
- **Advanced Analytics**: Voting pattern analysis and civic engagement metrics
- **Mobile Integration**: Mobile app support for voting and candidate information

### Scalability Considerations
- System handles cities from 1,000 to 10+ million population
- Blockchain storage scales with hierarchical structure
- Database optimization for large numbers of simultaneous elections
- UI performance optimization for cities with many candidates

## Summary

The updated city/town election system now provides:

1. **Standardized Base Representation**: Every municipality gets 2 senators and 2 representatives
2. **Population-Based Scaling**: Additional representatives for large cities (1 per 100k over 200k)
3. **Consistent Election Triggers**: 1% for initial elections, 50% for expansion elections  
4. **Term Limit Enforcement**: 1-year terms, 4-term maximum, non-consecutive restriction
5. **Full Blockchain Transparency**: Complete audit trail of all election activities
6. **User-Friendly Interface**: Integrated municipal election management dashboard

This provides a fair, scalable, and transparent system for municipal democratic governance that grows with city size while maintaining democratic principles and preventing concentration of power.