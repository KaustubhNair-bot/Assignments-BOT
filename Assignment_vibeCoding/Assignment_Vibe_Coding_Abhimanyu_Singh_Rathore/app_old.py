import streamlit as st
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
from custom_instructions import get_instruction, get_all_categories, combine_instructions

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

st.set_page_config(
    page_title="LLM Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 LLM Chat Interface")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection
    model_options = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    selected_model = st.selectbox("Select Model", model_options, index=0)
    
    # Temperature slider
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
    
    # Max tokens
    max_tokens = st.number_input("Max Tokens", min_value=1, max_value=4096, value=1000, step=50)
    
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

col1, col2 = st.columns([1, 1])

with col1:
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
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn1:
        if st.button("🚀 Generate Response", type="primary", use_container_width=True):
            if user_prompt:
                try:
                    # Combine system prompt with custom instructions
                    category = selected_category if selected_category != "None" else None
                    combined_system_prompt = combine_instructions(
                        system_prompt, 
                        category, 
                        custom_instructions
                    )
                    
                    # Prepare messages for the API
                    messages = []
                    
                    # Add combined system prompt if provided
                    if combined_system_prompt.strip():
                        messages.append({"role": "system", "content": combined_system_prompt})
                    
                    # Add user prompt
                    messages.append({"role": "user", "content": user_prompt})
                    
                    # Show loading spinner
                    with st.spinner(f"Calling {selected_model}..."):
                        # Make API call
                        response = client.chat.completions.create(
                            model=selected_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        
                        # Extract the response content
                        response_content = response.choices[0].message.content
                    
                    # Store the interaction in session state
                    if 'history' not in st.session_state:
                        st.session_state.history = []
                    
                    interaction = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'system_prompt': system_prompt,
                        'instruction_category': selected_category,
                        'custom_instructions': custom_instructions,
                        'user_prompt': user_prompt,
                        'model': selected_model,
                        'temperature': temperature,
                        'max_tokens': max_tokens,
                        'response': response_content
                    }
                    st.session_state.history.append(interaction)
                    st.session_state.current_response = response_content
                    st.success("Response generated successfully!")
                    
                except Exception as e:
                    st.error(f"Error calling LLM API: {str(e)}")
                    st.info("Please check your API key and try again.")
            else:
                st.error("Please enter a user prompt!")
    
    with col_btn2:
        if st.button("🗑️ Clear Inputs", use_container_width=True):
            st.session_state.system_prompt = ""
            st.session_state.user_prompt = ""
            st.rerun()
    
    with col_btn3:
        if st.button("📋 Copy Response", use_container_width=True):
            if 'current_response' in st.session_state:
                st.write("Response copied to clipboard!")
                st.code(st.session_state.current_response)

with col2:
    st.header("📤 Model Output")
    
    # Output display area
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
                st.text(formatted_response, height=300)
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
    else:
        st.info("👈 Enter your prompts and click 'Generate Response' to see the output here.")

# History section at the bottom
st.markdown("---")
st.header("📚 Conversation History")

if 'history' in st.session_state and st.session_state.history:
    for i, interaction in enumerate(reversed(st.session_state.history[-5:]), 1):
        with st.expander(f"Conversation {i} - {interaction['timestamp']}"):
            col_hist1, col_hist2 = st.columns(2)
            with col_hist1:
                st.write("**System Prompt:**")
                st.text(interaction['system_prompt'][:200] + "..." if len(interaction['system_prompt']) > 200 else interaction['system_prompt'])
                st.write("**User Prompt:**")
                st.text(interaction['user_prompt'][:200] + "..." if len(interaction['user_prompt']) > 200 else interaction['user_prompt'])
            with col_hist2:
                st.write("**Response:**")
                st.text(interaction['response'][:300] + "..." if len(interaction['response']) > 300 else interaction['response'])
                st.write(f"**Model:** {interaction['model']}")
else:
    st.info("No conversation history yet. Start by generating your first response!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🤖 LLM Chat Interface | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
