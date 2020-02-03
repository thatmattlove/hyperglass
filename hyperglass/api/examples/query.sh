curl -X POST %s/api/query/ -d \
    '{
        "query_location": "router01",
        "query_type": "bgp_route",
        "query_vrf": "default",
        "query_target": "1.1.1.0/24"
    }'