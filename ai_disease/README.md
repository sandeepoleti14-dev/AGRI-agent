# AgriAgent — Part 2: RAG + Vision Module (`ai_disease`)

An independent, evidence-backed crop disease diagnosis and management module built for farmer assistants.

Given a crop photograph (or symptom query), this module performs vision analysis, retrieves verified agricultural guidelines from an offline-capable ChromaDB vector database, and synthesizes evidence-grounded recommendations without hallucinating pesticide brands or dosages.

---

## Architecture Pipeline

```
           Image / Symptom Query
                     ↓
              VISION ANALYSIS
        (disease_vision.py + PIL / API)
                     ↓
       Possible Disease + Confidence + Observations
                     ↓
               RAG RETRIEVAL
          (ChromaDB collection:
         paddy_disease_knowledge)
                     ↓
        Relevant Agricultural Evidence
    (Symptoms, Cultural, Organic, Chemical)
                     ↓
               DISEASE AGENT
        (disease_agent.py + Grounded
           Multilingual Reasoning)
                     ↓
              STRUCTURED RESULT
     (Strict, Frozen JSON Integration Schema)
```

---

## 1. What This Module Does

- **Vision Analysis:** Assesses image quality (blurriness, exposure, non-crop objects) and detects foliar symptoms for key paddy diseases:
  1. Rice Blast (*Magnaporthe oryzae* / *Pyricularia oryzae*)
  2. Bacterial Leaf Blight (*Xanthomonas oryzae* pv. *oryzae*)
  3. Sheath Blight (*Rhizoctonia solani*)
  4. Brown Spot (*Bipolaris oryzae*)
  5. False Smut (*Ustilaginoidea virens*)
  6. Healthy foliage screening
- **Grounded Agricultural RAG:** Indexes authentic ICAR, IRRI, and TNAU advisories in ChromaDB.
- **Zero Pesticide Hallucination:** Chemical active ingredients (e.g., Tricyclazole, Hexaconazole, Validamycin, Copper Hydroxide, Streptocycline) are strictly sourced from verified agricultural extension records. No unverified commercial brands or ungrounded dosages are invented.
- **Multilingual Support:** Seamlessly renders localized outputs in English, Telugu (తెలుగు), Hindi (हिंदी), and others.
- **Single Public API:** Member 1 or other teammates only need to call `analyze_crop()`.

---

## 2. Installation

Install all required Python dependencies:

```bash
pip install -r requirements.txt
```

Core libraries:
- `chromadb` (Vector database)
- `pydantic` (Data schema validation)
- `pillow` (Computer vision and image preprocessing)
- `pymupdf` / `pypdf` (PDF text extraction)
- `reportlab` (Agricultural PDF bulletin generation)
- `pytest` (Automated testing)

---

## 3. Environment Variables

The module operates 100% offline out-of-the-box using built-in deterministic vision heuristics, ChromaDB ONNX embeddings, and grounded rule synthesis.

To enable online Google Gemini Vision and LLM synthesis, set:

```bash
# Optional: Activates Gemini 2.0 Flash Vision and multilingual generation
export GEMINI_API_KEY="your-gemini-api-key"

# Windows PowerShell:
$env:GEMINI_API_KEY="your-gemini-api-key"
```

If `GEMINI_API_KEY` is omitted, the module automatically uses the built-in local engine without raising errors.

---

## 4. How to Ingest PDFs

Official agricultural extension PDFs are placed in `ai_disease/data/pdf/`.

To build or refresh the corpus PDFs from the authentic ICAR/IRRI advisory data:

```bash
python ai_disease/data/build_corpus.py
```

To ingest documents through code:

```python
from ai_disease.ingestion.document_loader import DocumentLoader
from ai_disease.ingestion.text_chunker import TextChunker

loader = DocumentLoader()
docs = loader.load_directory("ai_disease/data/pdf")

chunker = TextChunker()
chunks = []
for doc in docs:
    chunks.extend(chunker.chunk_document(doc, crop="paddy"))
print(f"Total semantic chunks extracted: {len(chunks)}")
```

---

## 5. How to Build ChromaDB

The vector database is managed by `ChromaStore` inside `ai_disease/data/processed/chroma_db/` under the dedicated collection `paddy_disease_knowledge`.

To ingest all PDFs and build the vector database:

```bash
python -c "from ai_disease.vectorstore.chroma_store import ChromaStore; store = ChromaStore(); store.ingest_documents(); print(store.get_stats())"
```

Output:
```json
{
  "collection_name": "paddy_disease_knowledge",
  "document_count": 31,
  "persist_dir": ".../ai_disease/data/processed/chroma_db"
}
```

---

## 6. How to Test Retrieval

You can query the RAG vector store directly using `retrieve_disease_information()`:

```python
from ai_disease.retrieval.retriever import retrieve_disease_information

results = retrieve_disease_information(
    crop="paddy",
    disease="sheath blight",
    query="brown lesions near water level",
    top_k=5
)

for item in results:
    print(f"Source: {item['source']} (Score: {item['score']})")
    print(f"Content: {item['content'][:120]}...\n")
```

---

## 7. How to Test Vision

You can test the vision analyzer independently on any image:

