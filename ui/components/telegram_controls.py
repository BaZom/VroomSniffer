"""
Telegram notification components for the VroomSniffer UI.
"""
import streamlit as st

def send_listings_to_telegram(notification_service, listings, progress_container=None, source_description=None):
    """
    Send listings to Telegram using NotificationService.
    
    Args:
        notification_service: Instance of NotificationService
        listings: List of listings to send
        progress_container: Optional Streamlit container for progress display
        source_description: Optional description of the source URL
        
    Returns:
        int: Number of successfully sent messages
    """
    success_count = 0
    
    try:
        # Create progress bar and status message
        if len(listings) > 1:
            if progress_container:
                # Use the provided container
                progress_bar = progress_container.progress(0, text="Preparing to send messages...")
                status_text = st.empty()
            else:
                # Create new progress indicators
                progress_bar = st.progress(0, text="Preparing to send messages...")
                status_text = st.empty()
            
            # Create a source info message if provided
            if source_description:
                st.info(f"📍 Source: {source_description}")
            
            # Set up batching information
            batch_size = min(15, len(listings))
            total_batches = -(-len(listings) // batch_size)  # Ceiling division
            
            # Define a custom callback to update the UI on progress
            def progress_callback(sent, total, batch_num=None):
                progress = sent / total
                progress_bar.progress(progress)
                
                if batch_num is not None:
                    status_message = f"📤 Batch {batch_num}/{total_batches}: {sent}/{total} messages sent..."
                    status_text.text(status_message)
                    # Update the progress bar text too for better visibility
                    progress_bar.progress(progress, text=f"Sending: {sent}/{total} messages")
                else:
                    status_message = f"📤 Sending messages: {sent}/{total} complete..."
                    status_text.text(status_message)
                    # Update the progress bar text too
                    progress_bar.progress(progress, text=f"Sending: {sent}/{total} messages")
            
            # Call the notification service with our progress callback
            success_count, failed = notification_service.manual_send_listings(
                listings,
                parse_mode="HTML",
                retry_on_network_error=True,
                progress_callback=progress_callback
            )
            
            # Update UI with final status
            if success_count > 0:
                progress_bar.progress(1.0)
                status_text.success(f"✅ Sent {success_count}/{len(listings)} listings to Telegram")
            
            if failed:
                st.error(f"❌ Failed to send {len(failed)} listings")
        else:
            # Simple case for a single listing
            success = notification_service.send_listing(listings[0])
            success_count = 1 if success else 0
            
            if success:
                st.success("✅ Message sent successfully to Telegram")
            else:
                st.error("❌ Failed to send message to Telegram")
            
    except Exception as e:
        st.error(f"❌ Telegram sending failed: {str(e)}")
        
    return success_count

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
