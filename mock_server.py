from fastapi import FastAPI
from fastapi.responses import JSONResponse
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
app = FastAPI()

# In-memory mock database
mock_db = {
    "users": [{"id": i, "username": fake.user_name()} for i in range(1, 101)],
    "posts": [
        {
            "id": f"post_{i}",
            "title": fake.sentence(),
            "category_id": random.randint(1, 10),
            "likes": random.randint(0, 1000),
            "views": random.randint(0, 5000),
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        } for i in range(1, 501)
    ]
}

@app.get("/posts/view")
async def mock_viewed_posts():
    return JSONResponse({
        "posts": random.sample(mock_db["posts"], 50),
        "resonance_algorithm": "mock_v1"
    })

@app.get("/posts/like")
async def mock_liked_posts():
    return JSONResponse({
        "posts": random.sample(mock_db["posts"], 30),
        "resonance_algorithm": "mock_v1"
    })

@app.get("/users")
async def mock_users():
    return JSONResponse({
        "users": mock_db["users"],
        "page": 1,
        "page_size": 100
    })

# Add similar endpoints for other routes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)