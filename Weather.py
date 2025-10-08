import streamlit as st
import requests
import json
import asyncio
import threading
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Optional
import time
import base64

# Advanced configuration
class WeatherConfig:
    API_BASE = "http://api.openweathermap.org/data/2.5"
    CACHE_DURATION = 300  # 5 minutes
    MAX_HISTORY = 50
    WEATHER_EMOJIS = {
        'clear': '☀️', 'clouds': '☁️', 'rain': '🌧️', 'drizzle': '🌦️',
        'thunderstorm': '⛈️', 'snow': '❄️', 'mist': '🌫️', 'fog': '🌁',
        'haze': '😶‍🌫️', 'dust': '💨', 'sand': '🌪️', 'ash': '🌋',
        'squall': '💨', 'tornado': '🌪️'
    }
    
    # Weather video mappings
    WEATHER_VIDEOS = {
        'clear': 'https://assets.mixkit.co/videos/preview/mixkit-sunrise-over-the-sea-1186-large.mp4',
        'clouds': 'https://assets.mixkit.co/videos/preview/mixkit-white-clouds-in-the-sky-2401-large.mp4',
        'rain': 'https://assets.mixkit.co/videos/preview/mixkit-rain-falling-on-the-window-1185-large.mp4',
        'snow': 'https://assets.mixkit.co/videos/preview/mixkit-snow-falling-in-a-forest-1184-large.mp4',
        'thunderstorm': 'https://assets.mixkit.co/videos/preview/mixkit-lightning-storm-in-the-mountains-1183-large.mp4',
        'default': 'https://assets.mixkit.co/videos/preview/mixkit-aerial-view-of-a-river-in-a-forest-1182-large.mp4'
    }

