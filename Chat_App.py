import streamlit as st
import sqlite3
import hashlib
import json
import base64
import os
from datetime import datetime
from PIL import Image
import io
import bcrypt
import time
import random
import requests
from streamlit_autorefresh import st_autorefresh
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Page configuration
st.set_page_config(
    page_title="ChatVerse Pro - Connect & Chat",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #FFA62E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .chat-message {
        padding: 12px;
        border-radius: 15px;
        margin: 8px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .chat-message:hover {
        transform: translateX(5px);
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 25%;
        border-bottom-right-radius: 5px;
    }
    .other-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 25%;
        border-bottom-left-radius: 5px;
    }
    .system-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        text-align: center;
        margin: 0 30%;
        font-weight: bold;
    }
    .friend-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #4ECDC4;
        transition: transform 0.3s;
    }
    .friend-card:hover {
        transform: translateY(-5px);
    }
    .user-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 8px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .online-dot {
        height: 12px;
        width: 12px;
        background-color: #00ff00;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    .offline-dot {
        height: 12px;
        width: 12px;
        background-color: #ff4444;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    .stButton button {
        border-radius: 10px;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .notification {
        background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Database setup
def init_database():
    conn = sqlite3.connect('chat_app_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Enhanced Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE,
            avatar TEXT DEFAULT '👤',
            status TEXT DEFAULT 'online',
            bio TEXT DEFAULT 'Hey there! I am using ChatVerse Pro!',
            interests TEXT DEFAULT '',
            location TEXT DEFAULT '',
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_verified BOOLEAN DEFAULT FALSE,
            profile_views INTEGER DEFAULT 0
        )
    ''')
    
    # Enhanced messages table with direct messaging
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            username TEXT NOT NULL,
            target_user TEXT,
            message_type TEXT DEFAULT 'text',
            content TEXT NOT NULL,
            file_data BLOB,
            reply_to INTEGER,
            is_edited BOOLEAN DEFAULT FALSE,
            is_read BOOLEAN DEFAULT FALSE,
            reactions TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Enhanced rooms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_by TEXT NOT NULL,
            is_private BOOLEAN DEFAULT FALSE,
            password TEXT,
            max_users INTEGER DEFAULT 100,
            category TEXT DEFAULT 'general',
            tags TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User sessions for online status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            session_id TEXT NOT NULL,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            room TEXT DEFAULT 'general'
        )
    ''')
    
    # Friends system
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1 TEXT NOT NULL,
            user2 TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1, user2)
        )
    ''')
    
    # Friend requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user TEXT NOT NULL,
            to_user TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            message TEXT DEFAULT '',
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User notifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User interactions (for recommendations)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1 TEXT NOT NULL,
            user2 TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            strength INTEGER DEFAULT 1,
            last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default rooms with categories
    default_rooms = [
        ('general', 'General discussion room', 'system', 'general'),
        ('random', 'Random talks and fun', 'system', 'casual'),
        ('help', 'Get help and support', 'system', 'support'),
        ('tech', 'Technology discussions', 'system', 'technology'),
        ('gaming', 'Video games discussion', 'system', 'gaming'),
        ('music', 'Music lovers unite', 'system', 'music'),
        ('movies', 'Movie enthusiasts', 'system', 'entertainment'),
        ('sports', 'Sports discussion', 'system', 'sports')
    ]
    
    for room_name, description, created_by, category in default_rooms:
        cursor.execute('''
            INSERT OR IGNORE INTO rooms (name, description, created_by, category) VALUES (?, ?, ?, ?)
        ''', (room_name, description, created_by, category))
    
    conn.commit()
    return conn

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username, password, email=None, bio="", interests="", location=""):
    conn = init_database()
    cursor = conn.cursor()
    try:
        avatars = ['👤', '👨', '👩', '🧑', '👨‍💼', '👩‍💼', '👨‍🎓', '👩‍🎓', '🦸', '🦸‍♀️', '🧙', '🧙‍♀️', '👨‍🚀', '👩‍🚀']
        avatar = random.choice(avatars)
        
        cursor.execute(
            "INSERT INTO users (username, password, email, avatar, bio, interests, location) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, hash_password(password), email, avatar, bio, interests, location)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result and verify_password(password, result[0]):
        update_user_session(username)
        return True
    return False

def update_user_session(username, room='general'):
    conn = init_database()
    cursor = conn.cursor()
    session_id = f"{username}_{int(time.time())}"
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_sessions (username, session_id, last_activity, room)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?)
    ''', (username, session_id, room))
    
    cursor.execute('''
        UPDATE users SET status = 'online', last_seen = CURRENT_TIMESTAMP 
        WHERE username = ?
    ''', (username,))
    
    conn.commit()
    conn.close()

