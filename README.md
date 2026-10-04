# AgriAgent — Part 2: RAG + Vision

This folder contains the complete, independent **Part 2: RAG + Vision** module (`ai_disease`) for the AgriAgent hackathon project.

## Opening in VS Code

You can open this folder directly in VS Code:
```
File -> Open Folder... -> C:\Users\gamid\.gemini\antigravity\scratch\RAG
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run all 15 test scenarios:**
   ```bash
   python ai_disease/tests/run_tests.py
   ```

3. **Or run pytest:**
   ```bash
   pytest ai_disease/tests/test_suite.py
   ```

4. **Integration Example:**
   ```python
   from ai_disease.pipeline import analyze_crop

   result = analyze_crop(
       image_path="ai_disease/data/images/sheath_blight.jpg",
       crop="paddy",
       language="English"
   )
   print(result)
   ```

For full documentation, architecture diagrams, corpus details, and API schemas, see [ai_disease/README.md](file:///C:/Users/gamid/.gemini/antigravity/scratch/RAG/ai_disease/README.md).