def initialize_session_state():
    """Initialize all session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.weather_history = []
        st.session_state.favorite_cities = ['London', 'New York', 'Tokyo', 'Paris']
        st.session_state.user_preferences = {
            'units': 'metric',
            'theme': 'dark',
            'animations': True,
            'notifications': True,
            'background_video': True,
            'auto_refresh': True,
            'video_intensity': 0.7
        }
        st.session_state.selected_city = 'London'
        st.session_state.show_history = False
        st.session_state.cache = {}
        st.session_state.current_weather_type = 'clear'
        st.session_state.last_update = datetime.now()

class AdvancedWeatherAnimations:
    """Advanced animation system with weather-specific effects"""
    
    @staticmethod
    def get_animation_js():
        return """
        <script>
        class AdvancedWeatherAnimations {
            constructor() {
                this.currentWeather = '';
                this.particleSystems = new Map();
                this.videoElement = null;
                this.init();
            }

            init() {
                this.createMainCanvas();
                this.setupVideoBackground();
                this.setupEventListeners();
                this.startAnimationLoop();
            }

            createMainCanvas() {
                this.canvas = document.createElement('canvas');
                this.canvas.id = 'advanced-weather-canvas';
                this.canvas.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: -1;
                    opacity: 0.7;
                    transition: opacity 0.5s ease;
                `;
                document.body.appendChild(this.canvas);
                this.ctx = this.canvas.getContext('2d');
                this.resizeCanvas();
                window.addEventListener('resize', () => this.resizeCanvas());
            }

            setupVideoBackground() {
                this.videoContainer = document.createElement('div');
                this.videoContainer.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: -2;
                    overflow: hidden;
                `;
                
                this.videoElement = document.createElement('video');
                this.videoElement.style.cssText = `
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    opacity: 0.7;
                    transition: opacity 1s ease;
                `;
                this.videoElement.autoplay = true;
                this.videoElement.muted = true;
                this.videoElement.loop = true;
                
                this.videoContainer.appendChild(this.videoElement);
                document.body.appendChild(this.videoContainer);
            }

            setWeatherType(weatherType, videoUrl = null) {
                this.currentWeather = weatherType.toLowerCase();
                
                // Set video background if available
                if (videoUrl && window.videoBackgroundEnabled) {
                    this.setVideoBackground(videoUrl);
                }
                
                this.createWeatherEffect(this.currentWeather);
            }

            setVideoBackground(videoUrl) {
                if (this.videoElement) {
                    this.videoElement.style.opacity = '0';
                    setTimeout(() => {
                        this.videoElement.src = videoUrl;
                        this.videoElement.load();
                        this.videoElement.play().catch(e => console.log('Video play failed:', e));
                        this.videoElement.style.opacity = window.videoIntensity || '0.7';
                    }, 500);
                }
            }

            createWeatherEffect(weatherType) {
                this.clearParticles();
                
                switch(weatherType) {
                    case 'rain':
                        this.createRainEffect();
                        break;
                    case 'snow':
                        this.createSnowEffect();
                        break;
                    case 'clear':
                        this.createSunEffect();
                        break;
                    case 'clouds':
                        this.createCloudEffect();
                        break;
                    case 'thunderstorm':
                        this.createThunderEffect();
                        break;
                    default:
                        this.createDefaultEffect();
                }
            }

            createRainEffect() {
                const rainDrops = [];
                for (let i = 0; i < 200; i++) {
                    rainDrops.push({
                        x: Math.random() * this.canvas.width,
                        y: Math.random() * this.canvas.height,
                        length: Math.random() * 20 + 10,
                        speed: Math.random() * 5 + 5,
                        opacity: Math.random() * 0.5 + 0.3
                    });
                }
                this.particleSystems.set('rain', rainDrops);
            }

            createSnowEffect() {
                const snowFlakes = [];
                for (let i = 0; i < 150; i++) {
                    snowFlakes.push({
                        x: Math.random() * this.canvas.width,
                        y: Math.random() * this.canvas.height,
                        radius: Math.random() * 3 + 1,
                        speed: Math.random() * 2 + 1,
                        swing: Math.random() * 2 - 1,
                        opacity: Math.random() * 0.8 + 0.2
                    });
                }
                this.particleSystems.set('snow', snowFlakes);
            }

            createSunEffect() {
                const sunRays = [];
                for (let i = 0; i < 30; i++) {
                    sunRays.push({
                        angle: (i / 30) * Math.PI * 2,
                        length: Math.random() * 50 + 30,
                        speed: Math.random() * 0.02 + 0.01,
                        opacity: Math.random() * 0.3 + 0.1
                    });
                }
                this.particleSystems.set('sun', sunRays);
            }

            createCloudEffect() {
                const clouds = [];
                for (let i = 0; i < 6; i++) {
                    clouds.push({
                        x: Math.random() * this.canvas.width,
                        y: Math.random() * (this.canvas.height * 0.4),
                        width: Math.random() * 120 + 60,
                        speed: Math.random() * 0.3 + 0.1,
                        opacity: Math.random() * 0.3 + 0.1
                    });
                }
                this.particleSystems.set('clouds', clouds);
            }

            createThunderEffect() {
                this.lightning = {
                    active: false,
                    intensity: 0,
                    timer: 0
                };
                this.particleSystems.set('thunder', []);
            }

            createDefaultEffect() {
                const particles = [];
                for (let i = 0; i < 60; i++) {
                    particles.push({
                        x: Math.random() * this.canvas.width,
                        y: Math.random() * this.canvas.height,
                        radius: Math.random() * 2 + 0.5,
                        speedX: Math.random() * 2 - 1,
                        speedY: Math.random() * 2 - 1,
                        opacity: Math.random() * 0.3 + 0.1
                    });
                }
                this.particleSystems.set('default', particles);
            }

            updateParticles() {
                // Update rain
                if (this.particleSystems.has('rain')) {
                    const rain = this.particleSystems.get('rain');
                    rain.forEach(drop => {
                        drop.y += drop.speed;
                        if (drop.y > this.canvas.height) {
                            drop.y = -drop.length;
                            drop.x = Math.random() * this.canvas.width;
                        }
                    });
                }

                // Update snow
                if (this.particleSystems.has('snow')) {
                    const snow = this.particleSystems.get('snow');
                    snow.forEach(flake => {
                        flake.y += flake.speed;
                        flake.x += flake.swing * Math.sin(flake.y * 0.01);
                        if (flake.y > this.canvas.height) {
                            flake.y = -flake.radius;
                            flake.x = Math.random() * this.canvas.width;
                        }
                    });
                }

                // Update clouds
                if (this.particleSystems.has('clouds')) {
                    const clouds = this.particleSystems.get('clouds');
                    clouds.forEach(cloud => {
                        cloud.x += cloud.speed;
                        if (cloud.x > this.canvas.width + cloud.width) {
                            cloud.x = -cloud.width;
                        }
                    });
                }

                // Update thunder
                if (this.particleSystems.has('thunder')) {
                    this.lightning.timer++;
                    if (this.lightning.timer > 90) {
                        this.lightning.active = Math.random() > 0.8;
                        this.lightning.intensity = this.lightning.active ? Math.random() * 0.4 + 0.2 : 0;
                        if (this.lightning.active) this.lightning.timer = 0;
                    }
                }
            }

            drawParticles() {
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

                // Draw rain
                if (this.particleSystems.has('rain')) {
                    const rain = this.particleSystems.get('rain');
                    this.ctx.strokeStyle = 'rgba(174, 194, 224, 0.6)';
                    this.ctx.lineWidth = 1.5;
                    rain.forEach(drop => {
                        this.ctx.beginPath();
                        this.ctx.moveTo(drop.x, drop.y);
                        this.ctx.lineTo(drop.x, drop.y + drop.length);
                        this.ctx.stroke();
                    });
                }

                // Draw snow
                if (this.particleSystems.has('snow')) {
                    const snow = this.particleSystems.get('snow');
                    snow.forEach(flake => {
                        this.ctx.fillStyle = `rgba(255, 255, 255, ${flake.opacity})`;
                        this.ctx.beginPath();
                        this.ctx.arc(flake.x, flake.y, flake.radius, 0, Math.PI * 2);
                        this.ctx.fill();
                    });
                }

                // Draw thunder
                if (this.particleSystems.has('thunder') && this.lightning.active) {
                    this.ctx.fillStyle = `rgba(255, 255, 255, ${this.lightning.intensity})`;
                    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                }
            }

            clearParticles() {
                this.particleSystems.clear();
                this.lightning = { active: false, intensity: 0, timer: 0 };
            }

            startAnimationLoop() {
                const animate = () => {
                    this.updateParticles();
                    this.drawParticles();
                    requestAnimationFrame(animate.bind(this));
                };
                animate();
            }

            setupEventListeners() {
                // Mouse interaction
                this.canvas.addEventListener('mousemove', (e) => {
                    this.mouseX = e.clientX;
                    this.mouseY = e.clientY;
                });

                // Keyboard shortcuts
                document.addEventListener('keydown', (e) => {
                    if (e.ctrlKey && e.key === 'r') {
                        e.preventDefault();
                        window.dispatchEvent(new Event('refreshWeather'));
                    }
                    if (e.key === 'Escape') {
                        this.toggleAnimations();
                    }
                });

                // Visibility API for performance
                document.addEventListener('visibilitychange', () => {
                    const opacity = document.hidden ? '0.3' : '0.7';
                    this.canvas.style.opacity = opacity;
                    if (this.videoElement) {
                        this.videoElement.style.opacity = document.hidden ? '0.3' : (window.videoIntensity || '0.7');
                    }
                });
            }

            toggleAnimations() {
                const isVisible = this.canvas.style.display !== 'none';
                this.canvas.style.display = isVisible ? 'none' : 'block';
                if (this.videoElement) {
                    this.videoElement.style.display = isVisible ? 'none' : 'block';
                }
            }

            setVideoIntensity(intensity) {
                if (this.videoElement) {
                    this.videoElement.style.opacity = intensity;
                }
            }
        }

        // Initialize advanced animations
        let weatherAnimations;
        document.addEventListener('DOMContentLoaded', () => {
            weatherAnimations = new AdvancedWeatherAnimations();
            
            // Listen for weather updates
            window.addEventListener('weatherUpdate', (e) => {
                if (e.detail && e.detail.weather) {
                    const videoUrl = e.detail.videoUrl;
                    weatherAnimations.setWeatherType(e.detail.weather, videoUrl);
                }
            });

            // Listen for video intensity changes
            window.addEventListener('videoIntensityChange', (e) => {
                if (weatherAnimations && e.detail) {
                    weatherAnimations.setVideoIntensity(e.detail.intensity);
                }
            });

            // Auto-refresh system
            setInterval(() => {
                if (window.autoRefreshEnabled) {
                    window.dispatchEvent(new Event('refreshWeather'));
                }
            }, 300000);

            // Performance monitoring
            let lastUpdate = Date.now();
            const updateInterval = 1000 / 60; // 60 FPS
            
            function maintainPerformance() {
                const now = Date.now();
                if (now - lastUpdate > updateInterval) {
                    lastUpdate = now;
                }
                requestAnimationFrame(maintainPerformance);
            }
            maintainPerformance();
        });

        // Export to global scope for Streamlit interaction
        window.weatherAnimations = weatherAnimations;
        </script>
        """

class RealTimeDataManager:
    """Manages real-time data updates and caching"""
    
    def __init__(self):
        self.update_handlers = []
        
    def add_update_handler(self, handler):
        self.update_handlers.append(handler)
        
    def notify_handlers(self, data):
        for handler in self.update_handlers:
            handler(data)

class AdvancedWeatherApp:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.config = WeatherConfig()
        self.data_manager = RealTimeDataManager()
        
    def get_current_weather(self, city_name: str) -> Optional[Dict]:
        cache_key = f"current_{city_name}"
        if cache_key in st.session_state.cache and time.time() - st.session_state.cache[cache_key]['timestamp'] < self.config.CACHE_DURATION:
            return st.session_state.cache[cache_key]['data']
            
        url = f"{self.config.API_BASE}/weather?q={city_name}&appid={self.api_key}&units=metric"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("cod") == 200:
                st.session_state.cache[cache_key] = {'data': data, 'timestamp': time.time()}
                self._add_to_history(data)
                self.data_manager.notify_handlers(data)
                return data
        except Exception as e:
            st.error(f"🚨 Error fetching weather data: {e}")
        return None
    
    def get_forecast(self, city_name: str) -> Optional[Dict]:
        url = f"{self.config.API_BASE}/forecast?q={city_name}&appid={self.api_key}&units=metric"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            return data if data.get("cod") == "200" else None
        except Exception as e:
            st.error(f"🚨 Error fetching forecast: {e}")
            return None
    
    def _add_to_history(self, data: Dict):
        history_entry = {
            'timestamp': datetime.now(),
            'city': data['name'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'weather': data['weather'][0]['main'],
            'description': data['weather'][0]['description']
        }
        st.session_state.weather_history.append(history_entry)
        if len(st.session_state.weather_history) > self.config.MAX_HISTORY:
            st.session_state.weather_history.pop(0)

class WeatherVisualizations:
    """Advanced data visualizations"""
    
    @staticmethod
    def create_temperature_trend(history: List[Dict]):
        if len(history) < 2:
            return None
            
        df = pd.DataFrame(history)
        fig = px.line(df, x='timestamp', y='temperature', 
                     title='📈 Temperature Trend Over Time',
                     color_discrete_sequence=['#FF6B6B'])
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            template="plotly_dark" if st.session_state.user_preferences['theme'] == 'dark' else "plotly_white",
            hovermode='x unified'
        )
        return fig
    
    @staticmethod
    def create_weather_radar(current_data: Dict):
        fig = go.Figure()
        
        metrics = ['Temperature', 'Humidity', 'Wind Speed', 'Pressure', 'Visibility']
        values = [
            current_data['main']['temp'],
            current_data['main']['humidity'],
            current_data['wind']['speed'],
            current_data['main']['pressure'],
            current_data.get('visibility', 10000) / 100
        ]
        
        max_vals = [40, 100, 20, 1100, 100]
        normalized_values = [min((v / max_v) * 100, 100) for v, max_v in zip(values, max_vals)]
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=metrics,
            fill='toself',
            name='Current Conditions',
            line=dict(color='#4ECDC4', width=2),
            fillcolor='rgba(78, 205, 196, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='lightgray'),
                angularaxis=dict(gridcolor='lightgray')
            ),
            showlegend=False,
            title="🌪️ Weather Metrics Radar",
            font=dict(size=12)
        )
        return fig
    
    @staticmethod
    def create_forecast_chart(forecast_data: Dict):
        if not forecast_data or 'list' not in forecast_data:
            return None
            
        times = []
        temps = []
        humidity = []
        
        for item in forecast_data['list'][:8]:  # Next 24 hours
            times.append(datetime.fromtimestamp(item['dt']).strftime('%H:%M'))
            temps.append(item['main']['temp'])
            humidity.append(item['main']['humidity'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=temps, mode='lines+markers', 
                               name='Temperature', line=dict(color='#FF6B6B', width=3)))
        fig.add_trace(go.Bar(x=times, y=humidity, name='Humidity', 
                           marker_color='#4ECDC4', opacity=0.6, yaxis='y2'))
        
        fig.update_layout(
            title='🌡️ 24-Hour Forecast',
            xaxis_title='Time',
            yaxis=dict(title='Temperature (°C)', side='left'),
            yaxis2=dict(title='Humidity (%)', side='right', overlaying='y'),
            template="plotly_dark" if st.session_state.user_preferences['theme'] == 'dark' else "plotly_white",
            showlegend=True
        )
        return fig

def inject_advanced_animations():
    """Inject sophisticated JavaScript animations"""
    st.components.v1.html(AdvancedWeatherAnimations.get_animation_js(), height=0)

def inject_advanced_css():
    """Inject advanced CSS with dynamic themes"""
    theme = st.session_state.user_preferences['theme']
    video_intensity = st.session_state.user_preferences['video_intensity']
    
    css = f"""
    <style>
        :root {{
            --primary-color: { '#1f77b4' if theme == 'light' else '#74b9ff' };
            --bg-gradient: { 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if theme == 'light' else 'linear-gradient(135deg, #2c3e50 0%, #3498db 100%)' };
            --card-bg: { 'rgba(255, 255, 255, 0.92)' if theme == 'light' else 'rgba(30, 41, 59, 0.92)' };
            --text-color: { '#2c3e50' if theme == 'light' else '#f8fafc' };
            --border-color: { 'rgba(255,255,255,0.2)' if theme == 'light' else 'rgba(255,255,255,0.1)' };
        }}
        
        .stApp {{
            background: transparent !important;
        }}
        
        .main .block-container {{
            padding-top: 2rem;
            background: transparent;
        }}
        
        .advanced-weather-card {{
            background: var(--card-bg);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border-radius: 20px;
            padding: 25px;
            margin: 15px 0;
            color: var(--text-color);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid var(--border-color);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .advanced-weather-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--bg-gradient);
        }}
        
        .advanced-weather-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin: 20px 0;
        }}
        
        .metric-item {{
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
            transition: transform 0.3s ease;
        }}
        
        .metric-item:hover {{
            transform: scale(1.05);
        }}
        
        .weather-glow {{
            animation: glow 3s ease-in-out infinite alternate;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        }}
        
        @keyframes glow {{
            from {{ 
                text-shadow: 0 0 20px rgba(116, 185, 255, 0.5);
                transform: scale(1);
            }}
            to {{ 
                text-shadow: 0 0 30px rgba(116, 185, 255, 0.8), 0 0 40px rgba(116, 185, 255, 0.6);
                transform: scale(1.02);
            }}
        }}
        
        .floating {{
            animation: floating 4s ease-in-out infinite;
        }}
        
        @keyframes floating {{
            0% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-12px) rotate(1deg); }}
            100% {{ transform: translateY(0px) rotate(0deg); }}
        }}
        
        .pulse {{
            animation: pulse 2s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--primary-color);
            border-radius: 4px;
        }}
        
        /* Video background overlay */
        .video-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: { 'rgba(255,255,255,0.1)' if theme == 'light' else 'rgba(0,0,0,0.3)' };
            z-index: -2;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    # Inject video background settings
    st.components.v1.html(f"""
    <script>
        window.videoBackgroundEnabled = {str(st.session_state.user_preferences['background_video']).lower()};
        window.videoIntensity = '{video_intensity}';
    </script>
    """, height=0)

