"""
Prompt templates and instructions for getting structured outputs from LLM.
Use these along with your system and user prompts to get better formatted responses.
"""

# Base instruction for structured outputs
STRUCTURED_OUTPUT_INSTRUCTION = """
Please provide your response in a well-structured format. Follow these guidelines:

1. Use clear headings and subheadings
2. Break down complex information into bullet points or numbered lists
3. Use tables for comparing data or presenting structured information
4. Use code blocks for technical content, code examples, or commands
5. Use bold and italics appropriately for emphasis
6. Keep paragraphs concise and focused on single topics
7. Use emojis sparingly to enhance readability when appropriate

Format your response using Markdown syntax for better readability.
"""

# Specific instructions for different types of outputs

# For step-by-step instructions or tutorials
STEP_BY_STEP_INSTRUCTION = """
Please provide a step-by-step guide with the following format:

## Overview
[Brief description of what the user will accomplish]

## Prerequisites
[List any requirements or prerequisites]

## Steps
1. **Step 1 Title**: [Clear, actionable instruction]
   - [Additional details or context]
   - [Code example if applicable]

2. **Step 2 Title**: [Next instruction]
   - [Continue with clear, numbered steps]

## Tips & Best Practices
- [Helpful tips related to the process]

## Common Issues
- [Potential problems and solutions]
"""

# For comparisons or analysis
COMPARISON_INSTRUCTION = """
Please provide a detailed comparison using the following structure:

## Executive Summary
[Brief overview of the comparison]

## Comparison Table
| Feature/Aspect | Option 1 | Option 2 | Option 3 |
|----------------|----------|----------|----------|
| [Criteria 1]   | [Details] | [Details] | [Details] |
| [Criteria 2]   | [Details] | [Details] | [Details] |

## Detailed Analysis
### Option 1
- **Pros**: [Advantages]
- **Cons**: [Disadvantages]
- **Best for**: [Use cases]

### Option 2
- **Pros**: [Advantages]
- **Cons**: [Disadvantages]
- **Best for**: [Use cases]

## Recommendation
[Clear recommendation based on the analysis]
"""

# For code-related responses
CODE_INSTRUCTION = """
Please provide code-related responses with the following structure:

## Solution Approach
[Brief explanation of the approach]

## Code Implementation
```python
# Your well-commented code here
```

## Explanation
- [Line-by-line or section-by-section explanation]
- [Key concepts used]

## Usage Example
```python
# Example of how to use the code
```

## Common Errors
- [Potential issues and how to fix them]
"""

# For data analysis or explanations
DATA_ANALYSIS_INSTRUCTION = """
Please provide data analysis with the following structure:

## Key Findings
- [Main insights in bullet points]

## Detailed Analysis
### Metric 1: [Name]
- **Value**: [Specific value]
- **Interpretation**: [What this means]
- **Implications**: [Why it matters]

### Metric 2: [Name]
- **Value**: [Specific value]
- **Interpretation**: [What this means]
- **Implications**: [Why it matters]

## Visual Summary
[If applicable, suggest how to visualize the data]

## Recommendations
- [Actionable recommendations based on the analysis]
"""

# For troubleshooting or debugging
TROUBLESHOOTING_INSTRUCTION = """
Please provide troubleshooting help with this format:

## Problem Diagnosis
- **Symptoms**: [What you're observing]
- **Likely Causes**: [Most common causes]

## Solutions (in order of likelihood)
1. **Solution 1**: [Clear description]
   - **Steps**: [Numbered steps to implement]
   - **Verification**: [How to confirm it's fixed]

2. **Solution 2**: [Alternative approach]
   - **Steps**: [Numbered steps to implement]
   - **Verification**: [How to confirm it's fixed]

## Prevention Tips
- [How to avoid this issue in the future]
"""

# For learning or educational content
EDUCATIONAL_INSTRUCTION = """
Please provide educational content with this structure:

## Learning Objectives
- [What the user will be able to do after reading]

## Core Concepts
### Concept 1: [Name]
- **Definition**: [Clear explanation]
- **Example**: [Practical example]
- **Importance**: [Why it matters]

### Concept 2: [Name]
- **Definition**: [Clear explanation]
- **Example**: [Practical example]
- **Importance**: [Why it matters]

## Practical Application
[Real-world example or exercise]

## Key Takeaways
- [Main points to remember]
"""

# Function to get the appropriate instruction based on response type
def get_structured_prompt(response_type="general"):
    """
    Get the appropriate structured prompt instruction based on the type of response needed.
    
    Args:
        response_type (str): Type of structured response needed
            Options: "general", "steps", "comparison", "code", "data", "troubleshoot", "educational"
    
    Returns:
        str: The appropriate instruction string
    """
    instructions = {
        "general": STRUCTURED_OUTPUT_INSTRUCTION,
        "steps": STEP_BY_STEP_INSTRUCTION,
        "comparison": COMPARISON_INSTRUCTION,
        "code": CODE_INSTRUCTION,
        "data": DATA_ANALYSIS_INSTRUCTION,
        "troubleshoot": TROUBLESHOOTING_INSTRUCTION,
        "educational": EDUCATIONAL_INSTRUCTION
    }
    
    return instructions.get(response_type, STRUCTURED_OUTPUT_INSTRUCTION)

# Example usage functions
def combine_prompts(system_prompt, user_prompt, instruction_type="general"):
    """
    Combine system prompt, user prompt, and structured instruction.
    
    Args:
        system_prompt (str): The system prompt
        user_prompt (str): The user's question/request
        instruction_type (str): Type of structured output needed
    
    Returns:
        tuple: (combined_system_prompt, combined_user_prompt)
    """
    structured_instruction = get_structured_prompt(instruction_type)
    
    # Add structured instruction to system prompt
    enhanced_system_prompt = f"{system_prompt}\n\n{structured_instruction}"
    
    return enhanced_system_prompt, user_prompt

# Pre-built prompt combinations for common use cases
def get_step_by_step_prompt(user_request):
    """Get a complete prompt set for step-by-step instructions."""
    system_prompt = "You are a helpful assistant that provides clear, step-by-step instructions."
    return combine_prompts(system_prompt, user_request, "steps")

def get_code_help_prompt(user_request):
    """Get a complete prompt set for code-related help."""
    system_prompt = "You are an expert programmer that provides clean, well-commented code solutions."
    return combine_prompts(system_prompt, user_request, "code")

def get_comparison_prompt(user_request):
    """Get a complete prompt set for comparisons."""
    system_prompt = "You are an analytical assistant that provides detailed comparisons and recommendations."
    return combine_prompts(system_prompt, user_request, "comparison")

def get_troubleshooting_prompt(user_request):
    """Get a complete prompt set for troubleshooting."""
    system_prompt = "You are a technical support specialist that helps diagnose and solve problems."
    return combine_prompts(system_prompt, user_request, "troubleshoot")
