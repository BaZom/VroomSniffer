"""
Navigation components for the VroomSniffer UI.
"""
import streamlit as st
from ui.components.state_management import navigate_to

def create_navigation_card(title, description, bullet_points, target_page, is_primary=True):
    """
    Create a navigation card with title, description, and bullet points.
    
    Args:
        title: Card title
        description: Short description text
        bullet_points: List of bullet points to display
        target_page: Page to navigate to on button click
        is_primary: Whether to use primary button styling
    """
    st.subheader(title)
    st.write(description)
    
    # Display bullet points
    for point in bullet_points:
        st.write(f"• {point}")
    
    # Navigation button
    button_type = "primary" if is_primary else "secondary"
    if st.button(f"Go to {title}", type=button_type, use_container_width=True):
        navigate_to(target_page)

def create_navigation_cards(cards_data):
    """
    Create multiple navigation cards in a row layout.
    
    Args:
        cards_data: List of dictionaries with keys: title, description, 
                   bullet_points, target_page, and optional is_primary
    """
    # Determine layout
    cols_per_row = 2
    num_cards = len(cards_data)
    num_rows = (num_cards + cols_per_row - 1) // cols_per_row  # Ceiling division
    
    for row in range(num_rows):
        # Create columns for this row
        start_idx = row * cols_per_row
        end_idx = min(start_idx + cols_per_row, num_cards)
        cols = st.columns(end_idx - start_idx)
        
        # Fill the columns with cards
        for i, idx in enumerate(range(start_idx, end_idx)):
            with cols[i]:
                card = cards_data[idx]
                create_navigation_card(
                    card['title'],
                    card['description'],
                    card['bullet_points'],
                    card['target_page'],
                    card.get('is_primary', True)
                )