def save_message(room, username, message_type, content, file_data=None, reply_to=None, target_user=None):
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (room, username, message_type, content, file_data, reply_to, target_user) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (room, username, message_type, content, file_data, reply_to, target_user)
    )
    message_id = cursor.lastrowid
    
    # Record interaction if it's a direct message
    if target_user:
        record_interaction(username, target_user, 'message')
    
    conn.commit()
    conn.close()
    update_user_session(username, room)
    return message_id

def get_message_history(room, limit=100, target_user=None):
    conn = init_database()
    cursor = conn.cursor()
    
    if target_user:
        # Direct messages between two users
        cursor.execute('''
            SELECT username, message_type, content, file_data, timestamp, reply_to, is_edited, reactions
            FROM messages 
            WHERE ((username = ? AND target_user = ?) OR (username = ? AND target_user = ?))
            ORDER BY timestamp ASC LIMIT ?
        ''', (st.session_state.username, target_user, target_user, st.session_state.username, limit))
    else:
        # Room messages
        cursor.execute('''
            SELECT username, message_type, content, file_data, timestamp, reply_to, is_edited, reactions
            FROM messages WHERE room = ? AND target_user IS NULL
            ORDER BY timestamp ASC LIMIT ?
        ''', (room, limit))
    
    messages = cursor.fetchall()
    conn.close()
    return messages

def get_online_users(room=None):
    conn = init_database()
    cursor = conn.cursor()
    
    if room:
        cursor.execute('''
            SELECT DISTINCT u.username, u.avatar, u.status, u.bio
            FROM users u
            JOIN user_sessions s ON u.username = s.username
            WHERE s.last_activity > datetime('now', '-2 minutes')
            ORDER BY u.username
        ''')
    else:
        cursor.execute('''
            SELECT DISTINCT u.username, u.avatar, u.status, u.bio
            FROM users u
            JOIN user_sessions s ON u.username = s.username
            WHERE s.last_activity > datetime('now', '-2 minutes')
            ORDER BY u.username
        ''')
    
    users = cursor.fetchall()
    conn.close()
    return users

def get_rooms():
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, created_by, category FROM rooms WHERE is_private = FALSE ORDER BY name")
    rooms = cursor.fetchall()
    conn.close()
    return rooms

def create_room(room_name, description, username, is_private=False, password=None, category='general', tags=''):
    conn = init_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO rooms (name, description, created_by, is_private, password, category, tags) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (room_name, description, username, is_private, hash_password(password) if password else None, category, tags)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_profile(username):
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, avatar, status, bio, interests, location, last_seen, profile_views FROM users WHERE username = ?",
        (username,)
    )
    profile = cursor.fetchone()
    
    # Update profile views
    if profile and username != st.session_state.username:
        cursor.execute(
            "UPDATE users SET profile_views = profile_views + 1 WHERE username = ?",
            (username,)
        )
        conn.commit()
    
    conn.close()
    return profile

