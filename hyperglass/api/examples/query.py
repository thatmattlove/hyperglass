# Third Party
import httpx

query = {
    "query_location": "router01",
    "query_type": "bgp_route",
    "query_vrf": "default",
    "query_target": "1.1.1.0/24",
}

request = httpx.post("%s/api/query/", data=query)

print(request.json().get("output"))
