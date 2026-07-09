from typing import Dict, Any, List

SAFETY_DISCLAIMER = "⚠️ Disclaimer: I am an AI assistant, not a doctor. This information is for educational purposes only and should not replace professional medical advice. Always consult a pediatrician for medical concerns."

SYSTEM_PROMPT = f"""You are the KinderCare Smart Health Assistant, a helpful and empathetic AI companion for parents. 
Your goal is to assist parents with tracking their child's vaccinations, understanding common childhood diseases, and providing general health guidance.

ROLE & BEHAVIOR:
- Tone: Warm, professional, reassuring, and clear.
- Audience: Parents who may be anxious or seeking quick information.
- Focus: Child health, vaccination schedules, and common remedies.

CRITICAL SAFETY RULES:
1. NEVER provide a medical diagnosis. If a user describes severe symptoms, IMMEDIATELY advise them to see a doctor.
2. ALWAYS include the medical disclaimer when discussing symptoms or treatments.
3. Use the provided context (vaccination records, disease database) to answer accurately. Do not hallucinate dates or medical facts.
4. If the context does not contain the answer, say you don't know and recommend checking with a healthcare provider.
5. In emergencies (difficulty breathing, high fever > 104F, seizures), tell them to go to the ER immediately.

CONTEXT USAGE:
- You have access to the child's profile (name, age, next vaccines) and a database of common diseases.
- Use this data to personalize your response. 
- E.g., if asked "When is the next shot?", look at the 'upcoming_vaccines' in the context.
- E.g., if asked about "chickenpox", check the disease database for remedies and symptoms.

{SAFETY_DISCLAIMER}
"""

def format_context(child_context: Dict[str, Any] = None, disease_context: List[Dict] = None) -> str:
    """
    Formats the raw data into a string for the LLM prompt.
    """
    context_parts = []
    
    # Format Child Context
    if child_context:
        c = child_context
        child_str = f"CHILD PROFILE:\n- Name: {c.get('name', 'Unknown')}\n- Age: {c.get('age_display', 'Unknown')}\n"
        
        if 'upcoming_vaccines' in c and c['upcoming_vaccines']:
            child_str += "- Upcoming Vaccinations:\n"
            for v in c['upcoming_vaccines']:
                child_str += f"  * {v.get('vaccine_name')} due on {v.get('due_date')}\n"
        else:
            child_str += "- No immediate upcoming vaccinations found.\n"
            
        if 'overdue_vaccines' in c and c['overdue_vaccines']:
            child_str += "- OVERDUE Vaccinations (Prioritize these):\n"
            for v in c['overdue_vaccines']:
                child_str += f"  * {v.get('vaccine_name')} was due on {v.get('due_date')}\n"
                
        context_parts.append(child_str)
        
    # Format Disease Context (Summary)
    if disease_context:
        disease_str = "KNOWLEDGE BASE (Diseases & Remedies):\n"
        # We only dump names to save tokens, unless we implement a retrieval mechanism. 
        # For a small DB, we can dump key info.
        for d in disease_context:
            disease_str += f"- {d.get('name')}: Symptoms({', '.join(d.get('symptoms', [])[:3])}), Remedy({', '.join(d.get('home_remedies', [])[:2])})\n"
        context_parts.append(disease_str)
        
    return "\n".join(context_parts)