def send_friend_request(from_user, to_user, message=""):
    conn = init_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO friend_requests (from_user, to_user, message) VALUES (?, ?, ?)",
            (from_user, to_user, message)
        )
        
        # Add notification
        cursor.execute(
            "INSERT INTO notifications (username, type, content) VALUES (?, ?, ?)",
            (to_user, 'friend_request', f"{from_user} sent you a friend request!")
        )
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_friend_requests(username):
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fr.id, fr.from_user, fr.message, fr.sent_at, u.avatar 
        FROM friend_requests fr
        JOIN users u ON fr.from_user = u.username
        WHERE fr.to_user = ? AND fr.status = 'pending'
        ORDER BY fr.sent_at DESC
    ''', (username,))
    requests = cursor.fetchall()
    conn.close()
    return requests

def respond_to_friend_request(request_id, response):
    conn = init_database()
    cursor = conn.cursor()
    
    # Get request details
    cursor.execute('SELECT from_user, to_user FROM friend_requests WHERE id = ?', (request_id,))
    request = cursor.fetchone()
    
    if request:
        from_user, to_user = request
        
        if response == 'accept':
            # Add to friends table
            cursor.execute(
                "INSERT INTO friends (user1, user2, status) VALUES (?, ?, 'accepted')",
                (from_user, to_user)
            )
            # Add notification
            cursor.execute(
                "INSERT INTO notifications (username, type, content) VALUES (?, ?, ?)",
                (from_user, 'friend_accepted', f"{to_user} accepted your friend request!")
            )
            record_interaction(from_user, to_user, 'friend')
        
        # Update request status
        cursor.execute(
            "UPDATE friend_requests SET status = ? WHERE id = ?",
            (response, request_id)
        )
        
        conn.commit()
    
    conn.close()

def get_friends(username):
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            CASE WHEN f.user1 = ? THEN f.user2 ELSE f.user1 END as friend_username,
            u.avatar, u.status, u.bio, u.last_seen
        FROM friends f
        JOIN users u ON (CASE WHEN f.user1 = ? THEN f.user2 ELSE f.user1 END) = u.username
        WHERE (f.user1 = ? OR f.user2 = ?) AND f.status = 'accepted'
        ORDER BY u.status DESC, u.last_seen DESC
    ''', (username, username, username, username))
    friends = cursor.fetchall()
    conn.close()
    return friends

def get_notifications(username):
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT type, content, created_at, is_read 
        FROM notifications 
        WHERE username = ? 
        ORDER BY created_at DESC 
        LIMIT 20
    ''', (username,))
    notifications = cursor.fetchall()
    conn.close()
    return notifications

def mark_notification_read(username):
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE notifications SET is_read = TRUE 
        WHERE username = ? AND is_read = FALSE
    ''', (username,))
    conn.commit()
    conn.close()

