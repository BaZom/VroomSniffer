import streamlit as st
import pandas as pd
from services.caralyze_service import show_statistics

def show_statistics_ui(listings_data, show_trend=True):
    """Display statistics and optionally a price trend chart."""
    avg_price, count, prices = show_statistics(listings_data)
    if show_trend and prices:
        st.metric("Average Price", f"€{avg_price:,}")
        st.metric("Total Listings", f"{len(listings_data)}")
        chart_data = pd.DataFrame({"index": range(len(prices)), "price": prices})
        st.line_chart(chart_data.set_index("index"))
    return avg_price, count

def display_results(new_listings, all_listings, manual_send_callback):
    """Display monitoring results in organized sections."""
    st.header("📊 Results")
    col_summary1, col_summary2 = st.columns(2)
    with col_summary1:
        st.metric("🆕 New Listings", len(new_listings))
    with col_summary2:
        st.metric("📋 Total Listings", len(all_listings))
    if new_listings:
        st.subheader("🆕 New Listings")
        avg_new, _ = show_statistics_ui(new_listings, show_trend=False)
        st.info(f"Average price: €{avg_new:,}")
        df_new = pd.DataFrame(new_listings)
        df_new.insert(0, 'No.', range(1, len(df_new) + 1))
        st.dataframe(df_new, hide_index=True, use_container_width=True)
        if st.button("📤 Send New Listings Manually", type="primary"):
            manual_send_callback(new_listings)
    else:
        st.info("No new listings found")
    if all_listings:
        with st.expander("📋 All Listings & Analytics", expanded=False):
            show_statistics_ui(all_listings, show_trend=True)
            df_all = pd.DataFrame(all_listings)
            df_all.insert(0, 'No.', range(1, len(df_all) + 1))
            st.dataframe(df_all, hide_index=True, use_container_width=True)
