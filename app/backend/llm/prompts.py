#Centralized Prompt Templates for LLM Clients

from typing import Dict

#template for highlighting user-selected skills
SKILL_HIGHLIGHT_TEMPLATE: str = (
    "\n\nCRITICAL: The user has explicitly requested to highlight the following "
    "technical skills: {skills}. You must look for evidence of these "
    "in the provided code topics and emphasize them in the summary. Do not mention the topic id explicitly, only cover the content they represent."
)

#prompt dictionary organized by summary type
#now only online 
PROMPTS: Dict[str, Dict[str, str]] = {
    "short": {
        "description": "Generate a concise 2-3 bullet point summary",
        "prompt": """Using the data provided, generate a concise LinkedIn-style summary as a bullet-point list (2-3 points).
• Start with one line summarizing the work's goal and overall outcome (if multiple projects are present, provide a high-level overview).
• Highlight the most significant achievement(s): what was done, which technologies/tools were used, and what measurable results or improvements were achieved.
• Optionally include key skills developed or strengthened through this work.

Use action-oriented, professional language that is easy to scan. No extra text, greetings, or emojis."""
    },
    
    "standard": {
        "description": "Generate a standard 4-5 bullet point summary",
        "prompt": """Using the data provided, generate a LinkedIn-ready professional summary as a bullet-point list (4-5 points).
• First bullet: provide a clear, concise overview of the work's purpose and scope (if multiple projects are present, summarize the breadth of work).
• Subsequent bullets: highlight specific contributions (what was done), skills applied, and technologies/tools used — frame each as an accomplishment (not just a responsibility) and, where possible, quantify outcomes.
• Final bullet: describe the key professional and technical skills gained through this work, emphasizing development and growth.

Use strong action verbs (e.g., "developed", "optimized", "designed"), maintain an active and confident tone, and tailor the language for LinkedIn. Avoid redundancy; keep each bullet impactful and easy to scan. Do not include greetings, emojis, extraneous text, or anything outside the bullet list."""
    },
    
    "long": {
        "description": "Generate a comprehensive 5-7 bullet point summary",
        "prompt": """Using the data provided, generate a comprehensive LinkedIn-ready professional summary as a bullet-point list (5-7 points).
• First bullet: succinct overview of the work's objectives, context, and impact (if multiple projects are present, provide a cohesive narrative).
• Middle bullets (3-4): detailed accomplishments — each bullet should state what was done using strong action verbs, the tools/technologies/methodologies applied, and the outcomes or benefits achieved (ideally quantified).
• Next bullet: highlight collaboration, leadership, cross-functional aspects, or how meaningful challenges were overcome.
• Final bullet: describe the advanced skills gained or deepened through this work (both technical and professional).

Maintain an active, confident, growth-oriented tone, tailor for LinkedIn, avoid redundancy, keep bullets crisp and skimmable. Do not include introductory or closing text, salutations, or emojis."""
    }
}


LOCAL_PROMPT: str = (
    "Write a resume-style summary using the provided keywords. Output 4-5 bullet points.\n"
    "Rules:\n"
    "- Start each bullet with an action verb.\n"
    "- Make each bullet an achievement or impact.\n"
    "- Keep bullets short and professional.\n"
    "- Do not describe the keywords; turn them into accomplishments.\n"
    "- Do not invent numbers ; only use what is implied by the keywords."
)


def get_prompt(summary_type: str = "standard", llm_type: str = "online") -> str:
    """
    Retrieve a prompt template by summary type and LLM type.
    """
    #local LLM uses a single prompt regardless of summary type
    if llm_type == "local":
        return LOCAL_PROMPT
    
    if summary_type not in PROMPTS:
        valid_types = list(PROMPTS.keys())
        raise KeyError(f"Unknown summary type '{summary_type}'. Valid types: {valid_types}")
    return PROMPTS[summary_type]["prompt"]


def format_skill_highlight(skills: list) -> str:
    """
    Format the skill highlighting instruction with the given skills.
    """
    if not skills:
        return ""
    return SKILL_HIGHLIGHT_TEMPLATE.format(skills=", ".join(skills))