def create_sidebar(weather_app: AdvancedWeatherApp):
    """Advanced sidebar with multiple features"""
    with st.sidebar:
        st.title("⚙️ Control Panel")
        
        # Theme selector
        theme = st.selectbox("🎨 Theme", ["dark", "light"], 
                           index=0 if st.session_state.user_preferences['theme'] == 'dark' else 1)
        st.session_state.user_preferences['theme'] = theme
        
        # Background video settings
        st.subheader("🎥 Background Settings")
        background_video = st.checkbox("Enable Video Background", 
                                     value=st.session_state.user_preferences['background_video'])
        st.session_state.user_preferences['background_video'] = background_video
        
        if background_video:
            video_intensity = st.slider("Video Intensity", 0.1, 1.0, 
                                      value=st.session_state.user_preferences['video_intensity'])
            st.session_state.user_preferences['video_intensity'] = video_intensity
            st.components.v1.html(f"""
            <script>
                window.videoBackgroundEnabled = true;
                window.videoIntensity = '{video_intensity}';
                if (window.weatherAnimations) {{
                    window.weatherAnimations.setVideoIntensity('{video_intensity}');
                }}
            </script>
            """, height=0)
        
        # Auto-refresh
        auto_refresh = st.checkbox("🔄 Auto Refresh (5min)", 
                                 value=st.session_state.user_preferences.get('auto_refresh', True))
        st.session_state.user_preferences['auto_refresh'] = auto_refresh
        st.components.v1.html(f"""
        <script>window.autoRefreshEnabled = {str(auto_refresh).lower()};</script>
        """, height=0)
        
        # Animation toggle
        animations = st.checkbox("✨ Particle Animations", 
                               value=st.session_state.user_preferences['animations'])
        st.session_state.user_preferences['animations'] = animations
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("📊 Stats", use_container_width=True):
                st.session_state.show_history = not st.session_state.show_history
        
        # Favorite cities
        st.subheader("⭐ Favorite Cities")
        for city in st.session_state.favorite_cities:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📍 {city}", key=f"fav_{city}", use_container_width=True):
                    st.session_state.selected_city = city
                    st.rerun()
            with col2:
                if st.button("❌", key=f"remove_{city}"):
                    st.session_state.favorite_cities.remove(city)
                    st.rerun()
        
        # Add new favorite
        new_fav = st.text_input("Add new favorite city:")
        if st.button("Add to Favorites") and new_fav:
            if new_fav not in st.session_state.favorite_cities:
                st.session_state.favorite_cities.append(new_fav)
                st.rerun()

        # App info and stats
        st.subheader("📊 App Statistics")
        st.metric("Cities Searched", len(st.session_state.weather_history))
        st.metric("Favorite Cities", len(st.session_state.favorite_cities))
        
        if st.session_state.weather_history:
            avg_temp = np.mean([entry['temperature'] for entry in st.session_state.weather_history])
            st.metric("Average Temp", f"{avg_temp:.1f}°C")

