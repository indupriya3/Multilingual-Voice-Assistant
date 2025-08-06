# Multilingual Voice Assistant

A full-stack web application that provides an intelligent voice assistant supporting multiple Indian languages. The application features speech-to-text, natural language processing, intent detection, and text-to-speech capabilities with user authentication and command history.

## Features

### 🎤 Voice Processing
- **Speech-to-Text**: Convert spoken words to text using browser's Web Speech API
- **Text-to-Speech**: Generate natural-sounding speech from text responses
- **Real-time Audio**: Live microphone input with visual feedback
- **Multi-format Support**: Handles various audio formats for processing

### 🌍 Multilingual Support
- **6 Supported Languages**: English, Hindi, Telugu, Tamil, Kannada, Malayalam
- **Auto Language Detection**: Automatically detects the language of spoken input
- **Cross-language Translation**: Translate responses between supported languages
- **Native Language Processing**: Intent detection works across all supported languages

### 🧠 AI & NLP Features
- **Intent Detection**: Understands user commands (time, jokes, greetings, translation requests)
- **Smart Responses**: Context-aware responses based on detected intent
- **Translation Service**: Powered by Google Translate for accurate multilingual translation
- **Natural Language Understanding**: Processes casual, conversational speech patterns

### 🔐 User Management
- **Secure Authentication**: JWT-based login and registration system
- **Password Security**: BCrypt password hashing for secure storage
- **Protected Routes**: All voice features require user authentication
- **Session Management**: Persistent login sessions with automatic token validation

### 📊 Command History & Analytics
- **Command Tracking**: Saves all voice interactions with timestamps
- **Intent Analytics**: Tracks most used command types
- **Language Usage**: Monitors language preferences and usage patterns
- **Response History**: Complete log of assistant responses and translations

### 💻 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark Theme**: Professional dark interface with gradient backgrounds
- **Real-time Feedback**: Visual indicators for listening, processing, and response states
- **Accessibility**: Keyboard navigation, screen reader support, and high contrast
- **Professional Polish**: Glass morphism effects, smooth animations, and modern typography

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **MongoDB**: NoSQL database for user data and command history
- **JWT**: JSON Web Tokens for secure authentication
- **Speech Recognition**: Python library for speech-to-text processing
- **gTTS**: Google Text-to-Speech for multilingual voice synthesis
- **googletrans**: Translation service for multilingual support
- **NLTK/spaCy**: Natural language processing for intent detection
- **BCrypt**: Password hashing for security
- **Motor**: Async MongoDB driver for FastAPI

### Frontend
- **React.js**: Modern JavaScript library for building user interfaces
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Shadcn/ui**: High-quality React components with consistent design
- **Axios**: HTTP client for API communication
- **React Router**: Client-side routing for single-page application
- **Web Speech API**: Browser-native speech recognition
- **Speech Synthesis API**: Browser-native text-to-speech

### Development Tools
- **Python**: Backend development language
- **Node.js**: Frontend development environment
- **Yarn**: Package manager for frontend dependencies
- **Supervisor**: Process management for production deployment

## Installation & Setup

### Prerequisites
- Python 3.8+ installed on your system
- Node.js 16+ and Yarn package manager
- MongoDB running locally on port 27017
- Modern web browser with microphone access

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend/
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start MongoDB service**:
   ```bash
   # On macOS with Homebrew:
   brew services start mongodb-community
   
   # On Ubuntu/Linux:
   sudo systemctl start mongod
   
   # On Windows:
   net start MongoDB
   ```

5. **Run the FastAPI backend**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

The backend API will be available at `http://localhost:8001`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend/
   ```

2. **Install Node.js dependencies**:
   ```bash
   yarn install
   ```

3. **Configure environment variables**:
   Create or update `.env` file with your backend URL:
   ```
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

4. **Start the React development server**:
   ```bash
   yarn start
   ```

The frontend application will be available at `http://localhost:3000`

## Usage Guide

### Getting Started

