"""
Telegram notification components for the VroomSniffer UI.
"""
import streamlit as st

def send_listings_to_telegram(notification_service, listings):
    """
    Send listings to Telegram using NotificationService.
    
    Args:
        notification_service: Instance of NotificationService
        listings: List of listings to send
    """
    try:
        success_count, failed = notification_service.manual_send_listings(
            listings,
            parse_mode="HTML",
            retry_on_network_error=True
        )
        
        if success_count > 0:
            st.success(f"Sent {success_count}/{len(listings)} listings to Telegram")
        
        if failed:
            st.error(f"Failed to send {len(failed)} listings")
            
    except Exception as e:
        st.error(f"Telegram sending failed: {str(e)}")

def telegram_test_button(notification_service):
    """
    Clean Telegram test button using the NotificationService.
    
    Args:
        notification_service: Instance of NotificationService
    """
    if st.button("Test Connection", use_container_width=True, 
                help="Test your Telegram bot connection"):
        with st.spinner("Testing connection..."):
            import time
            time.sleep(0.5)
            
            success, error = notification_service.send_telegram_message(
                "Test from VroomSniffer! Connection successful!", 
                parse_mode="HTML"
            )
            
            if success:
                st.success("Connected! Telegram bot is working perfectly.")
            else:
                st.error(f"Connection failed: {error}")
