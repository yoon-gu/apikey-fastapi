from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN
from typing import List

API_KEYS = {"your_secret_api_key1", "your_secret_api_key2", "your_secret_api_key3"}  # 사용할 API 키들
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

items: List[str] = []  # 아이템을 저장할 리스트

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header in API_KEYS:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

@app.get("/items", response_model=List[str])
async def read_items():
    return items

@app.post("/items", response_model=List[str])
async def add_item(item: str, api_key: APIKey = Depends(get_api_key)):
    items.append(item)
    return items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# curl http://localhost:8000/items
# curl -X POST -H "access_token: your_secret_api_key1" -d "item=NewItem" http://localhost:8000/items