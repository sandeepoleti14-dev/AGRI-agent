"""
Prompts and multilingual instructions for the Grounded Agricultural Disease Agent.
Enforces strict grounding, zero-hallucination of chemicals/doses, and explicit uncertainty boundaries.
"""

from typing import Dict, Any, List

SYSTEM_PROMPT = """You are an expert Agricultural Plant Pathologist and Integrated Pest Management (IPM) specialist.
Your responsibility is to analyze crop leaf vision observations alongside authoritative RAG agricultural evidence from ICAR, IRRI, and state agricultural university manuals.

STRICT OPERATIONAL RULES:
1. EVIDENCE GROUNDING: You MUST base all diagnostic symptoms, cultural methods, organic remedies, and chemical recommendations SOLELY on the provided retrieved evidence.
2. ZERO PESTICIDE HALLUCINATION: Never invent, extrapolate, or recommend any chemical, pesticide, fungicide brand, or dosage not explicitly mentioned in the retrieved evidence chunks.
3. UNCERTAINTY & ADVISORY NOTICE: Always distinguish automated computer vision prediction from laboratory confirmation. Emphasize that visual diagnosis is a preliminary screening.
4. MANDATORY VERIFICATION: Always advise the farmer to consult local district agricultural extension officers (Krishi Vigyan Kendra / KVK) before purchasing or spraying any chemicals.
5. NO UNSUPPORTED CLAIMS: Never call any pesticide company or commercial brand 'top rated' or 'best' unless authentic evidence explicitly states so.
6. MULTILINGUAL FIDELITY: If the user requested language is other than English (such as Telugu or Hindi), provide symptoms, observations, organic management, and warnings in that language, while keeping chemical active ingredients recognizable.
"""

DISCLAIMER_TRANSLATIONS = {
    "English": "Vision prediction is an automated estimation and not a laboratory diagnosis. Verify with local agricultural extension officer or KVK before chemical application.",
    "Telugu": "దృష్టి విశ్లేషణ అనేది ఒక స్వయంచాలక అంచనా మాత్రమే, ఇది ప్రయోగశాల నిర్ధారణ కాదు. రసాయనాలు వాడే ముందు స్థానిక వ్యవసాయ విస్తరణ అధికారి (KVK) ని సంప్రదించండి.",
    "Hindi": "दृष्टि विश्लेषण एक स्वचालित अनुमान है और यह प्रयोगशाला निदान नहीं है। रासायनिक छिड़काव से पहले स्थानीय कृषि विस्तार अधिकारी (KVK) से परामर्श करें।",
    "Tamil": "காட்சி முன்னறிவிப்பு ஒரு தானியங்கி மதிப்பீடாகும்; ஆய்வக உறுதிப்படுத்தல் அல்ல. இரசாயனங்களைப் பயன்படுத்துவதற்கு முன் உள்ளூர் விவசாய விரிவாக்க அதிகாரி அல்லது KVK-ஐ அணுகவும்."
}

INSUFFICIENT_EVIDENCE_MESSAGES = {
    "English": "Insufficient evidence in the agricultural knowledge base.",
    "Telugu": "వ్యవసాయ సమాచార నిధిలో తగిన ఆధారాలు లభించలేదు.",
    "Hindi": "कृषि ज्ञानकोष में पर्याप्त साक्ष्य उपलब्ध नहीं हैं।",
    "Tamil": "விவசாய அறிவுக் களஞ்சியத்தில் போதுமான சான்றுகள் கிடைக்கவில்லை."
}


def build_disease_prompt(
    vision_result: Dict[str, Any],
    retrieved_evidence: List[Dict[str, Any]],
    crop: str = "paddy",
    language: str = "English"
) -> str:
    """
    Constructs a structured prompt for the Disease Agent combining vision output and retrieved evidence.
    """
    evidence_text = ""
    if not retrieved_evidence:
        evidence_text = "[No matching evidence found in knowledge base]"
    else:
        for i, item in enumerate(retrieved_evidence, 1):
            source = item.get("source", "Official Bulletin")
            score = item.get("score", 0.0)
            content = item.get("content", "").strip()
            evidence_text += f"\n--- Evidence Chunk {i} (Source: {source}, Relevance: {score}) ---\n{content}\n"

    observations_text = "\n".join(f"- {obs}" for obs in vision_result.get("observations", []))

    prompt = f"""
CROP: {crop}
LANGUAGE REQUESTED: {language}

VISION ANALYSIS:
- Possible Disease: {vision_result.get('possible_disease', 'uncertain')}
- Confidence: {vision_result.get('confidence', 0.0)}
- Visual Observations:
{observations_text}

RETRIEVED AUTHORITATIVE AGRICULTURAL EVIDENCE:
{evidence_text}

INSTRUCTIONS:
1. Cross-reference the visual observations with the retrieved agricultural evidence.
2. If evidence is insufficient, state "{INSUFFICIENT_EVIDENCE_MESSAGES.get(language, INSUFFICIENT_EVIDENCE_MESSAGES['English'])}".
3. Synthesize the validated symptoms, cultural prevention, organic/biological management, and chemical interventions.
4. Output strictly in the requested target language ({language}).
"""
    return prompt.strip()
