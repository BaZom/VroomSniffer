import streamlit as st
from notifier.telegram import send_telegram_message, format_car_listing_message
from services.caralyze_service import manual_send_listings

def manual_send_listings_ui(listings):
    """Send listings manually to Telegram, logging failed messages with errors and retrying once if network error occurs."""
    if not listings:
        st.warning("No listings to send")
        return
    with st.spinner(f"Sending {len(listings)} listings..."):
        success_count, failed = manual_send_listings(
            listings,
            send_telegram_message=send_telegram_message,
            format_car_listing_message=format_car_listing_message,
            parse_mode="HTML",
            retry_on_network_error=True
        )
        if success_count > 0:
            st.success(f"✅ Sent {success_count}/{len(listings)} listings!")
        if failed:
            st.error(f"❌ Failed to send {len(failed)} listings!")
            for f in failed:
                st.write(f"Listing #{f['index']} - {f['title']}")
                st.code(f["error"], language="text")
        elif success_count == 0:
            st.error("❌ Failed to send listings")

def telegram_test_button():
    if st.button("🧪 Test", use_container_width=True):
        success, error = send_telegram_message("🚗 Test from CarAlyze!", parse_mode="HTML")
        if success:
            st.success("✅ Connected!")
        else:
            st.error(f"❌ Connection failed!\n{error}")
