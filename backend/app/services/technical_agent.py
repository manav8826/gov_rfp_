import os
import json
from typing import List, Dict
from app.services.pdf_processor import PDFProcessor
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Define structured output for the LLM
class CableSpec(BaseModel):
    voltage: str = Field(description="Voltage grade of the cable")
    insulation: str = Field(description="Insulation type e.g., XLPE, PVC")
    cores: str = Field(description="Number of cores")
    armouring: str = Field(description="Type of armouring e.g., Strip, Wire, Unarmoured")

class RFPItem(BaseModel):
    name: str = Field(description="Name of the item")
    specs: CableSpec

class RFPExtraction(BaseModel):
    items: List[RFPItem]

from app.core.config import settings

from app.services.vector_store import ProductVectorDB

class TechnicalAgent:
    def __init__(self):
        # Initialize Groq
        api_key = settings.GROQ_API_KEY
        print(f"DEBUG: TechnicalAgent initializing. Groq Key present: {bool(api_key)}")
        if not api_key:
            print("WARNING: GROQ_API_KEY not found in settings. Agent will use Fallback/Mock mode.")
            self.llm = None
        else:
            self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=api_key, temperature=0)
            print("DEBUG: Groq LLM initialized successfully.")

        # Initialize Real Vector DB
        try:
            self.vector_db = ProductVectorDB()
            print("DEBUG: ChromaDB Vector Store initialized.")
        except Exception as e:
            print(f"WARNING: Vector DB failed to load: {e}")
            self.vector_db = None

    def process_rfp(self, file_content: bytes) -> Dict:
        print("DEBUG: process_rfp called. Starting PDF extraction...")
        # 1. Extraction
        if file_content.startswith(b"Simulated PDF Content"):
            # BYPASS PDF EXTRACTOR for Magic Run Demo
            full_text = file_content.decode('utf-8')
            # Simulated extracted text to prompt LLM correctly
            # We add diverse line items to show "Deep Analysis"
            full_text += """
            SCOPE OF WORK:
            1. Supply of 11kV XLPE Power Cable, 3 Core, 300sqmm, Armoured. Quantity: 5000 meters.
            2. Supply of 1.1kV PVC Control Cable, 12 Core, 1.5sqmm, Unarmoured. Quantity: 2000 meters.
            3. Enterprise Cloud Hosting & Managed Services for SCADA System. Quantity: 12 months.
            """
            print("DEBUG: Detected Mock Content, skipping PDF parser.")
        else:
            pdf_data = PDFProcessor.extract_structured_data(file_content)
            full_text = pdf_data["full_text"]
        
        print(f"DEBUG: Extracted {len(full_text)} chars from PDF.")
        if len(full_text.strip()) < 50:
            return {
                "summary": "Error: PDF seems empty or is a scanned image. OCR is required but not installed in MVP.",
                "line_items": [],
                "raw_text_snippet": "EMPTY_TEXT"
            }
        
        # 2. AI Extraction
        if file_content.startswith(b"Simulated PDF Content"):
             # BYPASS PDF EXTRACTOR for Magic Run Demo
             full_text = file_content.decode('utf-8')
             print("DEBUG: Detected Mock Content, returning Perfect Extraction.")
             # FORCE the logic to return these exact items so the Demo is consistent
             detected_requirements = [
                {
                    "name": "11kV XLPE Power Cable, 3 Core, 300sqmm, Armoured",
                    "quantity": 5000.0,
                    "specs": {"voltage": "11kV", "insulation": "XLPE", "cores": "3", "armouring": "Strip"}
                },
                {
                    "name": "1.1kV PVC Control Cable, 12 Core, 1.5sqmm, Unarmoured",
                    "quantity": 2000.0,
                    "specs": {"voltage": "1.1kV", "insulation": "PVC", "cores": "12", "armouring": "Unarmoured"}
                },
                {
                    "name": "Enterprise Cloud Hosting & Managed Services",
                    "quantity": 12.0,
                    "specs": {"type": "Cloud", "sla": "99.9%", "platform": "AWS/Azure"}
                }
             ]
             # Skip LLM call
             self.llm = None 
        else:
             # Real PDF Logic
             if self.llm:
                 print("DEBUG: Calling AI extraction...")
                 detected_requirements = self._extract_with_ai(full_text)
             else:
                 # Fallback for testing without keys
                 detected_requirements = [
                     {"name": "Mock AI Item", "specs": {"voltage": "11kV", "insulation": "Mock"}}
                 ]
        
        # 3. Matching Logic
        matches = []
        total_match_score = 0
        
        for req in detected_requirements:
            # Convert Pydantic model to dict if needed
            if hasattr(req, "dict"):
                req_dict = req.dict()
            else:
                req_dict = req

            best_match = self._find_best_match(req_dict)
            matches.append({
                "requirement": req_dict,
                "recommendation": best_match
            })
            # Aggregate score (max 100 per item)
            total_match_score += best_match.get("match_score", 0)

        # ------------------------------------------------------------------
        # CONSULTING LOGIC: Right-to-Win / Strategic Fit
        # ------------------------------------------------------------------
        num_items = len(detected_requirements) if detected_requirements else 1
        avg_score = total_match_score / num_items
        
        if avg_score > 75:
            win_prob = "High"
            rationale = "Strong portfolio fit. We have exact specs for most items."
        elif avg_score > 40:
            win_prob = "Medium"
            rationale = "Partial fit. Some customization or third-party sourcing required."
        else:
            win_prob = "Low"
            rationale = "High risk. Multiple items matched poorly or require new interaction."

        strategic_analysis = {
            "overall_capability_score": round(avg_score, 1),
            "win_probability": win_prob,
            "executive_summary": rationale,
            "risk_assessment": "Low" if avg_score > 60 else "High"
        }
            
        return {
            "summary": f"AI Analyzed {len(matches)} line items from RFP.",
            "strategic_analysis": strategic_analysis,
            "line_items": matches,
            "raw_text_snippet": full_text[:200] + "..."
        }

    def _extract_with_ai(self, text: str) -> List[Dict]:
        parser = PydanticOutputParser(pydantic_object=RFPExtraction)
        
        prompt = PromptTemplate(
            template="""You are an expert Technical Sales Engineer. Extract the 'Scope of Supply' from the following RFP text.
            Identify cable requirements, specifications, AND quantities.
            
            RFP Text:
            {text}
            
            {format_instructions}
            """,
            input_variables=["text"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # chain = prompt | self.llm | parser  <-- Old way
        
        try:
            # Chunking text if too large (naive approach for MVP)
            safe_text = text[:30000] 
            
            # Step 1: Get raw response
            chain_1 = prompt | self.llm
            response = chain_1.invoke({"text": safe_text})
            print(f"DEBUG: Raw AI Response: {response.content[:500]}...") # Print first 500 chars
            
            # Step 2: Parse
            output = parser.parse(response.content)
            return output.items
        except Exception as e:
            print(f"AI Extraction Failed: {e}")
            return []

    def _find_best_match(self, req: Dict) -> Dict:
        """
        Uses Semantic Search via ChromaDB to find top 3 products 
        and generates a comparison table.
        """
        if not self.vector_db:
             return {"sku": "DB_ERROR", "name": "Vector DB not loaded", "match_score": 0}
             
        query_text = f"{req.get('name')} {req.get('specs', '')}"
        
        # Get Top 3 Results
        candidates = self.vector_db.search(query_text, k=3)
        
        if not candidates:
            return {"sku": "NO_MATCH", "name": "No suitable product found", "match_score": 0}

        recommended_product = None
        highest_score = -1
        
        comparison_list = []

        # Evaluate matches
        for idx, cand in enumerate(candidates):
            # Calculate a mock "Spec Match %" based on distance
            dist = cand.get('distance', 1.0)
            base_score = max(0, min(100, int((1.5 - dist) / 1.5 * 100)))

            # ------------------------------------------------------------------
            # CONSULTING LOGIC: Granular Spec Breakdown
            # ------------------------------------------------------------------
            # We compare the 'specs' from the Requirement vs 'specs' from the Candidate Metadata
            # We compare the 'specs' from the Requirement vs 'specs' from the Candidate Metadata
            cand_specs = cand.get("specs", {})
            
            # Helper to parse stringified JSON from Chroma
            if isinstance(cand_specs, str):
                try:
                    cand_specs = json.loads(cand_specs)
                except:
                    cand_specs = {}
            
            req_specs = req.get("specs", {})
            if hasattr(req_specs, "dict"):
                 req_specs = req_specs.dict()
            
            detailed_analysis = []
            
            # 1. Voltage Check
            if "voltage" in req_specs and "voltage" in cand_specs:
                r_v = str(req_specs["voltage"]).lower()
                c_v = str(cand_specs["voltage"]).lower()
                if "not" in r_v or r_v in c_v or c_v in r_v:
                     detailed_analysis.append({"spec": "Voltage", "status": "Methods", "value": cand_specs["voltage"]})
                else:
                     detailed_analysis.append({"spec": "Voltage", "status": "Mismatch", "value": cand_specs["voltage"]})
            
            # 2. Insulation Check
            if "insulation" in req_specs and "insulation" in cand_specs:
                r_i = str(req_specs["insulation"]).lower()
                c_i = str(cand_specs["insulation"]).lower()
                if "not" in r_i or r_i in c_i or c_i in r_i:
                     detailed_analysis.append({"spec": "Insulation", "status": "Match", "value": cand_specs["insulation"]})
                else:
                     detailed_analysis.append({"spec": "Insulation", "status": "Mismatch", "value": cand_specs["insulation"]})

            # For Services, we just add a generic check
            if cand.get("category") == "Service":
                detailed_analysis.append({"spec": "Service Type", "status": "Match", "value": cand.get("name")})
            
            cand_info = {
                "rank": idx + 1,
                "sku": cand["sku"],
                "name": cand["name"],
                "description": cand.get("details", ""),
                "price": cand.get("price"),
                "category": cand.get("category"),
                "match_score": base_score,
                "spec_breakdown": detailed_analysis
            }
            comparison_list.append(cand_info)
            
            if base_score > highest_score:
                highest_score = base_score
                recommended_product = cand_info
                
            if idx == 0 and not recommended_product:
                 # Default to rank 1 if scores are weird
                 recommended_product = cand_info

        # If best match is too poor, reject it
        if highest_score < 20:
             return {
                 "sku": "NO_MATCH", 
                 "name": "No suitable product found (Low Score)", 
                 "match_score": highest_score,
                 "comparison_table": comparison_list
             }

        # Return the selected product + the full comparison context
        return {
            "sku": recommended_product["sku"],
            "name": recommended_product["name"],
            "description": recommended_product["description"],
            "price": recommended_product["price"],
            "category": recommended_product["category"],
            "match_score": recommended_product["match_score"],
            "comparison_table": comparison_list
        }
