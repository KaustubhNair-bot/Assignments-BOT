"""
UI components for the Streamlit application
"""

import streamlit as st
import json
from config import Config
from custom_instructions import get_instruction, get_all_categories

def render_sidebar():
    """Render the sidebar with configuration options"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        selected_model = st.selectbox(
            "Select Model", 
            Config.MODEL_OPTIONS, 
            index=Config.MODEL_OPTIONS.index(Config.DEFAULT_MODEL)
        )
        
        # Temperature slider
        temperature = st.slider(
            "Temperature", 
            min_value=Config.MIN_TEMPERATURE, 
            max_value=Config.MAX_TEMPERATURE, 
            value=Config.DEFAULT_TEMPERATURE, 
            step=Config.TEMPERATURE_STEP
        )
        
        # Max tokens
        max_tokens = st.number_input(
            "Max Tokens", 
            min_value=Config.MIN_TOKENS, 
            max_value=Config.MAX_TOKENS, 
            value=Config.DEFAULT_MAX_TOKENS, 
            step=Config.TOKEN_STEP
        )
        
        # Custom Instructions Section
        st.markdown("---")
        st.header("📋 Custom Instructions")
        
        # Instruction category selection
        instruction_categories = ["None"] + get_all_categories()
        selected_category = st.selectbox(
            "Formatting Style",
            instruction_categories,
            index=0,
            help="Select predefined formatting constraints for different use cases"
        )
        
        # Show preview of selected instructions
        if selected_category != "None":
            with st.expander(f"📝 {selected_category} Instructions Preview"):
                st.text(get_instruction(selected_category))
        
        # Additional custom instructions
        custom_instructions = st.text_area(
            "Additional Instructions",
            placeholder="Enter any additional formatting constraints or instructions...",
            height=100,
            help="Add any custom instructions beyond the predefined categories"
        )
        
        # Context awareness settings
        st.markdown("---")
        st.header("🧠 Conversation Context")
        
        use_context = st.checkbox(
            "Enable Conversation Memory",
            value=True,
            help="Include previous messages in conversation context for better continuity"
        )
        
        if use_context:
            st.info(f"📝 Context will include the last {Config.MAX_CONTEXT_MESSAGES} message exchanges")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation History", use_container_width=True):
            # Import here to avoid circular imports
            from utils import clear_conversation_context
            clear_conversation_context()
            st.success("Conversation history cleared!")
            st.rerun()
        
        return {
            'model': selected_model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'instruction_category': selected_category,
            'custom_instructions': custom_instructions,
            'use_context': use_context
        }

def render_input_section():
    """Render the input configuration section"""
    st.header("📝 Input Configuration")
    
    # System prompt
    system_prompt = st.text_area(
        "System Prompt",
        placeholder="Enter the system prompt that defines the AI's behavior and role...",
        height=150,
        help="This prompt sets the context and behavior for the AI model"
    )
    
    # User prompt
    user_prompt = st.text_area(
        "User Prompt",
        placeholder="Enter your question or request here...",
        height=200,
        help="This is your actual question or task for the AI"
    )
    
    return system_prompt, user_prompt

def render_action_buttons():
    """Render action buttons"""
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    generate_clicked = False
    clear_clicked = False
    copy_clicked = False
    
    with col_btn1:
        if st.button("🚀 Generate Response", type="primary", use_container_width=True):
            generate_clicked = True
    
    with col_btn2:
        if st.button("🗑️ Clear Inputs", use_container_width=True):
            clear_clicked = True
    
    with col_btn3:
        if st.button("📋 Copy Response", use_container_width=True):
            copy_clicked = True
    
    return generate_clicked, clear_clicked, copy_clicked

def render_output_section():
    """Render the output display section"""
    st.header("📤 Model Output")
    
    if 'current_response' in st.session_state:
        response_container = st.container()
        with response_container:
            st.subheader("Generated Response")
            
            # Format the response
            formatted_response = st.session_state.current_response
            
            # Display with formatting options
            display_format = st.radio(
                "Display Format:",
                ["Plain Text", "Markdown", "JSON"],
                horizontal=True
            )
            
            if display_format == "Plain Text":
                st.text_area("Response", value=formatted_response, height=300, disabled=True)
            elif display_format == "Markdown":
                st.markdown(formatted_response)
            else:  # JSON
                try:
                    # Try to parse as JSON for pretty formatting
                    if formatted_response.strip().startswith('{') or formatted_response.strip().startswith('['):
                        parsed = json.loads(formatted_response)
                        st.json(parsed)
                    else:
                        # If not valid JSON, wrap it
                        st.json({"response": formatted_response})
                except:
                    st.json({"response": formatted_response})
            
            # Response metadata
            with st.expander("📊 Response Metadata"):
                if 'history' in st.session_state and st.session_state.history:
                    last_interaction = st.session_state.history[-1]
                    st.write(f"**Model:** {last_interaction['model']}")
                    st.write(f"**Temperature:** {last_interaction['temperature']}")
                    st.write(f"**Max Tokens:** {last_interaction['max_tokens']}")
                    st.write(f"**Generated:** {last_interaction['timestamp']}")
                    if last_interaction.get('instruction_category') and last_interaction['instruction_category'] != 'None':
                        st.write(f"**Formatting Style:** {last_interaction['instruction_category']}")
    else:
        st.info("👈 Enter your prompts and click 'Generate Response' to see the output here.")

def render_history_section():
    """Render the conversation history section"""
    st.header("📚 Conversation History")
    
    if 'history' in st.session_state and st.session_state.history:
        for i, interaction in enumerate(reversed(st.session_state.history[-Config.MAX_HISTORY_DISPLAY:]), 1):
            with st.expander(f"Conversation {i} - {interaction['timestamp']}"):
                col_hist1, col_hist2 = st.columns(2)
                with col_hist1:
                    st.write("**System Prompt:**")
                    system_text = interaction['system_prompt']
                    if len(system_text) > Config.PREVIEW_LENGTH['system']:
                        system_text = system_text[:Config.PREVIEW_LENGTH['system']] + "..."
                    st.text(system_text)
                    
                    st.write("**User Prompt:**")
                    user_text = interaction['user_prompt']
                    if len(user_text) > Config.PREVIEW_LENGTH['user']:
                        user_text = user_text[:Config.PREVIEW_LENGTH['user']] + "..."
                    st.text(user_text)
                    
                with col_hist2:
                    st.write("**Response:**")
                    response_text = interaction['response']
                    if len(response_text) > Config.PREVIEW_LENGTH['response']:
                        response_text = response_text[:Config.PREVIEW_LENGTH['response']] + "..."
                    st.text(response_text)
                    
                    st.write(f"**Model:** {interaction['model']}")
                    st.write(f"**Temperature:** {interaction['temperature']}")
                    
                    if interaction.get('instruction_category') and interaction['instruction_category'] != 'None':
                        st.write(f"**Formatting:** {interaction['instruction_category']}")
    else:
        st.info("No conversation history yet. Start by generating your first response!")

def render_footer():
    """Render the application footer"""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🤖 LLM Chat Interface | Built with Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_error(message):
    """Display error message"""
    st.error(message)

def show_success(message):
    """Display success message"""
    st.success(message)

def show_info(message):
    """Display info message"""
    st.info(message)