def record_interaction(user1, user2, interaction_type):
    conn = init_database()
    cursor = conn.cursor()
    
    # Ensure consistent ordering of usernames
    sorted_users = sorted([user1, user2])
    user1_sorted, user2_sorted = sorted_users
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_interactions 
        (user1, user2, interaction_type, strength, last_interaction)
        VALUES (?, ?, ?, COALESCE((SELECT strength FROM user_interactions WHERE user1 = ? AND user2 = ?), 0) + 1, CURRENT_TIMESTAMP)
    ''', (user1_sorted, user2_sorted, interaction_type, user1_sorted, user2_sorted))
    
    conn.commit()
    conn.close()

def get_user_recommendations(username, limit=5):
    conn = init_database()
    cursor = conn.cursor()
    
    # Get users with similar interactions or interests
    cursor.execute('''
        SELECT u.username, u.avatar, u.bio, u.status,
               COUNT(DISTINCT ui.interaction_type) as common_interactions
        FROM users u
        LEFT JOIN user_interactions ui ON (ui.user1 = ? AND ui.user2 = u.username) 
                                      OR (ui.user2 = ? AND ui.user1 = u.username)
        WHERE u.username != ? 
          AND u.username NOT IN (
              SELECT CASE WHEN user1 = ? THEN user2 ELSE user1 END 
              FROM friends 
              WHERE user1 = ? OR user2 = ?
          )
        GROUP BY u.username
        ORDER BY common_interactions DESC, u.profile_views DESC
        LIMIT ?
    ''', (username, username, username, username, username, username, limit))
    
    recommendations = cursor.fetchall()
    conn.close()
    return recommendations

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_room' not in st.session_state:
    st.session_state.current_room = 'general'
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = None  # For direct messaging
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "chat"

# Enhanced emoji support
EMOJIS = {
    "😊": "smile", "😂": "laugh", "❤️": "heart", "👍": "thumbs_up",
    "🔥": "fire", "🎉": "party", "🙏": "pray", "👋": "wave",
    "😢": "cry", "😡": "angry", "🤔": "thinking", "👏": "clap",
    "🎯": "target", "🚀": "rocket", "💡": "idea", "⭐": "star",
    "🌈": "rainbow", "🤖": "robot", "👻": "ghost", "🎨": "art"
}

def display_message(username, content, message_type='text', file_data=None, timestamp=None, reply_to=None, is_edited=False, reactions=None):
    timestamp_str = timestamp[:16] if timestamp else ""
    
    if username == "system":
        st.markdown(f"""
        <div class="chat-message system-message">
            🔔 {content} • {timestamp_str}
        </div>
        """, unsafe_allow_html=True)
    
    elif message_type == 'text':
        message_class = "user-message" if username == st.session_state.username else "other-message"
        
        edited_text = " ✏️" if is_edited else ""
        
        st.markdown(f"""
        <div class="chat-message {message_class}">
            <strong>{username}</strong>{edited_text} • {timestamp_str}<br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    
    elif message_type == 'image':
        message_class = "user-message" if username == st.session_state.username else "other-message"
        st.markdown(f"""
        <div class="chat-message {message_class}">
            <strong>{username}</strong> sent an image • {timestamp_str}<br>
        </div>
        """, unsafe_allow_html=True)
        
        if file_data:
            try:
                image = Image.open(io.BytesIO(file_data))
                st.image(image, width=300, caption=content)
            except:
                st.error("Could not display image")

def login_page():
    st.markdown('<div class="main-header">🌐 ChatVerse Pro</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>Connect, Chat, and Build Communities</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Feature showcase
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>👥 Connect</h3>
            <p>Find and connect with like-minded people</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>💬 Chat</h3>
            <p>Real-time messaging with friends & communities</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🌍 Discover</h3>
            <p>Join communities and meet new people</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Welcome Back! 👋")
                login_username = st.text_input("👤 Username", placeholder="Enter your username")
                login_password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                login_submit = st.form_submit_button("🚀 Login to ChatVerse Pro")
                
                if login_submit:
                    if login_username and login_password:
                        if authenticate_user(login_username, login_password):
                            st.session_state.authenticated = True
                            st.session_state.username = login_username
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.error("⚠️ Please fill in all fields")
        
        with tab2:
            with st.form("register_form"):
                st.subheader("Join Our Community! 🌟")
                reg_username = st.text_input("👤 Choose Username", placeholder="Enter unique username")
                reg_email = st.text_input("📧 Email", placeholder="your@email.com")
                reg_password = st.text_input("🔒 Create Password", type="password", placeholder="Strong password")
                reg_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                reg_bio = st.text_area("📝 Bio", placeholder="Tell us about yourself...")
                reg_interests = st.text_input("🎯 Interests", placeholder="e.g., tech, music, sports")
                reg_location = st.text_input("📍 Location", placeholder="Your city or country")
                
                register_submit = st.form_submit_button("🎉 Join ChatVerse Pro")
                
                if register_submit:
                    if reg_username and reg_password and reg_confirm:
                        if reg_password == reg_confirm:
                            if len(reg_password) >= 6:
                                if register_user(reg_username, reg_password, reg_email, reg_bio, reg_interests, reg_location):
                                    st.success("🎊 Registration successful! Please login.")
                                else:
                                    st.error("❌ Username or email already exists")
                            else:
                                st.error("⚠️ Password must be at least 6 characters")
                        else:
                            st.error("⚠️ Passwords do not match")
                    else:
                        st.error("⚠️ Please fill in all required fields")

def chat_page():
    # Auto refresh every 2 seconds
    st_autorefresh(interval=2000, key="chat_refresh")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Group Chat", 
        "👥 Direct Messages", 
        "🔍 Discover People", 
        "👨‍💼 My Profile",
        "🔔 Notifications"
    ])
    
    with tab1:
        render_group_chat()
    with tab2:
        render_direct_messages()
    with tab3:
        render_discover_people()
    with tab4:
        render_my_profile()
    with tab5:
        render_notifications()

def render_group_chat():
    st.markdown(f'<div class="main-header">💬 {st.session_state.current_room}</div>', unsafe_allow_html=True)
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        user_profile = get_user_profile(st.session_state.username)
        if user_profile:
            st.markdown(f"""
            <div class="user-card">
                <div style="font-size: 2rem;">{user_profile[1]}</div>
                <strong>{user_profile[0]}</strong><br>
                <small>🟢 {user_profile[2]}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Sidebar for group chat
    with st.sidebar:
        st.header("🏠 Chat Rooms")
        
        # Room categories
        rooms = get_rooms()
        categories = set([room[3] for room in rooms])
        
        for category in categories:
            with st.expander(f"📁 {category.title()}"):
                category_rooms = [room for room in rooms if room[3] == category]
                for room_name, description, created_by, cat in category_rooms:
                    if st.button(f"#{room_name}", key=f"room_{room_name}", use_container_width=True):
                        st.session_state.current_room = room_name
                        update_user_session(st.session_state.username, room_name)
                        st.rerun()
                    st.caption(f"📝 {description}")
        
        # Create new room
        with st.expander("➕ Create New Room"):
            new_room = st.text_input("Room Name")
            room_desc = st.text_input("Description")
            room_category = st.selectbox("Category", ["general", "technology", "gaming", "music", "sports", "education", "business"])
            is_private = st.checkbox("Private Room")
            room_password = st.text_input("Room Password", type="password") if is_private else None
            
            if st.button("Create Room"):
                if new_room:
                    if create_room(new_room, room_desc, st.session_state.username, is_private, room_password, room_category):
                        st.success(f"🎊 Room '{new_room}' created!")
                        st.rerun()
                    else:
                        st.error("❌ Room already exists")
        
        # Online users in current room
        st.subheader("👥 Online Now")
        online_users = get_online_users(st.session_state.current_room)
        for username, avatar, status, bio in online_users:
            if username != st.session_state.username:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.write(f"{avatar}")
                with col2:
                    st.write(f"**{username}**")
                    st.caption(bio[:30] + "..." if len(bio) > 30 else bio)
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat messages container
        with st.container():
            st.subheader("💭 Group Messages")
            messages = get_message_history(st.session_state.current_room)
            
            if not messages:
                st.info("💬 No messages yet. Start the conversation!")
            else:
                for msg in messages:
                    username, msg_type, content, file_data, timestamp, reply_to, is_edited, reactions = msg
                    display_message(username, content, msg_type, file_data, timestamp, reply_to, is_edited, reactions)
    
    with col2:
        # Quick actions and room info
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
        
        if st.button("📢 Announce", use_container_width=True):
            save_message(
                st.session_state.current_room,
                "system",
                'text',
                f"{st.session_state.username} made an announcement! 🎉"
            )
            st.rerun()
        
        # Room information
        current_room_info = next((room for room in rooms if room[0] == st.session_state.current_room), None)
        if current_room_info:
            st.info(f"""
            **Room:** {current_room_info[0]}
            **Category:** {current_room_info[3]}
            **Description:** {current_room_info[1]}
            """)
    
    # Message input
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        message = st.text_area(
            "Type your message...",
            key="group_message",
            label_visibility="collapsed",
            placeholder="Type your message here...",
            height=60
        )
    
    with col2:
        if st.button("🚀 Send", use_container_width=True, key="send_group"):
            if message:
                save_message(
                    st.session_state.current_room,
                    st.session_state.username,
                    'text',
                    message
                )
                st.session_state.group_message = ""
                st.rerun()

def render_direct_messages():
    st.markdown('<div class="main-header">👥 Direct Messages</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("� Friends List")
        friends = get_friends(st.session_state.username)
        
        if not friends:
            st.info("👋 No friends yet. Go to Discover tab to find people!")
        else:
            for friend_username, avatar, status, bio, last_seen in friends:
                status_dot = "🟢" if status == 'online' else "🔴"
                if st.button(f"{status_dot} {avatar} {friend_username}", key=f"dm_{friend_username}", use_container_width=True):
                    st.session_state.current_chat = friend_username
                    st.rerun()
                st.caption(bio[:40] + "..." if len(bio) > 40 else bio)
    
    with col2:
        if st.session_state.current_chat:
            st.subheader(f"💬 Chat with {st.session_state.current_chat}")
            
            # Display direct messages
            messages = get_message_history("direct", target_user=st.session_state.current_chat)
            
            chat_container = st.container(height=400)
            with chat_container:
                if not messages:
                    st.info("💭 No messages yet. Start the conversation!")
                else:
                    for msg in messages:
                        username, msg_type, content, file_data, timestamp, reply_to, is_edited, reactions = msg
                        display_message(username, content, msg_type, file_data, timestamp, reply_to, is_edited, reactions)
            
            # Direct message input
            col1, col2 = st.columns([4, 1])
            with col1:
                dm_message = st.text_input(
                    "Type a direct message...",
                    key="dm_input",
                    placeholder=f"Message {st.session_state.current_chat}...",
                    label_visibility="collapsed"
                )
            with col2:
                if st.button("📤 Send", key="send_dm"):
                    if dm_message:
                        save_message(
                            "direct",
                            st.session_state.username,
                            'text',
                            dm_message,
                            target_user=st.session_state.current_chat
                        )
                        st.session_state.dm_input = ""
                        st.rerun()
        else:
            st.info("👈 Select a friend from the list to start chatting!")

def render_discover_people():
    st.markdown('<div class="main-header">🔍 Discover People</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 Recommended", "🌐 Online Users", "📨 Friend Requests"])
    
    with tab1:
        st.subheader("💫 People You May Know")
        recommendations = get_user_recommendations(st.session_state.username)
        
        if not recommendations:
            st.info("🌟 No recommendations available yet. Keep using the app to get personalized suggestions!")
        else:
            for username, avatar, bio, status, common_interactions in recommendations:
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 2])
                    with col1:
                        st.write(f"## {avatar}")
                    with col2:
                        st.write(f"**{username}**")
                        st.caption(f"🟢 {status}" if status == 'online' else "🔴 offline")
                        st.caption(bio[:50] + "..." if len(bio) > 50 else bio)
                    with col3:
                        if st.button("👋 Connect", key=f"connect_{username}"):
                            if send_friend_request(st.session_state.username, username, "Hi! I'd like to connect with you."):
                                st.success(f"✅ Friend request sent to {username}!")
                            else:
                                st.error("❌ Could not send friend request")
                    st.markdown("---")
    
    with tab2:
        st.subheader("🌐 Currently Online")
        online_users = get_online_users()
        online_users = [user for user in online_users if user[0] != st.session_state.username]
        
        if not online_users:
            st.info("😴 No one is online right now. Check back later!")
        else:
            for username, avatar, status, bio in online_users:
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 2])
                    with col1:
                        st.write(f"## {avatar}")
                    with col2:
                        st.write(f"**{username}**")
                        st.caption("🟢 Online Now")
                        st.caption(bio[:50] + "..." if len(bio) > 50 else bio)
                    with col3:
                        if st.button("👋 Connect", key=f"online_{username}"):
                            if send_friend_request(st.session_state.username, username, "Hi! Saw you're online and wanted to connect."):
                                st.success(f"✅ Friend request sent to {username}!")
                            else:
                                st.error("❌ Could not send friend request")
                    st.markdown("---")
    
    with tab3:
        st.subheader("📨 Pending Friend Requests")
        friend_requests = get_friend_requests(st.session_state.username)
        
        if not friend_requests:
            st.info("📭 No pending friend requests")
        else:
            for req_id, from_user, message, sent_at, avatar in friend_requests:
                with st.container():
                    st.markdown(f"""
                    <div class="friend-card">
                        <div style="font-size: 2rem; text-align: center;">{avatar}</div>
                        <h4>{from_user}</h4>
                        <p>{message or 'Wants to be your friend!'}</p>
                        <small>Sent: {sent_at[:16]}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Accept", key=f"accept_{req_id}", use_container_width=True):
                            respond_to_friend_request(req_id, 'accept')
                            st.success(f"✅ You are now friends with {from_user}!")
                            st.rerun()
                    with col2:
                        if st.button("❌ Decline", key=f"decline_{req_id}", use_container_width=True):
                            respond_to_friend_request(req_id, 'decline')
                            st.info(f"❌ Friend request from {from_user} declined")
                            st.rerun()

def render_my_profile():
    st.markdown('<div class="main-header">👨‍💼 My Profile</div>', unsafe_allow_html=True)
    
    user_profile = get_user_profile(st.session_state.username)
    if user_profile:
        username, avatar, status, bio, interests, location, last_seen, profile_views = user_profile
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 20px;">{avatar}</div>
                <h2>{username}</h2>
                <p>🟢 {status}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Profile Views", profile_views)
            st.metric("Last Seen", last_seen[:16])
        
        with col2:
            st.subheader("📝 About Me")
            st.info(f"**Bio:** {bio}")
            st.info(f"**Interests:** {interests}")
            st.info(f"**Location:** {location}")
            
            # Friends count
            friends = get_friends(st.session_state.username)
            st.metric("Friends", len(friends))
            
            # Edit profile
            with st.expander("✏️ Edit Profile"):
                new_bio = st.text_area("Bio", value=bio)
                new_interests = st.text_input("Interests", value=interests)
                new_location = st.text_input("Location", value=location)
                
                if st.button("Update Profile"):
                    # Update profile in database
                    conn = init_database()
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE users SET bio = ?, interests = ?, location = ? WHERE username = ?",
                        (new_bio, new_interests, new_location, st.session_state.username)
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Profile updated successfully!")
                    st.rerun()

def render_notifications():
    st.markdown('<div class="main-header">🔔 Notifications</div>', unsafe_allow_html=True)
    
    notifications = get_notifications(st.session_state.username)
    
    if not notifications:
        st.info("📭 No notifications")
    else:
        unread_count = sum(1 for notif in notifications if not notif[3])
        if unread_count > 0:
            st.success(f"🔔 You have {unread_count} unread notifications")
            
            if st.button("Mark All as Read"):
                mark_notification_read(st.session_state.username)
                st.rerun()
        
        for notif_type, content, created_at, is_read in notifications:
            read_icon = "✅" if is_read else "🔔"
            st.markdown(f"""
            <div class="notification">
                {read_icon} <strong>{content}</strong><br>
                <small>{created_at[:16]}</small>
            </div>
            """, unsafe_allow_html=True)

def main():
    # Initialize database
    init_database()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        # Navigation sidebar
        with st.sidebar:
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.rerun()
        
        chat_page()

if __name__ == "__main__":
    main()