pimport streamlit as st
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import requests
import json
import sqlite3
import os
import re
import threading
import tempfile
from gtts import gTTS
import base64
from streamlit.components.v1 import html
import time

class VoiceAssistant:
    def __init__(self):
        # Initialize session state
        self.init_session_state()
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Setup database
        self.setup_database()
        
        # Calibrate microphone
        self.calibrate_microphone()
    
    def init_session_state(self):
        """Initialize all session state variables"""
        defaults = {
            'is_listening': False,
            'conversation': [],
            'user_preferences': {
                'name': 'User',
                'city': 'London',
                'voice_enabled': True,
                'theme': 'dark',
                'assistant_name': 'Alexa'
            },
            'assistant_busy': False,
            'audio_playing': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.add_to_conversation("system", "Microphone calibrated successfully! 🎤")
        except Exception as e:
            self.add_to_conversation("system", f"Microphone setup: {str(e)}")
    
    def listen_once(self):
        """Listen for a single voice command"""
        try:
            with self.microphone as source:
                st.session_state.assistant_busy = True
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
            
            command = self.recognizer.recognize_google(audio)
            st.session_state.assistant_busy = False
            return command
            
        except sr.WaitTimeoutError:
            st.session_state.assistant_busy = False
            return None
        except sr.UnknownValueError:
            st.session_state.assistant_busy = False
            return "❌ I didn't understand that. Please try again."
        except sr.RequestError as e:
            st.session_state.assistant_busy = False
            return f"❌ Speech recognition error: {str(e)}"
        except Exception as e:
            st.session_state.assistant_busy = False
            return f"❌ Unexpected error: {str(e)}"
    
    def process_command(self, command):
        """Process a voice command and return a response"""
        if not command or command.startswith("❌"):
            return command
        
        command_lower = command.lower().strip()
        
        # Greetings
        if any(greeting in command_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            return self.respond_to_greeting()
        
        # Time and Date
        elif "time" in command_lower:
            return self.get_current_time()
        elif "date" in command_lower:
            return self.get_current_date()
        elif "day" in command_lower:
            return self.get_current_day()
        
        # Web Search
        elif any(keyword in command_lower for keyword in ["search", "google", "find"]):
            return self.search_web(command)
        
        # Weather
        elif "weather" in command_lower:
            return self.get_weather()
        
        # Reminders
        elif any(keyword in command_lower for keyword in ["remind", "reminder"]):
            return self.set_reminder(command)
        
        # Entertainment
        elif "joke" in command_lower:
            return self.tell_joke()
        elif "quote" in command_lower:
            return self.get_inspirational_quote()
        
        # Calculations
        elif any(keyword in command_lower for keyword in ["calculate", "what is"]) and any(op in command_lower for op in ["+", "-", "*", "/"]):
            return self.calculate(command)
        
        # Navigation
        elif any(keyword in command_lower for keyword in ["open", "launch"]):
            return self.open_website(command)
        
        # System
        elif any(keyword in command_lower for keyword in ["exit", "quit", "goodbye", "bye"]):
            return self.exit_assistant()
        
        # Personal
        elif "your name" in command_lower:
            return f"My name is {st.session_state.user_preferences['assistant_name']}! 😊"
        elif "who are you" in command_lower:
            return "I'm your personal voice assistant! I can help with tasks, information, and much more! 🌟"
        
        else:
            return self.get_general_response(command)
    
    def respond_to_greeting(self):
        """Respond to greetings"""
        greetings = [
            f"Hello {st.session_state.user_preferences['name']}! How can I assist you today? 🌟",
            f"Hi there {st.session_state.user_preferences['name']}! What can I do for you? 😊",
            f"Greetings {st.session_state.user_preferences['name']}! I'm here and ready to help! 🚀",
            f"Hey {st.session_state.user_preferences['name']}! Great to see you! What's on your mind? 💫"
        ]
        import random
        return random.choice(greetings)
    
    def get_current_time(self):
        """Get current time"""
        now = datetime.datetime.now()
        return f"🕒 The current time is {now.strftime('%I:%M %p')}"
    
    def get_current_date(self):
        """Get current date"""
        now = datetime.datetime.now()
        return f"📅 Today's date is {now.strftime('%A, %B %d, %Y')}"
    
    def get_current_day(self):
        """Get current day"""
        now = datetime.datetime.now()
        return f"📆 Today is {now.strftime('%A')}"
    
    def search_web(self, command):
        """Search the web based on the command"""
        query = re.sub(r'(search|google|find|for)', '', command, flags=re.IGNORECASE).strip()
        if not query:
            return "🔍 What would you like me to search for?"
        
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"🔍 Searching the web for: **{query}**"
    
    def get_weather(self):
        """Get weather information"""
        city = st.session_state.user_preferences.get('city', 'London')
        
        # Simulated weather response (in real app, use OpenWeatherMap API)
        weather_conditions = ["☀️ sunny", "⛅ partly cloudy", "🌧️ rainy", "⛈️ stormy", "❄️ snowy", "🌫️ foggy"]
        temperatures = [22, 18, 25, 16, 20, 19]
        import random
        
        condition = random.choice(weather_conditions)
        temp = random.choice(temperatures)
        
        return f"🌤️ The weather in **{city}** is {condition} with a temperature of **{temp}°C**. Perfect day to be productive! 💪"
    
    def set_reminder(self, command):
        """Set a reminder based on voice command"""
        reminder_text = re.sub(r'(remind|reminder|me to|set|a|an)', '', command, flags=re.IGNORECASE).strip()
        
        if not reminder_text:
            return "⏰ What would you like me to remind you about?"
        
        self.save_reminder(reminder_text)
        return f"✅ Reminder set: **{reminder_text}**\n\nI'll make sure you don't forget! 🐘"
    
    def tell_joke(self):
        """Tell a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 🤓",
            "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
            "Why don't skeletons fight each other? They don't have the guts! 💀",
            "What do you call a fake noodle? An impasta! 🍝",
            "Why did the math book look so sad? Because it had too many problems! 📚",
            "What do you call a sleeping bull? A bulldozer! 🐮"
        ]
        import random
        return f"😄 {random.choice(jokes)}"
    
    def get_inspirational_quote(self):
        """Get an inspirational quote"""
        quotes = [
            "The only way to do great work is to love what you do. - Steve Jobs 💼",
            "Innovation distinguishes between a leader and a follower. - Steve Jobs 🚀",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt ✨",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill 🏆",
            "The way to get started is to quit talking and begin doing. - Walt Disney 🎯"
        ]
        import random
        return f"💫 {random.choice(quotes)}"
    
    def calculate(self, command):
        """Perform basic calculations"""
        try:
            expression = re.sub(r'(calculate|what is|please)', '', command, flags=re.IGNORECASE).strip()
            
            if not re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expression):
                return "❌ I can only perform basic math with numbers and +, -, *, / operators"
            
            result = eval(expression)
            return f"🧮 **{expression} = {result}**\n\nMath is fun! 🤓"
        
        except Exception as e:
            return "❌ Sorry, I couldn't calculate that. Please try a simpler expression."
    
    def open_website(self, command):
        """Open websites based on command"""
        sites = {
            'youtube': 'https://youtube.com',
            'facebook': 'https://facebook.com',
            'twitter': 'https://twitter.com',
            'linkedin': 'https://linkedin.com',
            'github': 'https://github.com',
            'gmail': 'https://gmail.com'
        }
        
        for site, url in sites.items():
            if site in command.lower():
                webbrowser.open(url)
                return f"🌐 Opening **{site.capitalize()}** for you!"
        
        return "❌ I can open: YouTube, Facebook, Twitter, LinkedIn, GitHub, or Gmail. Just ask!"
    
    def exit_assistant(self):
        """Handle exit command"""
        return "👋 Goodbye! It was great helping you today. Come back anytime! 🌟"
    
    def get_general_response(self, command):
        """Respond to general questions"""
        responses = [
            f"🤔 I'm not sure about \"{command}\". Try asking about time, weather, calculations, or web searches!",
            f"💡 That's interesting! I'm better with practical tasks like reminders, calculations, or web searches.",
            f"🎯 I'm still learning! For now, I can help with time, weather, jokes, calculations, and web searches.",
            f"🌟 Great question! I specialize in practical tasks. Try: \"What's the time?\", \"Tell me a joke\", or \"Search for...\""
        ]
        import random
        return random.choice(responses)
    
    def speak(self, text):
        """Convert text to speech using gTTS"""
        try:
            # Clean text for speech (remove emojis and markdown)
            clean_text = re.sub(r'[^\w\s.,!?]', '', text)
            tts = gTTS(text=clean_text, lang='en', slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                return fp.name
        except Exception as e:
            self.add_to_conversation("system", f"❌ TTS Error: {str(e)}")
            return None
    
    def add_to_conversation(self, speaker, text):
        """Add message to conversation history"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.conversation.append({
            'speaker': speaker,
            'text': text,
            'timestamp': timestamp
        })
    
    def setup_database(self):
        """Setup SQLite database for reminders"""
        try:
            self.conn = sqlite3.connect("assistant_v2.db", check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            self.add_to_conversation("system", f"❌ Database error: {str(e)}")
    
    def save_reminder(self, reminder_text):
        """Save reminder to database"""
        try:
            self.cursor.execute("INSERT INTO reminders (text) VALUES (?)", (reminder_text,))
            self.conn.commit()
        except Exception as e:
            self.add_to_conversation("system", f"❌ Error saving reminder: {str(e)}")
    
    def get_reminders(self):
        """Get all reminders from database"""
        try:
            self.cursor.execute("SELECT text, created_at FROM reminders ORDER BY created_at DESC LIMIT 5")
            return self.cursor.fetchall()
        except Exception as e:
            return []

def autoplay_audio(file_path):
    """Auto-play audio file"""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="🎤 NeoVoice Assistant",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize assistant
    assistant = VoiceAssistant()
    
    # Custom CSS for modern styling
    st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat bubbles */
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 25px 25px 5px 25px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .assistant-bubble {
        background: rgba(255, 255, 255, 0.95);
        color: #333;
        padding: 15px 20px;
        border-radius: 25px 25px 25px 5px;
        margin: 10px 0;
        max-width: 80%;
        margin-right: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    .system-bubble {
        background: rgba(255, 193, 7, 0.2);
        color: #856404;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 60%;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
        font-size: 0.9em;
    }
    
    /* Header styling */
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Listening animation */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .listening {
        animation: pulse 1s infinite;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='main-header'>
            <h1 style='text-align: center; color: white; margin: 0;'>🎤 NeoVoice Assistant</h1>
            <p style='text-align: center; color: rgba(255,255,255,0.8); margin: 0;'>Your AI-powered voice companion</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Voice Control Section
        st.markdown("### 🎤 Voice Control Center")
        
        # Voice status and controls
        col1a, col1b, col1c = st.columns(3)
        
        with col1a:
            if st.button("🎤 Start Listening", key="listen", use_container_width=True):
                with st.spinner("🎤 Listening... Speak now!"):
                    command = assistant.listen_once()
                    if command and not command.startswith("❌"):
                        response = assistant.process_command(command)
                        assistant.add_to_conversation("user", command)
                        assistant.add_to_conversation("assistant", response)
                        
                        # Text-to-speech with auto-play
                        if st.session_state.user_preferences.get('voice_enabled', True):
                            audio_file = assistant.speak(response)
                            if audio_file:
                                autoplay_audio(audio_file)
                                os.unlink(audio_file)
                        st.rerun()
        
        with col1b:
            if st.button("🔊 Test Voice", key="test_voice", use_container_width=True):
                test_text = "Hello! I'm your voice assistant. How can I help you today?"
                audio_file = assistant.speak(test_text)
                if audio_file:
                    autoplay_audio(audio_file)
                    os.unlink(audio_file)
        
        with col1c:
            if st.button("🔄 Clear Chat", key="clear", use_container_width=True):
                st.session_state.conversation = []
                st.rerun()
        
        # Manual Input
        st.markdown("### 💬 Type Your Message")
        manual_command = st.text_input("Enter your command:", placeholder="Ask me anything...")
        if st.button("Send Message", use_container_width=True) and manual_command:
            assistant.add_to_conversation("user", manual_command)
            response = assistant.process_command(manual_command)
            assistant.add_to_conversation("assistant", response)
            
            if st.session_state.user_preferences.get('voice_enabled', True):
                audio_file = assistant.speak(response)
                if audio_file:
                    autoplay_audio(audio_file)
                    os.unlink(audio_file)
            st.rerun()
        
        # Conversation History
        st.markdown("### 💭 Conversation History")
        
        if st.session_state.conversation:
            for msg in reversed(st.session_state.conversation[-8:]):
                if msg['speaker'] == 'user':
                    st.markdown(f"""
                    <div class='user-bubble'>
                        <strong>You</strong> • {msg['timestamp']}<br>
                        {msg['text']}
                    </div>
                    """, unsafe_allow_html=True)
                elif msg['speaker'] == 'assistant':
                    st.markdown(f"""
                    <div class='assistant-bubble'>
                        <strong>Assistant</strong> • {msg['timestamp']}<br>
                        {msg['text']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='system-bubble'>
                        {msg['text']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align: center; padding: 40px; color: rgba(255,255,255,0.7);'>
                <h3>🌟 Welcome to NeoVoice Assistant!</h3>
                <p>Start by clicking the microphone button or typing a message below.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Sidebar Content
        st.markdown("### ⚙️ Settings & Tools")
        
        # User Preferences
        with st.expander("👤 Personal Settings", expanded=True):
            name = st.text_input("Your Name", value=st.session_state.user_preferences['name'])
            assistant_name = st.text_input("Assistant Name", value=st.session_state.user_preferences['assistant_name'])
            city = st.text_input("Your City", value=st.session_state.user_preferences['city'])
            voice_enabled = st.checkbox("Enable Voice Responses", value=st.session_state.user_preferences['voice_enabled'])
            
            if st.button("💾 Save Settings"):
                st.session_state.user_preferences.update({
                    'name': name,
                    'assistant_name': assistant_name,
                    'city': city,
                    'voice_enabled': voice_enabled
                })
                st.success("Settings saved!")
        
        # Quick Actions
        with st.expander("🚀 Quick Actions"):
            quick_col1, quick_col2 = st.columns(2)
            
            with quick_col1:
                if st.button("🕒 Time", use_container_width=True):
                    response = assistant.get_current_time()
                    assistant.add_to_conversation("assistant", response)
                    if voice_enabled:
                        audio_file = assistant.speak(response)
                        if audio_file:
                            autoplay_audio(audio_file)
                            os.unlink(audio_file)
                    st.rerun()
                
                if st.button("🌤️ Weather", use_container_width=True):
                    response = assistant.get_weather()
                    assistant.add_to_conversation("assistant", response)
                    if voice_enabled:
                        audio_file = assistant.speak(response)
                        if audio_file:
                            autoplay_audio(audio_file)
                            os.unlink(audio_file)
                    st.rerun()
            
            with quick_col2:
                if st.button("😄 Joke", use_container_width=True):
                    response = assistant.tell_joke()
                    assistant.add_to_conversation("assistant", response)
                    if voice_enabled:
                        audio_file = assistant.speak(response)
                        if audio_file:
                            autoplay_audio(audio_file)
                            os.unlink(audio_file)
                    st.rerun()
                
                if st.button("💫 Quote", use_container_width=True):
                    response = assistant.get_inspirational_quote()
                    assistant.add_to_conversation("assistant", response)
                    if voice_enabled:
                        audio_file = assistant.speak(response)
                        if audio_file:
                            autoplay_audio(audio_file)
                            os.unlink(audio_file)
                    st.rerun()
        
        # Reminders Section
        with st.expander("⏰ Reminders"):
            reminder_text = st.text_input("New Reminder", placeholder="Remember to...")
            if st.button("Add Reminder", use_container_width=True) and reminder_text:
                assistant.save_reminder(reminder_text)
                assistant.add_to_conversation("system", f"✅ Reminder added: {reminder_text}")
                st.rerun()
            
            st.markdown("**Recent Reminders:**")
            reminders = assistant.get_reminders()
            if reminders:
                for reminder in reminders[:3]:
                    st.write(f"• {reminder[0]}")
            else:
                st.write("No reminders yet")
        
        # Voice Commands Help
        with st.expander("📚 Voice Commands"):
            st.markdown("""
            **🎯 Try these commands:**
            - *"Hello"* / *"Hi"* - Greet me
            - *"What time is it?"* - Current time
            - *"What's the weather?"* - Weather info
            - *"Tell me a joke"* - Have a laugh
            - *"Calculate 15 + 27"* - Math helper
            - *"Search for AI news"* - Web search
            - *"Set reminder to call mom"* - Reminders
            - *"Open YouTube"* - Website navigation
            - *"Inspirational quote"* - Motivation
            """)
        
        # Status
        with st.expander("📊 System Status"):
            st.write(f"🔊 Voice: {'Enabled' if voice_enabled else 'Disabled'}")
            st.write(f"🎤 Microphone: Ready")
            st.write(f"💾 Database: Connected")
            st.write(f"👤 User: {st.session_state.user_preferences['name']}")

if __name__ == "__main__":

    main()
