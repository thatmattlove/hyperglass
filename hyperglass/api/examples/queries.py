# Third Party
import httpx

request = httpx.get("%s/api/queries")

print(request.json())
