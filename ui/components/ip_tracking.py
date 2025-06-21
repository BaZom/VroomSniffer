"""
IP Tracking display component for the VroomSniffer UI.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import json

def display_ip_tracking():
    """
    Display IP tracking information in the UI.
    
    Shows a table of tracked URLs and the IPs used to access them.
    """
    st.subheader("IP Tracking")
    
    # Path to IP tracking file
    ip_tracking_path = Path(__file__).parent.parent.parent / "storage" / "ip_tracking.json"
    
    if not ip_tracking_path.exists():
        st.info("No IP tracking data available yet. Run scrapes to start collecting IP data.")
        return
    
    try:
        # Load the IP tracking data
        with open(ip_tracking_path, "r", encoding="utf-8") as f:
            tracking_data = json.load(f)
        
        if not tracking_data.get("url_ip_mapping"):
            st.info("No IP tracking data available yet. Run scrapes to start collecting IP data.")
            return
        
        st.write(f"Last Updated: {tracking_data.get('last_updated', 'Unknown')}")
        st.write(f"URLs Tracked: {len(tracking_data.get('url_ip_mapping', {}))}")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["URL View", "IP Summary"])
        
        with tab1:
            # URL-centric view
            for url, ip_entries in tracking_data.get("url_ip_mapping", {}).items():
                with st.expander(f"{url}"):
                    # Create two columns for direct and proxy IPs
                    col1, col2 = st.columns(2)
                    
                    # Filter entries by type
                    direct_ips = [entry for entry in ip_entries if not entry.get("is_proxy")]
                    proxy_ips = [entry for entry in ip_entries if entry.get("is_proxy")]
                    
                    with col1:
                        st.write("**Direct IPs:**")
                        if direct_ips:
                            df_direct = pd.DataFrame(direct_ips)
                            st.dataframe(df_direct, hide_index=True)
                        else:
                            st.write("No direct IPs recorded")
                    
                    with col2:
                        st.write("**Proxy IPs:**")
                        if proxy_ips:
                            df_proxy = pd.DataFrame(proxy_ips)
                            st.dataframe(df_proxy, hide_index=True)
                        else:
                            st.write("No proxy IPs recorded")
        
        with tab2:
            # IP summary view - show unique IPs and how many URLs they were used for
            all_ips = {}
            
            for url, ip_entries in tracking_data.get("url_ip_mapping", {}).items():
                for entry in ip_entries:
                    ip = entry.get("ip")
                    is_proxy = entry.get("is_proxy")
                    
                    if ip not in all_ips:
                        all_ips[ip] = {
                            "ip": ip,
                            "is_proxy": is_proxy,
                            "urls": [url],
                            "total_uses": entry.get("use_count", 1)
                        }
                    else:
                        all_ips[ip]["urls"].append(url)
                        all_ips[ip]["total_uses"] += entry.get("use_count", 1)
            
            # Convert to list for DataFrame
            ip_summary_list = list(all_ips.values())
            for item in ip_summary_list:
                item["url_count"] = len(set(item["urls"]))  # Count unique URLs
                item["urls"] = ", ".join(set(item["urls"]))  # Convert to string
            
            if ip_summary_list:
                df_summary = pd.DataFrame(ip_summary_list)
                st.dataframe(df_summary, hide_index=True)
            else:
                st.write("No IP data available")
                
    except json.JSONDecodeError:
        st.error("IP tracking file is corrupted or empty.")
    except Exception as e:
        st.error(f"Failed to display IP tracking information: {str(e)}")
