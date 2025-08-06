from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import io
import speech_recognition as sr
from gtts import gTTS
import tempfile
import json
import re
from googletrans import Translator, LANGUAGES
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
import random


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security setup
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Download NLTK data (only needed once)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Initialize translator
translator = Translator()

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Create the main app without a prefix
app = FastAPI(title="Multilingual Voice Assistant", description="A voice assistant supporting multiple Indian languages")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class VoiceCommand(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    transcribed_text: str
    detected_language: str
    intent: str
    response_text: str
    target_language: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class VoiceResponse(BaseModel):
    transcribed_text: str
    detected_language: str
    intent: str
    response_text: str
    target_language: str
    audio_url: Optional[str] = None

class TranslationRequest(BaseModel):
    text: str
    target_language: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

def detect_intent(text):
    """Simple intent detection based on keywords"""
    text = text.lower()
    
    # Time-related intents
    time_keywords = ['time', 'clock', 'what time', 'current time', 'samay', 'waqt', 'కాలం', 'நேரம்', 'സമയം']
    if any(keyword in text for keyword in time_keywords):
        return 'time'
    
    # Joke intents
    joke_keywords = ['joke', 'funny', 'humor', 'laugh', 'हंसी', 'मज़ाक', 'హాస్యం', 'நகைச்சுवை', 'തമാശ']
    if any(keyword in text for keyword in joke_keywords):
        return 'joke'
    
    # Greeting intents
    greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good evening', 'namaste', 'नमस्ते', 'वणक्कम्', 'നമസ്കാരം']
    if any(keyword in text for keyword in greeting_keywords):
        return 'greeting'
    
    # Translation intents
    translate_keywords = ['translate', 'convert', 'meaning', 'अनुवाद', 'மொழிபெயர्पு', 'অনুবাদ', 'అనువాదం']
    if any(keyword in text for keyword in translate_keywords):
        return 'translate'
    
    return 'general'

def generate_response(intent, detected_language='en'):
    """Generate appropriate response based on intent"""
    
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!",
        "Why did the math book look so sad? Because it had too many problems!"
    ]
    
    responses = {
        'time': f"The current time is {datetime.now().strftime('%I:%M %p')}",
        'joke': random.choice(jokes),
        'greeting': "Hello! I'm your multilingual voice assistant. How can I help you today?",
        'translate': "Please provide the text you want me to translate.",
        'general': "I understand you're asking something. Could you please be more specific about what you need help with?"
    }
    
    return responses.get(intent, responses['general'])

# Language mapping for translation
SUPPORTED_LANGUAGES = {
    'en': 'english',
    'hi': 'hindi', 
    'te': 'telugu',
    'ta': 'tamil',
    'kn': 'kannada',
    'ml': 'malayalam'
}

# Authentication routes
@api_router.post("/register", response_model=dict)
async def register(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    existing_username = await db.users.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_obj = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    await db.users.insert_one(user_obj.dict())
    
    return {"message": "User registered successfully"}

@api_router.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Voice processing routes
@api_router.post("/speech-to-text", response_model=dict)
async def speech_to_text(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    try:
        # Read the uploaded audio file
        audio_data = await file.read()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_filename = temp_file.name
        
        try:
            # Use speech recognition
            with sr.AudioFile(temp_filename) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
            
            # Detect language
            detected = translator.detect(text)
            detected_language = detected.lang if detected.lang in SUPPORTED_LANGUAGES else 'en'
            
            # Clean up temp file
            os.unlink(temp_filename)
            
            return {
                "transcribed_text": text,
                "detected_language": detected_language,
                "confidence": getattr(detected, 'confidence', 0.5)
            }
        
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise HTTPException(status_code=400, detail=f"Speech recognition failed: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing audio: {str(e)}")

@api_router.post("/text-to-speech")
async def text_to_speech(text: str, language: str = "en", current_user: User = Depends(get_current_user)):
    try:
        # Create TTS
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            
            # Read the file and return as bytes
            with open(temp_file.name, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Clean up
            os.unlink(temp_file.name)
            
        return {"audio_data": audio_data.hex(), "message": "TTS conversion successful"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"TTS conversion failed: {str(e)}")

@api_router.post("/process-voice", response_model=VoiceResponse)
async def process_voice(
    transcribed_text: str,
    detected_language: str,
    target_language: str = "en",
    current_user: User = Depends(get_current_user)
):
    try:
        # Detect intent
        intent = detect_intent(transcribed_text)
        
        # Generate response based on intent
        response_text = generate_response(intent, detected_language)
        
        # If translation is requested or target language is different, translate
        if target_language != detected_language:
            translated = translator.translate(response_text, dest=target_language)
            response_text = translated.text
        
        # Save command history
        command = VoiceCommand(
            user_id=current_user.id,
            transcribed_text=transcribed_text,
            detected_language=detected_language,
            intent=intent,
            response_text=response_text,
            target_language=target_language
        )
        
        await db.voice_commands.insert_one(command.dict())
        
        return VoiceResponse(
            transcribed_text=transcribed_text,
            detected_language=detected_language,
            intent=intent,
            response_text=response_text,
            target_language=target_language
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Voice processing failed: {str(e)}")

@api_router.post("/translate", response_model=dict)
async def translate_text(request: TranslationRequest, current_user: User = Depends(get_current_user)):
    try:
        translated = translator.translate(request.text, dest=request.target_language)
        return {
            "original_text": request.text,
            "translated_text": translated.text,
            "source_language": translated.src,
            "target_language": request.target_language
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Translation failed: {str(e)}")

@api_router.get("/command-history", response_model=List[VoiceCommand])
async def get_command_history(current_user: User = Depends(get_current_user)):
    commands = await db.voice_commands.find(
        {"user_id": current_user.id}
    ).sort("timestamp", -1).limit(50).to_list(50)
    
    return [VoiceCommand(**cmd) for cmd in commands]

@api_router.get("/supported-languages")
async def get_supported_languages():
    return {
        "languages": SUPPORTED_LANGUAGES,
        "message": "Supported languages for voice assistant"
    }

# Test routes
@api_router.get("/")
async def root():
    return {"message": "Multilingual Voice Assistant API"}

@api_router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}! This is a protected route."}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()