from fastapi import FastAPI, HTTPException, Depends, Request, Body
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN
from typing import List, Dict
from collections import defaultdict

API_KEYS = {"your_secret_api_key1", "your_secret_api_key2", "your_secret_api_key3"}
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

items: List[str] = []
access_count: Dict[str, int] = defaultdict(int)  # API 키별 접속량을 추적하는 딕셔너리

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header in API_KEYS:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get(API_KEY_NAME)
        if api_key in API_KEYS:
            access_count[api_key] += 1
        response = await call_next(request)
        return response

app.add_middleware(AccessLogMiddleware)

@app.get("/items", response_model=List[str])
async def read_items():
    return items

@app.post("/items", response_model=List[str])
async def add_item(item: str = Body(..., embed=True), api_key: APIKey = Depends(get_api_key)):
    items.append(item)
    return items

@app.get("/access-counts")
async def get_access_counts():
    return access_count

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# curl http://localhost:8000/items
# curl -X POST "http://localhost:8000/items" -H "access_token: your_secret_api_key1" -H "Content-Type: application/json" -d "{\"item\":\"NewItem\"}"