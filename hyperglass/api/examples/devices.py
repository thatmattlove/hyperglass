# Third Party
import httpx

request = httpx.get("%s/api/devices")

print(request.json())