1. **Create Account**:
   - Open the application in your web browser
   - Click "Need an account? Sign up" 
   - Enter username, email, and secure password
   - Click "Sign Up" to create your account

2. **Login**:
   - Use your registered email and password
   - Click "Sign In" to access the dashboard

### Using the Voice Assistant

1. **Select Output Language**:
   - Choose your preferred response language from the dropdown
   - Supports: English, Hindi, Telugu, Tamil, Kannada, Malayalam

2. **Voice Interaction**:
   - Click the large microphone button to start listening
   - Speak clearly into your microphone
   - The assistant will automatically process your speech
   - View the transcribed text and AI response

3. **Available Commands**:
   - **"What time is it?"** - Get current time
   - **"Tell me a joke"** - Hear a random joke
   - **"Hello" / "Hi"** - General greeting
   - **"Translate [text]"** - Translation requests
   - **General questions** - Conversational responses

4. **Translation Feature**:
   - After speaking, click "Translate to [Language]"
   - Get instant translation in your selected language
   - Hear the translated response spoken aloud

### Command History

- View all your past voice interactions in the history panel
- See detected intents, timestamps, and language information
- Track your usage patterns and frequently used commands

### Audio Playback

- Click the "Play" button next to any response to hear it spoken
- Automatic text-to-speech in your selected language
- Adjustable playback using browser controls

## API Documentation

Once the backend is running, visit `http://localhost:8001/docs` to access the interactive API documentation powered by FastAPI's automatic OpenAPI generation.

### Key Endpoints

- `POST /api/register` - User registration
- `POST /api/login` - User authentication
- `POST /api/process-voice` - Process voice commands
- `POST /api/translate` - Text translation
- `GET /api/command-history` - Retrieve user's command history
- `GET /api/supported-languages` - List of supported languages

## Development

### Adding New Languages

1. Update the `SUPPORTED_LANGUAGES` dictionary in both backend and frontend
2. Ensure the language code is supported by Google Translate
3. Add appropriate language-specific keywords for intent detection
4. Test speech recognition and synthesis for the new language

### Extending Intent Detection

1. Add new intent patterns in the `detect_intent()` function
2. Create corresponding response generators in `generate_response()`
3. Update the UI to handle new intent types
4. Add appropriate keywords in multiple languages

### Customizing Responses

- Modify the `generate_response()` function in `server.py`
- Add context-aware responses based on user history
- Integrate with external APIs for dynamic content
- Implement personality traits for more engaging interactions

### Database Schema

The application uses MongoDB with the following collections:

- **users**: User authentication and profile data
- **voice_commands**: Command history with full conversation context

## Contributing

This project is designed as a portfolio showcase demonstrating full-stack development skills with AI/NLP integration. The codebase follows modern development practices:

- RESTful API design with FastAPI
- Component-based React architecture  
- Responsive design with Tailwind CSS
- Secure authentication with JWT
- Async/await patterns for performance
- Error handling and user feedback
- Professional code organization

## License

This project is created for educational and portfolio purposes. Feel free to use the code as a reference for learning full-stack development with AI integration.

## Troubleshooting

### Common Issues

1. **Microphone not working**: 
   - Ensure browser permissions for microphone access
   - Check if HTTPS is enabled (required for some browsers)
   - Verify microphone is working in system settings

2. **Backend connection errors**:
   - Verify MongoDB is running on port 27017
   - Check if backend server is running on port 8001
   - Ensure frontend .env has correct REACT_APP_BACKEND_URL

3. **Speech recognition not working**:
   - Use Chrome or Edge browsers (best Web Speech API support)
   - Ensure stable internet connection
   - Speak clearly and avoid background noise

4. **Translation errors**:
   - Check internet connection (required for Google Translate)
   - Verify the target language is in the supported list
   - Ensure the text is not empty or too long

### Performance Tips

- Clear command history periodically for better performance
- Use a good quality microphone for better speech recognition
- Ensure stable internet connection for translation features
- Close unnecessary browser tabs while using the voice assistant

For additional support or to report bugs, please check the browser console for error messages and ensure all dependencies are correctly installed.