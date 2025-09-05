# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import base64

def get_page_content(url: str):
    """
    Fetches and parses the content of a web page.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Simple heuristic to extract main text (you can make this more robust)
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        
        # Get all image URLs, handling both 'src' and 'data-src' attributes
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and src.startswith(('http', 'https')):
                images.append(src)

        return {"text": text, "images": images}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch content from URL: {e}"}

def download_and_base64_image(image_url: str):
    """
    Downloads an image and encodes it in Base64.
    """
    try:
        response = requests.get(image_url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except (requests.RequestException, IOError) as e:
        return None # Return None if image download or processing fails


from transformers import pipeline

# Load models from Hugging Face.
# We will use "distilbert-base-uncased-finetuned-sst-2-english" for text classification.
# We will use "sshleifer/distilbart-cnn-12-6" for text summarization.
# We will use "Salesforce/blip-vqa-base" for Visual Question Answering.
# We will use "openai/clip-vit-base-patch32" for Zero-Shot Image Classification.

try:
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    vqa_pipeline = pipeline("visual-question-answering", model="Salesforce/blip-vqa-base")
    clip_classifier = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")
    
except Exception as e:
    print(f"Error loading models: {e}")
    # You might want to handle this more gracefully in a production environment
    classifier = None
    summarizer = None
    vqa_pipeline = None
    clip_classifier = None

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

from pydantic import BaseModel

class URLPayload(BaseModel):
    url: str

@app.post("/analyze_url")
async def analyze_url(payload: URLPayload):
    url = payload.url
    
    # Step 1: Get content from the URL
    content = get_page_content(url)
    
    if "error" in content:
        return {"error": content["error"]}
        
    text = content.get("text", "")
    images = content.get("images", [])

    analysis_results = {
        "text_summary": None,
        "text_sentiment": None,
        "image_analysis": []
    }

    # Step 2: Analyze the text
    if text and summarizer:
        summary_result = summarizer(text, max_length=150, min_length=50, do_sample=False)
        analysis_results["text_summary"] = summary_result[0]['summary_text']
        
    if text and classifier:
        sentiment_result = classifier(text)
        analysis_results["text_sentiment"] = sentiment_result[0]
        
    # Step 3: Analyze the images
    if images and vqa_pipeline and clip_classifier:
        
        # We'll analyze only the first image for this demo to save time and resources
        first_image_url = images[0]
        try:
            image_data = requests.get(first_image_url, stream=True).raw
            
            # Perform Visual Question Answering
            vqa_question = "What is in this image?"
            vqa_answer = vqa_pipeline(image=image_data, question=vqa_question)
            
            # Perform Zero-Shot Image Classification
            candidate_labels = ["photograph", "AI-generated image", "drawing", "screenshot"]
            classification_result = clip_classifier(image=image_data, candidate_labels=candidate_labels)
            
            # Encode image for display on the frontend
            base64_img = download_and_base64_image(first_image_url)

            analysis_results["image_analysis"] = [{
                "url": first_image_url,
                "base64_image": base64_img,
                "vqa_answer": vqa_answer[0]['answer'] if vqa_answer else "N/A",
                "zero_shot_classification": classification_result
            }]

        except Exception as e:
            analysis_results["image_analysis"] = [{"error": f"Failed to analyze image: {e}"}]

    return analysis_results

@app.get("/")
def read_root():
    return {"message": "VeriMedia Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}



@app.post("/analyze_url")
async def analyze_url(payload: URLPayload):
    url = payload.url
    content = get_page_content(url)
    
    if "error" in content:
        return {"error": content["error"]}
        
    text = content.get("text", "")
    images = content.get("images", [])

    analysis_results = {
        "text_summary": None,
        "text_sentiment": None,
        "image_analysis": []
    }

    # Step 2: Analyze the text
    # ... (text analysis code, no changes needed here)
        
    # Step 3: Analyze the images
    if images and vqa_pipeline and clip_classifier:
        first_image_url = images[0]
        try:
            # Download the image data
            image_response = requests.get(first_image_url)
            image_response.raise_for_status()

            # Create a BytesIO object from the image content
            image_stream = BytesIO(image_response.content)
            
            # Open the image with Pillow
            pil_image = Image.open(image_stream).convert("RGB") # Convert to RGB to handle various formats

            # Perform Visual Question Answering
            vqa_question = "What is in this image?"
            vqa_answer = vqa_pipeline(image=pil_image, question=vqa_question)
            
            # Perform Zero-Shot Image Classification
            candidate_labels = ["photograph", "AI-generated image", "drawing", "screenshot"]
            classification_result = clip_classifier(image=pil_image, candidate_labels=candidate_labels)
            
            # Encode image for display on the frontend
            base64_img = download_and_base64_image(first_image_url)

            analysis_results["image_analysis"] = [{
                "url": first_image_url,
                "base64_image": base64_img,
                "vqa_answer": vqa_answer[0]['answer'] if vqa_answer else "N/A",
                "zero_shot_classification": classification_result
            }]

        except Exception as e:
            analysis_results["image_analysis"] = [{"error": f"Failed to analyze image: {e}"}]

    return analysis_results