"""
Main Streamlit application for LLM Chat Interface
"""

import streamlit as st
from config import Config
from api_client import LLMClient
from ui_components import (
    render_sidebar, render_input_section, render_action_buttons,
    render_output_section, render_history_section, render_footer,
    show_error, show_success, show_info
)
from utils import initialize_session_state, clear_inputs, copy_to_clipboard, save_interaction_to_history, validate_inputs

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Configure page
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout=Config.LAYOUT,
        initial_sidebar_state=Config.SIDEBAR_STATE
    )
    
    # Page title
    st.title("🤖 LLM Chat Interface")
    st.markdown("---")
    
    # Initialize API client
    try:
        llm_client = LLMClient()
    except Exception as e:
        show_error(f"Failed to initialize API client: {str(e)}")
        return
    
    # Render sidebar configuration
    config = render_sidebar()
    
    # Create main columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Render input section
        system_prompt, user_prompt = render_input_section()
        
        # Render action buttons
        generate_clicked, clear_clicked, copy_clicked = render_action_buttons()
        
        # Handle button clicks
        if generate_clicked:
            handle_generate_response(
                llm_client, system_prompt, user_prompt, config
            )
        
        if clear_clicked:
            clear_inputs()
            show_info("Inputs cleared!")
        
        if copy_clicked:
            current_response = st.session_state.get('current_response')
            if current_response:
                copy_to_clipboard(current_response)
            else:
                show_info("No response to copy!")
    
    with col2:
        # Render output section
        render_output_section()
    
    # Render history section
    render_history_section()
    
    # Render footer
    render_footer()

def handle_generate_response(llm_client, system_prompt, user_prompt, config):
    """Handle the generate response button click"""
    # Validate inputs
    errors = validate_inputs(user_prompt, system_prompt)
    if errors:
        for error in errors:
            show_error(error)
        return
    
    try:
        # Show loading spinner
        with st.spinner(f"Calling {config['model']}..."):
            # Generate response
            interaction = llm_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=config['model'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                instruction_category=config['instruction_category'],
                custom_instructions=config['custom_instructions'],
                use_context=config['use_context']
            )
        
        # Save to history
        save_interaction_to_history(interaction)
        
        # Set current response
        st.session_state.current_response = interaction['response']
        
        # Show success message
        show_success("Response generated successfully!")
        
        # Rerun to update the UI
        st.rerun()
        
    except Exception as e:
        show_error(str(e))
        show_info("Please check your API key and try again.")

if __name__ == "__main__":
    main()
