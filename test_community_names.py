"""Test the new name mode for community validation."""

# Standard Library
import typing as t
from unittest.mock import Mock

# Third Party
from pydantic import ValidationError

# Project
from hyperglass.models.data.bgp_route import BGPRoute
from hyperglass.models.config.structured import StructuredCommunities


def test_community_validation_name_mode():
    """Test that name mode correctly appends friendly names to communities."""
    
    # Mock the state to return our test configuration
    from hyperglass import state
    
    # Create a mock structured config with name mode
    mock_structured = Mock()
    mock_structured.communities = StructuredCommunities(
        mode="name",
        names={
            "65000:1000:0": "Upstream Any",
            "65000:1001:0": "Upstream A (all locations)",
            "65000:1": "Test Community"
        }
    )
    
    # Mock the params with our structured config
    mock_params = Mock()
    mock_params.structured = mock_structured
    
    # Mock the use_state function to return our mock params
    original_use_state = getattr(state, 'use_state', None)
    state.use_state = Mock(return_value=mock_params)
    
    try:
        # Test data for BGP route
        test_data = {
            "prefix": "192.0.2.0/24",
            "active": True,
            "age": 3600,
            "weight": 100,
            "med": 0,
            "local_preference": 100,
            "as_path": [65000, 65001],
            "communities": [
                "65000:1000:0",  # Should get friendly name
                "65000:1001:0",  # Should get friendly name  
                "65000:9999:0",  # Should remain unchanged (no mapping)
                "65000:1",        # Should get friendly name
            ],
            "next_hop": "192.0.2.1",
            "source_as": 65001,
            "source_rid": "192.0.2.1",
            "peer_rid": "192.0.2.2",
            "rpki_state": 1
        }
        
        # Create BGPRoute instance
        route = BGPRoute(**test_data)
        
        # Check that communities have been transformed correctly
        expected_communities = [
            "65000:1000:0,Upstream Any",
            "65000:1001:0,Upstream A (all locations)",
            "65000:9999:0",  # No friendly name, stays unchanged
            "65000:1,Test Community"
        ]
        
        assert route.communities == expected_communities
        
    finally:
        # Restore original use_state function
        if original_use_state:
            state.use_state = original_use_state


def test_community_validation_permit_mode_unchanged():
    """Test that permit mode still works as before."""
    
    from hyperglass import state
    
    # Create a mock structured config with permit mode
    mock_structured = Mock()
    mock_structured.communities = StructuredCommunities(
        mode="permit",
        items=["^65000:.*$", "1234:1"]
    )
    
    mock_params = Mock()
    mock_params.structured = mock_structured
    
    original_use_state = getattr(state, 'use_state', None)
    state.use_state = Mock(return_value=mock_params)
    
    try:
        test_data = {
            "prefix": "192.0.2.0/24",
            "active": True,
            "age": 3600,
            "weight": 100,
            "med": 0,
            "local_preference": 100,
            "as_path": [65000, 65001],
            "communities": [
                "65000:100",  # Should be permitted (matches ^65000:.*$)
                "65001:200",  # Should be denied (doesn't match patterns)
                "1234:1",     # Should be permitted (exact match)
            ],
            "next_hop": "192.0.2.1",
            "source_as": 65001,
            "source_rid": "192.0.2.1",
            "peer_rid": "192.0.2.2",
            "rpki_state": 1
        }
        
        route = BGPRoute(**test_data)
        
        # Should only include permitted communities
        expected_communities = ["65000:100", "1234:1"]
        assert route.communities == expected_communities
        
    finally:
        if original_use_state:
            state.use_state = original_use_state


if __name__ == "__main__":
    test_community_validation_name_mode()
    test_community_validation_permit_mode_unchanged()
    print("All tests passed!")