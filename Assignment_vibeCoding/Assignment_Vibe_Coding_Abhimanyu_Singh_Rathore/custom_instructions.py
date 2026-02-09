"""
Custom Instructions and Formatting Constraints for LLM Models
This file contains predefined instructions for different use cases and formatting requirements.
"""

# General formatting constraints
GENERAL_FORMATTING = """
Response Formatting Guidelines:
- Use clear, well-structured paragraphs
- Include relevant headings and subheadings when appropriate
- Use bullet points or numbered lists for clarity
- Maintain professional and concise language
- Avoid excessive jargon unless specifically requested
- Ensure responses are grammatically correct and well-edited
"""

# Code-related constraints
CODE_FORMATTING = """
Code Response Guidelines:
- Provide code in proper fenced code blocks with language specification
- Include comments for complex logic
- Follow best practices and naming conventions
- Provide brief explanation of the code approach
- Include error handling where applicable
- Test the code logic before presenting
"""

# Technical documentation constraints
TECHNICAL_DOCS = """
Technical Documentation Guidelines:
- Use structured format with clear sections (Overview, Implementation, Examples, etc.)
- Include step-by-step procedures
- Provide code examples with explanations
- Use consistent terminology
- Include prerequisites and requirements
- Add troubleshooting tips when relevant
"""

# Creative writing constraints
CREATIVE_WRITING = """
Creative Writing Guidelines:
- Maintain consistent tone and style
- Use descriptive language and imagery
- Develop clear narrative structure
- Create engaging dialogue when applicable
- Show, don't just tell - use vivid descriptions
- Consider the target audience and purpose
"""

# Business communication constraints
BUSINESS_COMMUNICATION = """
Business Communication Guidelines:
- Use professional and formal tone
- Be concise and to the point
- Structure with clear purpose statement
- Include actionable items or next steps
- Use appropriate business terminology
- Consider cultural sensitivity in communication
"""

# Educational content constraints
EDUCATIONAL_CONTENT = """
Educational Content Guidelines:
- Structure content with learning objectives
- Use progressive complexity (simple to complex)
- Include examples and analogies for better understanding
- Provide practice exercises or questions
- Summarize key takeaways
- Consider different learning styles
"""

# Data analysis constraints
DATA_ANALYSIS = """
Data Analysis Guidelines:
- Present data in clear, readable format
- Use appropriate visualizations (charts, graphs)
- Explain methodology and assumptions
- Provide statistical context and significance
- Include limitations and caveats
- Suggest actionable insights based on findings
"""

# Research and academic constraints
RESEARCH_ACADEMIC = """
Research and Academic Guidelines:
- Use formal academic language
- Cite sources and provide references
- Maintain objective and unbiased tone
- Structure with clear thesis and supporting arguments
- Include methodology and limitations
- Follow academic formatting standards (APA, MLA, etc.)
"""

# Customer support constraints
CUSTOMER_SUPPORT = """
Customer Support Guidelines:
- Use empathetic and patient tone
- Provide clear, step-by-step solutions
- Anticipate follow-up questions
- Include alternative solutions when possible
- Use simple, non-technical language when appropriate
- Ensure responses are helpful and actionable
"""

# Marketing content constraints
MARKETING_CONTENT = """
Marketing Content Guidelines:
- Use persuasive and engaging language
- Focus on benefits and value propositions
- Include clear call-to-actions
- Use brand-appropriate tone and voice
- Consider target audience preferences
- Ensure compliance with advertising standards
"""

# Dictionary of instruction categories
INSTRUCTION_CATEGORIES = {
    "General": GENERAL_FORMATTING,
    "Code": CODE_FORMATTING,
    "Technical Documentation": TECHNICAL_DOCS,
    "Creative Writing": CREATIVE_WRITING,
    "Business Communication": BUSINESS_COMMUNICATION,
    "Educational Content": EDUCATIONAL_CONTENT,
    "Data Analysis": DATA_ANALYSIS,
    "Research & Academic": RESEARCH_ACADEMIC,
    "Customer Support": CUSTOMER_SUPPORT,
    "Marketing Content": MARKETING_CONTENT
}

def get_instruction(category):
    """
    Get instruction by category name
    
    Args:
        category (str): The category of instructions
        
    Returns:
        str: The instruction text for the category
    """
    return INSTRUCTION_CATEGORIES.get(category, GENERAL_FORMATTING)

def get_all_categories():
    """
    Get list of all available instruction categories
    
    Returns:
        list: List of category names
    """
    return list(INSTRUCTION_CATEGORIES.keys())

def combine_instructions(system_prompt, instruction_category=None, custom_instructions=""):
    """
    Combine system prompt with selected formatting instructions
    
    Args:
        system_prompt (str): The main system prompt
        instruction_category (str): Category of formatting instructions
        custom_instructions (str): Additional custom instructions
        
    Returns:
        str: Combined system instructions
    """
    combined = system_prompt
    
    if instruction_category and instruction_category in INSTRUCTION_CATEGORIES:
        combined += "\n\n" + INSTRUCTION_CATEGORIES[instruction_category]
    
    if custom_instructions.strip():
        combined += "\n\n" + custom_instructions.strip()
    
    return combined
