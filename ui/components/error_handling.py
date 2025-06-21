"""
Error handling utilities for the VroomSniffer UI.
"""
import streamlit as st
import traceback

def handle_error(func):
    """
    Decorator to handle exceptions in UI functions.
    
    Args:
        func: The function to decorate
        
    Returns:
        Wrapped function that catches and displays exceptions
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.error(f"❌ Error: {str(e)}")
                st.code(traceback.format_exc())
            else:
                st.error(f"❌ An error occurred: {str(e)}")
    return wrapper

def show_error(message, exception=None):
    """
    Display an error message with optional exception details.
    
    Args:
        message: Main error message to display
        exception: Optional exception object for details
    """
    st.error(f"❌ {message}")
    
    if exception and st.session_state.get('debug_mode', False):
        with st.expander("Error Details"):
            st.code(str(exception))
            st.code(traceback.format_exc())

def show_success(message):
    """Show a success message."""
    st.success(f"✅ {message}")

def show_info(message):
    """Show an info message."""
    st.info(f"ℹ️ {message}")

def show_warning(message):
    """Show a warning message."""
    st.warning(f"⚠️ {message}")

def confirm_action(message, callback, *args, **kwargs):
    """
    Create a confirmation button for a destructive action.
    
    Args:
        message: Confirmation message to display
        callback: Function to call when confirmed
        *args: Arguments to pass to the callback
        **kwargs: Keyword arguments to pass to the callback
        
    Returns:
        True if the action was confirmed and executed, False otherwise
    """
    # Generate a unique key for this confirmation
    import hashlib
    hash_input = message + str(callback.__name__) + str(args) + str(kwargs)
    confirm_key = f"confirm_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
    
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    
    if st.session_state[confirm_key]:
        # Second click (confirmed)
        st.session_state[confirm_key] = False  # Reset
        result = callback(*args, **kwargs)
        return True, result
    else:
        # First click
        if st.button(message):
            st.session_state[confirm_key] = True
            st.warning("⚠️ Click again to confirm")
            st.rerun()
    
    return False, None
