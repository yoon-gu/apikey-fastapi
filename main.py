from fastapi import FastAPI, HTTPException, Depends, Body, Request
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN
from typing import List, Dict
from collections import defaultdict
from transformers import GPT2Tokenizer

API_KEYS = {"your_secret_api_key1", "your_secret_api_key2", "your_secret_api_key3"}
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

items: List[str] = []
access_count: Dict[str, int] = defaultdict(int)  # API 키별 접속량을 추적하는 딕셔너리

# GPT-2 토크나이저 초기화
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

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
async def read_items(api_key: APIKey = Depends(get_api_key)):
    return items

@app.post("/items", response_model=List[str])
async def add_item(item: str = Body(..., embed=True), api_key: APIKey = Depends(get_api_key)):
    items.append(item)
    return items

@app.get("/access-counts", response_model=Dict[str, int])
async def get_access_counts(api_key: APIKey = Depends(get_api_key)):
    return access_count

@app.post("/encode", response_model=Dict[str, List[int]])
async def encode_text(text: str = Body(..., embed=True), api_key: APIKey = Depends(get_api_key)):
    encoded_text = tokenizer.encode(text)
    return {"encoded_text": encoded_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# curl http://localhost:8000/items
# curl -X POST "http://localhost:8000/items" -H "access_token: your_secret_api_key1" -H "Content-Type: application/json" -d "{\"item\":\"NewItem\"}"
# curl -X POST "http://localhost:8000/encode" -H "access_token: your_secret_api_key1" -H "Content-Type: application/json" -d "{\"text\":\"Hello, world\"}"