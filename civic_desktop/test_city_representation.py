#!/usr/bin/env python3
"""
Test script for new city representation structure:
- Each city gets 2 senators and 2 representatives as base
- Cities over 200k population get 1 additional representative per 100k population
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from governance.city_elections import CityElectionConfig

def test_new_representation_structure():
    """Test the new representation calculation"""
    
    print("Testing new city representation structure...")
    print("=" * 60)
    
    # Test cases with different population sizes
    test_cities = [
        ("Small Town", 5000),
        ("Medium Town", 25000), 
        ("Large Town", 85000),
        ("Small City", 150000),
        ("Medium City", 250000),  # Should get 1 extra rep (50k over 200k)
        ("Large City", 450000),   # Should get 2 extra reps (250k over 200k)
        ("Major City", 750000),   # Should get 5 extra reps (550k over 200k)
        ("Metropolis", 1200000),  # Should get 10 extra reps (1M over 200k)
    ]
    
    for city_name, population in test_cities:
        config = CityElectionConfig(
            city_id=f"test_{city_name.lower().replace(' ', '_')}",
            city_name=city_name,
            state="Test State",
            country="Test Country",
            population_estimate=population
        )
        
        total_representatives = config.calculate_total_representatives()
        total_senators = config.calculate_total_senators()
        
        print(f"{city_name:12} (Pop: {population:8,})")
        print(f"  Representatives: {total_representatives:2} (Base: 2, Additional: {max(0, total_representatives-2)})")
        print(f"  Senators:        {total_senators:2} (Always 2)")
        
        # Verify calculations
        if population <= 200000:
            expected_reps = 2
        else:
            excess_population = population - 200000
            additional_reps = excess_population // 100000
            expected_reps = 2 + additional_reps
        
        assert total_representatives == expected_reps, f"Expected {expected_reps} reps, got {total_representatives}"
        assert total_senators == 2, f"Expected 2 senators, got {total_senators}"
        
        print(f"  ✓ Calculations correct")
        print()
    
    print("=" * 60)
    print("✅ All representation calculations passed!")
    
    # Test edge cases
    print("\nTesting edge cases:")
    print("-" * 30)
    
    # Exactly at threshold
    config_200k = CityElectionConfig(
        city_id="test_200k",
        city_name="Exactly 200k",
        state="Test State",
        country="Test Country", 
        population_estimate=200000
    )
    
    assert config_200k.calculate_total_representatives() == 2, "200k should have exactly 2 reps"
    print("✓ 200,000 population = 2 representatives (no additional)")
    
    # Just over threshold
    config_200k_plus_1 = CityElectionConfig(
        city_id="test_200k_plus_1",
        city_name="200k Plus 1", 
        state="Test State",
        country="Test Country",
        population_estimate=200001
    )
    
    assert config_200k_plus_1.calculate_total_representatives() == 2, "200,001 should still have 2 reps"
    print("✓ 200,001 population = 2 representatives (no additional until 300k)")
    
    # Exactly at first additional rep threshold
    config_300k = CityElectionConfig(
        city_id="test_300k",
        city_name="Exactly 300k",
        state="Test State",
        country="Test Country",
        population_estimate=300000
    )
    
    assert config_300k.calculate_total_representatives() == 3, "300k should have 3 reps"  
    print("✓ 300,000 population = 3 representatives (1 additional)")
    
    print("\n🎉 All tests passed! New representation structure is working correctly.")

if __name__ == "__main__":
    test_new_representation_structure()