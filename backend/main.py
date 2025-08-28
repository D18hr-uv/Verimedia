# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# We will need this to allow our React frontend to communicate with the FastAPI backend.
# Replace "http://localhost:3000" with your frontend's URL when you set it up.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "VeriMedia Backend is running!"}

# You can also add an endpoint for a simple health check
@app.get("/health")
def health_check():
    return {"status": "ok"}