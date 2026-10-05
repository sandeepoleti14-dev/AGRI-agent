"""
Prompts and multilingual instructions for the Grounded Agricultural Disease Agent.
Enforces strict grounding, zero-hallucination of chemicals/doses, and explicit uncertainty boundaries.
"""

from typing import Dict, Any, List

SYSTEM_PROMPT = """You are an expert Agricultural Plant Pathologist and Integrated Pest Management (IPM) specialist.
Your responsibility is to analyze the available crop observations alongside authoritative RAG agricultural evidence from ICAR, IRRI, and state agricultural university manuals.

STRICT OPERATIONAL RULES:
1. EVIDENCE GROUNDING: You MUST base all diagnostic symptoms, cultural methods, organic remedies, and chemical recommendations SOLELY on the provided retrieved evidence.
2. ZERO PESTICIDE HALLUCINATION: Never invent, extrapolate, or recommend any chemical, pesticide, fungicide brand, or dosage not explicitly mentioned in the retrieved evidence chunks.
3. UNCERTAINTY & ADVISORY NOTICE: Distinguish farmer-reported symptoms from computer-vision observations. Never claim that an image was classified if the vision result is unavailable. Any visual diagnosis is preliminary, not laboratory confirmation.
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
            source = item.get("source") or "Not available"
            score = item.get("score")
            content = item.get("content", "").strip()
            relevance = score if score is not None else "Not available"
            evidence_text += f"\n--- Evidence Chunk {i} (Source: {source}, Relevance: {relevance}) ---\n{content}\n"

    observations_text = "\n".join(f"- {obs}" for obs in vision_result.get("observations", []))
    input_mode = vision_result.get("input_mode", "image")
    if input_mode == "text":
        analysis_label = "FARMER-REPORTED SYMPTOMS (NO IMAGE PROVIDED)"
        confidence_text = "Not available; do not invent a confidence score."
        mode_instruction = (
            "Analyze only the farmer-reported symptoms and retrieved evidence. "
            "Do not claim visual observations. Set confidence to null."
        )
    elif input_mode == "image_and_text":
        analysis_label = "IMAGE RESULT AND FARMER-REPORTED SYMPTOMS"
        confidence_text = vision_result.get("confidence")
        mode_instruction = (
            "Keep image observations separate from farmer-reported symptoms. "
            "If no vision prediction or score is available, do not invent one; set confidence to null."
        )
    else:
        analysis_label = "VISION ANALYSIS"
        confidence_text = vision_result.get("confidence")
        mode_instruction = (
            "If no vision prediction or score is available, do not infer a disease from image quality or filename; "
            "state uncertainty and set confidence to null."
        )

    prompt = f"""
CROP: {crop}
LANGUAGE REQUESTED: {language}

{analysis_label}:
- Possible Disease: {vision_result.get('possible_disease', 'uncertain')}
- Confidence: {confidence_text}
- Observations:
{observations_text}

RETRIEVED AUTHORITATIVE AGRICULTURAL EVIDENCE:
{evidence_text}

INSTRUCTIONS:
1. {mode_instruction}
2. Cross-reference the available observations with the retrieved agricultural evidence.
3. If evidence is insufficient, state "{INSUFFICIENT_EVIDENCE_MESSAGES.get(language, INSUFFICIENT_EVIDENCE_MESSAGES['English'])}".
4. Synthesize only validated symptoms, cultural prevention, organic/biological management, and chemical interventions.
5. Output strictly in the requested target language ({language}).
"""
    return prompt.strip()
