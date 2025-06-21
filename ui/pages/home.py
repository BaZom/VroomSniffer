import streamlit as st
import sys
import os
import time
from pathlib import Path

# Add the parent directory to the path so we can import from local modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import services via the new services_provider
from providers.services_provider import get_storage_service
# Import UI components
from ui.components.metrics import display_metrics_row
from ui.components.navigation import create_navigation_cards
from ui.components.error_handling import handle_error

@handle_error
def show_home_page(all_old_path, latest_new_path):
    """Clean home page with simple design and clear navigation."""    
    st.title("VroomSniffer - Car Monitoring System")
    st.write("Monitor car listings with scraping, data management, and notifications")
    
    # Initialize the storage service
    storage_service = get_storage_service()
    
    # Simple metrics
    try:
        stats = storage_service.get_cache_stats(all_old_path)
        recent_listings = storage_service.load_cache(latest_new_path) if latest_new_path else {}
        
        # Prepare metrics data
        metrics_data = [
            {'label': 'Total Listings', 'value': stats["total_listings"]},
            {'label': 'Recent Additions', 'value': len(recent_listings) if recent_listings else 0},
        ]
        
        # Add cache size metric
        cache_size_mb = stats.get('cache_size_mb', 0)
        if cache_size_mb > 0:
            metrics_data.append({'label': 'Cache Size', 'value': f"{cache_size_mb} MB"})
        else:
            metrics_data.append({'label': 'Cache Size', 'value': "< 0.01 MB"})
        
        # Prepare the last column with update time info
        last_updated = "Never"
        if all_old_path and os.path.exists(all_old_path):
            modified_time = os.path.getmtime(all_old_path)
            hours_ago = int((time.time() - modified_time) / 3600)
            if hours_ago == 0:
                last_updated = "< 1 hour ago"
            elif hours_ago < 24:
                last_updated = f"{hours_ago}h ago"
            else:
                days_ago = hours_ago // 24
                last_updated = f"{days_ago}d ago"
        
        # Add the last column to metrics
        metrics_data.append({'label': 'Last Updated', 'value': last_updated})
        
        # Use the metrics component to display metrics
        display_metrics_row(metrics_data, 4)
        
        # Simple status message
        if stats["total_listings"] == 0:
            st.info("Getting Started: Use the Scraper to start collecting car listings!")
        else:
            st.success(f"You have {stats['total_listings']} cached listings ready to explore!")
            
    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")
    
    st.divider()
    
    # Simple navigation cards
    st.subheader("Quick Navigation")
    
    # Define navigation cards data
    cards_data = [
        {
            'title': 'Car Scraper',
            'description': 'Search & monitor car listings',
            'bullet_points': [
                'Manual scraping with URL inputs',
                'Real-time monitoring capabilities',
                'Telegram notifications'
            ],
            'target_page': '🔍 Scraper',
            'is_primary': True
        },
        {
            'title': 'Data Storage',
            'description': 'Analyze & manage your data',
            'bullet_points': [
                'Browse and search cached listings',
                'Advanced filtering and insights',
                'Cache management tools'
            ],
            'target_page': '📊 Data Storage',
            'is_primary': True
        },
        {
            'title': 'Playground',
            'description': 'Testing & experimentation',
            'bullet_points': [
                'Test scraping functionality',
                'Send test messages',
                'Debug and troubleshoot'
            ],
            'target_page': '🎮 Playground',
            'is_primary': False
        }
    ]
    
    # Create navigation cards
    create_navigation_cards(cards_data)
    
    # System status section
    col1, col2 = st.columns(2)
    
    with col2:
        st.subheader("System Status")
        if stats.get("total_listings", 0) > 0:
            st.write("Your current data:")
            st.write(f"• {stats['total_listings']} total listings cached")
            if recent_listings:
                st.write(f"• {len(recent_listings)} recent additions")
            else:
                st.write("• No recent additions")
        else:
            st.write("No data yet - start scraping!")