def display_advanced_weather(data: Dict, weather_app: AdvancedWeatherApp):
    """Display weather data with advanced visualizations"""
    
    # Update current weather type
    st.session_state.current_weather_type = data['weather'][0]['main'].lower()
    
    # Main weather card with enhanced design
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        weather_emoji = WeatherConfig.WEATHER_EMOJIS.get(st.session_state.current_weather_type, '🌈')
        st.markdown(f"""
        <div class="advanced-weather-card floating">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
                <h2 style="margin: 0; font-size: 2rem;">{weather_emoji}</h2>
                <div>
                    <h2 style="margin: 0;">🌍 {data['name']}, {data['sys']['country']}</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 1.1rem;">{data['weather'][0]['description'].capitalize()}</p>
                </div>
            </div>
            <h1 style="font-size: 4rem; margin: 0; background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {data['main']['temp']:.1f}°C
            </h1>
            <div class="metric-grid">
                <div class="metric-item pulse">💧 {data['main']['humidity']}%</div>
                <div class="metric-item pulse">💨 {data['wind']['speed']} m/s</div>
                <div class="metric-item pulse">📊 {data['main']['pressure']} hPa</div>
                <div class="metric-item pulse">👁️ {data.get('visibility', 'N/A')}m</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M")
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M")
        st.markdown(f"""
        <div class="advanced-weather-card">
            <h3>🌅 Sun Times</h3>
            <p style="font-size: 1.1rem;">🌅 Sunrise: {sunrise}</p>
            <p style="font-size: 1.1rem;">🌇 Sunset: {sunset}</p>
            <p style="font-size: 1.1rem;">📅 Day Length: {timedelta(seconds=data['sys']['sunset']-data['sys']['sunrise'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="advanced-weather-card">
            <h3>📈 Temperature Info</h3>
            <p style="font-size: 1.1rem;">🌡️ Feels like: {data['main']['feels_like']:.1f}°C</p>
            <p style="font-size: 1.1rem;">📉 Minimum: {data['main']['temp_min']:.1f}°C</p>
            <p style="font-size: 1.1rem;">📈 Maximum: {data['main']['temp_max']:.1f}°C</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Forecast section
    st.subheader("🌤️ Weather Forecast")
    with st.spinner("Loading forecast..."):
        forecast_data = weather_app.get_forecast(st.session_state.selected_city)
    
    if forecast_data:
        forecast_col1, forecast_col2 = st.columns(2)
        
        with forecast_col1:
            forecast_fig = WeatherVisualizations.create_forecast_chart(forecast_data)
            if forecast_fig:
                st.plotly_chart(forecast_fig, use_container_width=True)
        
        with forecast_col2:
            # Display next 5 forecast items
            st.markdown("#### 📅 Upcoming Hours")
            for i, item in enumerate(forecast_data['list'][:5]):
                time_str = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                emoji = WeatherConfig.WEATHER_EMOJIS.get(item['weather'][0]['main'].lower(), '🌈')
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.markdown(f"<h3>{emoji}</h3>", unsafe_allow_html=True)
                with col2:
                    st.write(f"**{time_str}**")
                    st.write(item['weather'][0]['description'].capitalize())
                with col3:
                    st.write(f"**{item['main']['temp']:.1f}°C**")
                if i < 4:
                    st.divider()
    
    # Advanced visualizations
    st.subheader("📊 Advanced Analytics")
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        if len(st.session_state.weather_history) >= 2:
            trend_fig = WeatherVisualizations.create_temperature_trend(st.session_state.weather_history)
            if trend_fig:
                st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.info("📈 Temperature history will appear here after multiple searches")
    
    with viz_col2:
        radar_fig = WeatherVisualizations.create_weather_radar(data)
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)
    
    # Real-time metrics
    st.subheader("🔄 Real-time Metrics")
    metrics_cols = st.columns(4)
    metrics = [
        ("🌡️ Apparent Temp", f"{data['main']['feels_like']:.1f}°C"),
        ("💨 Wind Gust", f"{data['wind'].get('gust', 'N/A')} m/s"),
        ("☁️ Cloudiness", f"{data['clouds'].get('all', 0)}%"),
        ("🌊 Sea Level", f"{data['main'].get('sea_level', 'N/A')} hPa")
    ]
    
    for col, (label, value) in zip(metrics_cols, metrics):
        with col:
            st.metric(label, value)

def weather_animations_component():
    """Component that handles all weather-related animations"""
    
    # JavaScript for animations
    st.components.v1.html("""
    <div id="weather-animations">
        <canvas id="weather-particles"></canvas>
    </div>
    
    <script>
    // Weather Animation Component
    class WeatherAnimationComponent {
        constructor() {
            this.canvas = document.getElementById('weather-particles');
            this.ctx = this.canvas.getContext('2d');
            this.particles = [];
            this.init();
        }

        init() {
            this.resizeCanvas();
            window.addEventListener('resize', () => this.resizeCanvas());
            this.createParticles();
            this.animate();
        }

        resizeCanvas() {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }

        createParticles() {
            this.particles = [];
            for (let i = 0; i < 100; i++) {
                this.particles.push({
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    size: Math.random() * 3 + 1,
                    speedX: Math.random() * 2 - 1,
                    speedY: Math.random() * 2 - 1,
                    opacity: Math.random() * 0.5 + 0.2
                });
            }
        }

        animate() {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            
            this.particles.forEach(particle => {
                particle.x += particle.speedX;
                particle.y += particle.speedY;

                if (particle.x > this.canvas.width) particle.x = 0;
                if (particle.x < 0) particle.x = this.canvas.width;
                if (particle.y > this.canvas.height) particle.y = 0;
                if (particle.y < 0) particle.y = this.canvas.height;

                this.ctx.beginPath();
                this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                this.ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
                this.ctx.fill();
            });

            requestAnimationFrame(() => this.animate());
        }
    }

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', () => {
        new WeatherAnimationComponent();
    });
    </script>
    
    <style>
    #weather-particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    </style>
    """, height=0)

def main():
    # Initialize session state first
    initialize_session_state()
    
    # Set page config
    st.set_page_config(
        page_title="Ultimate Weather Dashboard",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject advanced features
    if st.session_state.user_preferences['animations']:
        inject_advanced_animations()
        weather_animations_component()
    inject_advanced_css()
    
    # App header with dynamic effects
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 class="weather-glow" style="font-size: 4rem; margin-bottom: 0.5rem;">🌤️ Ultimate Weather</h1>
        <p style="font-size: 1.2rem; opacity: 0.8;">Advanced Real-time Weather Monitoring System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize weather app
    api_key = "441c9cc77530b16acae5221e3485be0b"  # You can move this to secrets
    weather_app = AdvancedWeatherApp(api_key)
    
    # Create sidebar
    create_sidebar(weather_app)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        city_name = st.text_input("🏙️ Enter City Name", 
                                value=st.session_state.selected_city,
                                placeholder="e.g., London, New York, Tokyo...")
        
        if st.button("🔍 Search Weather", use_container_width=True):
            st.session_state.selected_city = city_name
            if city_name and city_name not in st.session_state.favorite_cities:
                st.session_state.favorite_cities.append(city_name)
    
    with col2:
        st.info("💡 **Pro Tip**: Use Ctrl+R to refresh or add cities to favorites!")
    
    if city_name:
        # Display loading with advanced animations
        with st.spinner("🛰️ Fetching satellite weather data..."):
            current_data = weather_app.get_current_weather(city_name)
        
        if current_data and current_data.get("cod") == 200:
            # Get weather type and corresponding video
            weather_type = current_data['weather'][0]['main'].lower()
            video_url = WeatherConfig.WEATHER_VIDEOS.get(weather_type, WeatherConfig.WEATHER_VIDEOS['default'])
            
            # Trigger JavaScript weather update with video
            st.components.v1.html(f"""
            <script>
                if (window.weatherAnimations) {{
                    window.weatherAnimations.setWeatherType('{weather_type}', '{video_url}');
                }}
                window.dispatchEvent(new CustomEvent('weatherUpdate', {{
                    detail: {{ 
                        weather: '{weather_type}',
                        videoUrl: '{video_url}'
                    }}
                }}));
            </script>
            """, height=0)
            
            # Display advanced weather cards
            display_advanced_weather(current_data, weather_app)
            
        else:
            error_msg = current_data.get('message', 'Unknown error') if current_data else 'API error'
            st.error(f"🚨 City not found or API error: {error_msg}. Please check the city name and try again.")

if __name__ == "__main__":
    main()