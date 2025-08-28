# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# We will need this to allow our React frontend to communicate with the FastAPI backend.
# The URL for your React app is http://localhost:5173
origins = [
    "http://localhost:5173", # Correct URL for Vite's dev server
    "http://127.0.0.1:5173", # A good practice is to include this as well
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

@app.get("/health")
def health_check():
    return {"status": "ok"}