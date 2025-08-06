import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";
import { Mic, MicOff, Play, Pause, Volume2, User, LogOut, History, Loader } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Supported languages
const SUPPORTED_LANGUAGES = {
  'en': 'English',
  'hi': 'Hindi',
  'te': 'Telugu',
  'ta': 'Tamil',
  'kn': 'Kannada',
  'ml': 'Malayalam'
};

// Authentication Context
const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Validate token by calling protected route
      axios.get(`${API}/protected`)
        .then(response => {
          setUser({ authenticated: true });
        })
        .catch(error => {
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
          delete axios.defaults.headers.common['Authorization'];
        });
    }
  }, [token]);

  const login = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    setUser({ authenticated: true });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return { user, login, logout, token };
};

// Login Component
const Login = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const response = await axios.post(`${API}/login`, {
          email: formData.email,
          password: formData.password
        });
        onLogin(response.data.access_token);
        toast.success("Login successful!");
      } else {
        await axios.post(`${API}/register`, formData);
        toast.success("Registration successful! Please login.");
        setIsLogin(true);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-4">
            <Volume2 className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Voice Assistant</h1>
          <p className="text-gray-400">Multilingual AI-powered voice assistant</p>
        </div>

        <Card className="backdrop-blur-sm bg-white/10 border-white/20">
          <CardHeader>
            <CardTitle className="text-white">
              {isLogin ? "Welcome Back" : "Create Account"}
            </CardTitle>
            <CardDescription className="text-gray-300">
              {isLogin ? "Sign in to your account" : "Register for a new account"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div>
                  <Input
                    type="text"
                    placeholder="Username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    required
                    className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  />
                </div>
              )}
              <div>
                <Input
                  type="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                />
              </div>
              <div>
                <Input
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                />
              </div>
              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                disabled={loading}
              >
                {loading && <Loader className="mr-2 h-4 w-4 animate-spin" />}
                {isLogin ? "Sign In" : "Sign Up"}
              </Button>
            </form>
            <div className="mt-4 text-center">
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="text-blue-400 hover:text-blue-300 underline"
              >
                {isLogin ? "Need an account? Sign up" : "Already have an account? Sign in"}
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Voice Assistant Dashboard
const Dashboard = ({ onLogout }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const [responseText, setResponseText] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [commandHistory, setCommandHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';
      
      rec.onstart = () => {
        setIsListening(true);
      };
      
      rec.onend = () => {
        setIsListening(false);
      };
      
      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setTranscribedText(transcript);
        processVoiceCommand(transcript, 'en');
      };
      
      rec.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        toast.error('Speech recognition error: ' + event.error);
        setIsListening(false);
      };
      
      setRecognition(rec);
    } else {
      toast.error('Speech recognition not supported in this browser');
    }

    loadCommandHistory();
  }, []);

  const loadCommandHistory = async () => {
    try {
      const response = await axios.get(`${API}/command-history`);
      setCommandHistory(response.data);
    } catch (error) {
      console.error('Failed to load command history:', error);
    }
  };

  const startListening = () => {
    if (recognition && !isListening) {
      setTranscribedText('');
      setResponseText('');
      recognition.start();
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  const processVoiceCommand = async (text, detectedLanguage) => {
    setIsProcessing(true);
    try {
      const response = await axios.post(`${API}/process-voice`, null, {
        params: {
          transcribed_text: text,
          detected_language: detectedLanguage,
          target_language: selectedLanguage
        }
      });
      
      setResponseText(response.data.response_text);
      
      // Text-to-speech for response
      if (response.data.response_text) {
        speakText(response.data.response_text, selectedLanguage);
      }
      
      loadCommandHistory();
      toast.success('Voice command processed!');
    } catch (error) {
      console.error('Voice processing failed:', error);
      toast.error('Failed to process voice command');
    } finally {
      setIsProcessing(false);
    }
  };

  const speakText = (text, language) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === 'en' ? 'en-US' : `${language}-IN`;
      speechSynthesis.speak(utterance);
    }
  };

  const translateText = async () => {
    if (!transcribedText) {
      toast.error('Please speak something first');
      return;
    }

    try {
      const response = await axios.post(`${API}/translate`, {
        text: transcribedText,
        target_language: selectedLanguage
      });
      
      setResponseText(response.data.translated_text);
      speakText(response.data.translated_text, selectedLanguage);
      toast.success('Translation completed!');
    } catch (error) {
      console.error('Translation failed:', error);
      toast.error('Translation failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Volume2 className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-xl font-bold text-white">Voice Assistant</h1>
            </div>
            <Button
              onClick={onLogout}
              variant="outline"
              className="border-white/20 text-white hover:bg-white/10"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Voice Interface */}
          <div className="lg:col-span-2">
            <Card className="backdrop-blur-sm bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Mic className="h-5 w-5" />
                  <span>Voice Interface</span>
                </CardTitle>
                <CardDescription className="text-gray-300">
                  Click the microphone to start speaking in any supported language
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Language Selection */}
                <div className="flex items-center space-x-4">
                  <label className="text-white font-medium">Output Language:</label>
                  <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                    <SelectTrigger className="w-48 bg-white/10 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-white/20">
                      {Object.entries(SUPPORTED_LANGUAGES).map(([code, name]) => (
                        <SelectItem key={code} value={code} className="text-white focus:bg-white/10">
                          {name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Microphone Button */}
                <div className="flex justify-center">
                  <Button
                    onClick={isListening ? stopListening : startListening}
                    size="lg"
                    className={`w-24 h-24 rounded-full ${
                      isListening 
                        ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                        : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
                    }`}
                    disabled={isProcessing}
                  >
                    {isProcessing ? (
                      <Loader className="h-8 w-8 animate-spin" />
                    ) : isListening ? (
                      <MicOff className="h-8 w-8" />
                    ) : (
                      <Mic className="h-8 w-8" />
                    )}
                  </Button>
                </div>

                {/* Status */}
                <div className="text-center">
                  <Badge 
                    variant={isListening ? "destructive" : isProcessing ? "secondary" : "default"}
                    className="px-4 py-2"
                  >
                    {isProcessing ? "Processing..." : isListening ? "Listening..." : "Ready to listen"}
                  </Badge>
                </div>

                {/* Transcribed Text */}
                {transcribedText && (
                  <div className="space-y-2">
                    <label className="text-white font-medium">You said:</label>
                    <div className="p-4 bg-black/30 rounded-lg border border-white/10">
                      <p className="text-white">{transcribedText}</p>
                    </div>
                  </div>
                )}

                {/* Response Text */}
                {responseText && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-white font-medium">Assistant Response:</label>
                      <Button
                        onClick={() => speakText(responseText, selectedLanguage)}
                        size="sm"
                        variant="outline"
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Play className="mr-2 h-4 w-4" />
                        Play
                      </Button>
                    </div>
                    <div className="p-4 bg-green-900/30 rounded-lg border border-green-500/20">
                      <p className="text-white">{responseText}</p>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex space-x-4">
                  <Button
                    onClick={translateText}
                    disabled={!transcribedText || isProcessing}
                    className="flex-1"
                    variant="outline"
                  >
                    Translate to {SUPPORTED_LANGUAGES[selectedLanguage]}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Command History */}
          <div>
            <Card className="backdrop-blur-sm bg-white/10 border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <History className="h-5 w-5" />
                  <span>Command History</span>
                </CardTitle>
                <CardDescription className="text-gray-300">
                  Your recent voice commands and responses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {commandHistory.length > 0 ? (
                    commandHistory.map((command) => (
                      <div key={command.id} className="p-3 bg-black/30 rounded-lg border border-white/10">
                        <div className="flex items-center justify-between mb-2">
                          <Badge variant="secondary" className="text-xs">
                            {command.intent}
                          </Badge>
                          <span className="text-xs text-gray-400">
                            {new Date(command.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-300 mb-1">
                          <strong>You:</strong> {command.transcribed_text}
                        </p>
                        <p className="text-sm text-white">
                          <strong>Assistant:</strong> {command.response_text}
                        </p>
                        <div className="flex items-center mt-2 space-x-2">
                          <Badge variant="outline" className="text-xs">
                            {SUPPORTED_LANGUAGES[command.detected_language] || command.detected_language}
                          </Badge>
                          <span className="text-xs text-gray-400">→</span>
                          <Badge variant="outline" className="text-xs">
                            {SUPPORTED_LANGUAGES[command.target_language] || command.target_language}
                          </Badge>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-400 text-center py-4">
                      No commands yet. Start speaking to see your history!
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const { user, login, logout } = useAuth();

  return (
    <div className="App">
      <BrowserRouter>
        <Toaster position="top-right" />
        <Routes>
          <Route 
            path="/" 
            element={
              user ? (
                <Dashboard onLogout={logout} />
              ) : (
                <Login onLogin={login} />
              )
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;