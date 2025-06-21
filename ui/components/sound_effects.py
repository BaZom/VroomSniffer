"""
Sound effect utilities for the VroomSniffer UI.
"""
import streamlit as st
import base64
import time
from pathlib import Path

def play_sound(sound_file):
    """
    Play a sound effect using Streamlit's audio component.
    
    Args:
        sound_file: Filename of the sound file in the sounds directory
    """
    try:
        # Check if sound effects are enabled
        if not st.session_state.get('sound_effects_enabled', True):
            return
            
        sound_path = Path(__file__).parent.parent / "resources" / "sounds" / sound_file
        if sound_path.exists():
            with open(sound_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            
            # Use hidden HTML audio for background sound effects
            audio_base64 = base64.b64encode(audio_bytes).decode()
            audio_format = "audio/wav" if sound_file.endswith('.wav') else "audio/mpeg"
            
            # Multiple HTML approaches for better browser compatibility
            audio_html = f"""
            <script>
                // Try multiple methods to play audio
                try {{
                    // Method 1: Create and play audio element
                    var audio = new Audio('data:{audio_format};base64,{audio_base64}');
                    audio.volume = 0.5;
                    audio.play().catch(function(e) {{
                        console.log('Audio play failed:', e);
                    }});
                }} catch(e) {{
                    console.log('Audio creation failed:', e);
                }}
            </script>
            <audio controls autoplay style="display:none;">
                <source src="data:{audio_format};base64,{audio_base64}" type="{audio_format}">
            </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
            
            # Add delay to let sound complete before continuing
            time.sleep(2.5)  # Allow 2.5 seconds for sound to play completely
            
    except Exception as e:
        # Show error in debug mode
        if st.session_state.get('debug_mode', False):
            st.error(f"Sound playback error: {e}")
        pass