```python
from ai_disease.vision.disease_vision import DiseaseVision

vision = DiseaseVision()
result = vision.analyze_image("ai_disease/data/images/rice_blast.jpg")

print(result)
```

Output:
```json
{
  "crop": "paddy",
  "possible_disease": "Rice Blast",
  "confidence": 0.88,
  "observations": [
    "Spindle-shaped / diamond-shaped lesions observed on leaf blade",
    "Lesions exhibit whitish-gray centers with dark reddish-brown margins",
    "Early signs of leaf tissue necrosis coalescing along leaf axis"
  ]
}
```

If the image is blurry or non-crop:
```json
{
  "crop": "paddy",
  "possible_disease": "uncertain",
  "confidence": 0.0,
  "observations": ["Image lacks sufficient edge sharpness and focus for diagnostic evaluation"]
}
```

---

## 8. How to Call `analyze_crop()`

`analyze_crop()` is the **single public entry point** for all teammates.

```python
from ai_disease.pipeline import analyze_crop

# 1. Image-based diagnosis in English
result = analyze_crop(
    image_path="ai_disease/data/images/sheath_blight.jpg",
    crop="paddy",
    language="English"
)

# 2. Image-based diagnosis in Telugu
result_te = analyze_crop(
    image_path="ai_disease/data/images/rice_blast.jpg",
    crop="paddy",
    language="Telugu"
)

# 3. Symptom query mode without image
result_query = analyze_crop(
    image_path=None,
    crop="paddy",
    query="leaves have spindle shaped spots with grey centers",
    language="English"
)
```

---

## 9. Input Schema

`analyze_crop()` accepts the following parameters:

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `image_path` | `str` | Optional (if `query` provided) | `None` | Local filepath to the leaf/panicle photo (`.jpg`, `.jpeg`, `.png`, `.webp`) |
| `crop` | `str` | Optional | `"paddy"` | Name of crop (e.g. `"paddy"`, `"rice"`) |
| `language` | `str` | Optional | `"English"` | Output language: `"English"`, `"Telugu"`, `"Hindi"`, etc. |
| `query` | `str` | Optional | `None` | Text description of symptoms (used when image is omitted or as extra context) |

---

## 10. Output Schema (Contract Frozen)

The return value is a Python dictionary matching the frozen `DiseaseAnalysisResult` schema:

```json
{
  "crop": "paddy",
  "disease": "Sheath Blight",
  "confidence": 0.89,
  "observations": [
    "Oval to oblong water-soaked greenish-gray lesions detected on lower leaf sheath",
    "Irregular dark brown borders with banded snake-skin-like pattern",
    "Lesions localized near the water/soil line"
  ],
  "symptoms": [
    "Initial symptoms develop on leaf sheaths near the water level as oval or oblong, water-soaked, greenish-gray spots (1-3 cm long).",
    "As lesions mature, the centers become bleached, grayish-white, with an irregular dark brown or purple border."
  ],
  "organic_management": [
    "Seed treatment with Trichoderma viride or Pseudomonas fluorescens @ 10 g/kg seed.",
    "Soil application of Trichoderma enriched farmyard manure (FYM) @ 2.5 kg/ha at final land preparation.",
    "Opt for wider spacing during transplanting (20 x 15 cm) to facilitate canopy aeration."
  ],
  "chemical_management": [
    "Foliar spray targeted at the base of the plant: Hexaconazole 5% EC @ 2.0 mL/L or Validamycin 3% L @ 2.0 mL/L at first appearance of symptoms.",
    "Active Ingredient: Hexaconazole 5% EC | Reference Formulation: Contaf | Source: DPPQS Approved Pesticide List"
  ],
  "evidence": [
    "1. Identification and Morphological Symptoms: Initial symptoms develop on leaf sheaths...",
    "5. Verified Chemical Interventions: Foliar spray targeted at the base of the plant: Hexaconazole 5% EC..."
  ],
  "sources": [
    "sheath_blight_management_manual.pdf"
  ],
  "warning": "Vision prediction is an automated estimation and not a laboratory diagnosis. Verify with local agricultural extension officer or KVK before chemical application.",
  "language": "English"
}
```

---

## 11. Integration Instructions for Member 1 (LangGraph)

Member 1 can connect `ai_disease` to a LangGraph node in just **3 lines of code**:

```python
# Inside your LangGraph agent or node file:
from ai_disease.pipeline import analyze_crop

def disease_diagnosis_node(state: dict) -> dict:
    # 1. Read input from graph state
    image_path = state.get("image_path")
    crop = state.get("crop", "paddy")
    language = state.get("language", "English")

    # 2. Call the single public interface
    diagnosis = analyze_crop(
        image_path=image_path,
        crop=crop,
        language=language
    )

    # 3. Store structured diagnosis back into state
    state["disease_result"] = diagnosis
    return state
```

### Team Guarantee:
- No LangGraph dependencies inside `ai_disease`.
- No modification of your agent state schemas, checkpointers, or routing logic.
- Stable, contract-frozen return structure.

---

## 12. Running Tests

Run the comprehensive 15-scenario verification runner:

```bash
python ai_disease/tests/run_tests.py
```

Run via pytest:

```bash
pytest ai_disease/tests/test_suite.py
```
