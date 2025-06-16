"""
Reusable metrics components for the VroomSniffer UI.
"""
import streamlit as st

def display_metrics_row(metrics_data, num_columns=4):
    """
    Display a row of metrics in columns
    
    Args:
        metrics_data: List of dicts with 'label' and 'value' keys
        num_columns: Number of columns to split into
    """
    columns = st.columns(num_columns)
    
    # Fill columns with metrics
    for i, metric_info in enumerate(metrics_data):
        with columns[i % num_columns]:
            label = metric_info.get('label', '')
            value = metric_info.get('value', '')
            delta = metric_info.get('delta', None)
            
            if delta is not None:
                st.metric(label, value, delta)
            else:
                st.metric(label, value)
                
    # Return any unfilled columns
    return columns[len(metrics_data) % num_columns:]

def display_system_stats(stats, total_runs=None):
    """
    Display system stats consistently across pages
    
    Args:
        stats: Dictionary with stats data
        total_runs: Optional total runs counter
    """
    metrics = []
    
    # Add total listings
    if 'total_listings' in stats:
        metrics.append({'label': 'Total Listings', 'value': stats['total_listings']})
    
    # Add recent additions if available
    if 'recent_additions' in stats:
        metrics.append({'label': 'Recent Additions', 'value': stats['recent_additions']})
    
    # Add cache size
    if 'cache_size_mb' in stats:
        cache_size_mb = stats['cache_size_mb']
        if cache_size_mb > 0:
            metrics.append({'label': 'Cache Size', 'value': f"{cache_size_mb} MB"})
        else:
            metrics.append({'label': 'Cache Size', 'value': "< 0.01 MB"})
    
    # Add total runs if available
    if total_runs is not None:
        metrics.append({'label': 'Total Runs', 'value': total_runs})
    
    # Display the metrics row
    return display_metrics_row(metrics)
