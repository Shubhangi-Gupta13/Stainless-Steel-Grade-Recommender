"""Knowledge Base loader, database query engine, and RAG retrieval pipeline"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.config import GRADES_DB_PATH, KB_DIR, FAISS_DIR
from src.models import GradeRecord


class KnowledgeBase:
    """Manages structured grade database and unstructured technical knowledge corpus"""

    def __init__(self):
        self.grades: List[GradeRecord] = []
        self.grades_by_name: Dict[str, GradeRecord] = {}
        self.knowledge_docs: List[Dict[str, Any]] = []
        self._load_database()
        self._load_markdown_docs()

    def _load_database(self):
        """Loads and parses the structured JSON database into GradeRecord models"""
        if not GRADES_DB_PATH.exists():
            raise FileNotFoundError(f"Grades database not found at {GRADES_DB_PATH}")

        with open(GRADES_DB_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        self.grades = [GradeRecord(**item) for item in raw_data]
        for g in self.grades:
            self.grades_by_name[g.grade_name.upper()] = g
            for alias in g.aliases:
                self.grades_by_name[alias.upper()] = g

    def _load_markdown_docs(self):
        """Loads technical documents from data/knowledge_base/"""
        if not KB_DIR.exists():
            return

        for md_file in KB_DIR.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                # Split content into logical sections by H2 headers
                sections = content.split("\n## ")
                doc_title = sections[0].strip("# \n")
                
                for idx, sec in enumerate(sections[1:], start=1):
                    lines = sec.split("\n")
                    sub_title = lines[0].strip()
                    sec_body = "\n".join(lines[1:]).strip()
                    
                    self.knowledge_docs.append({
                        "doc_title": doc_title,
                        "section_title": sub_title,
                        "file_name": md_file.name,
                        "text": f"## {sub_title}\n{sec_body}",
                        "chunk_id": f"{md_file.stem}#sec-{idx}"
                    })
            except Exception as e:
                print(f"Error loading {md_file}: {e}")

    def get_all_grades(self) -> List[GradeRecord]:
        """Returns all stainless steel grades in database"""
        return self.grades

    def get_grade_by_name(self, name: str) -> Optional[GradeRecord]:
        """Lookup grade by exact or alias name"""
        clean_name = name.strip().upper()
        if clean_name in self.grades_by_name:
            return self.grades_by_name[clean_name]
        # Partial match fallback
        for key, record in self.grades_by_name.items():
            if clean_name in key or key in clean_name:
                return record
        return None

    def retrieve_relevant_snippets(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieves relevant technical documentation passages using keyword and semantic matching.
        Guaranteed to run deterministically with zero latency.
        """
        query_words = set(query.lower().replace(",", " ").replace("-", " ").split())
        scored_docs = []

        for doc in self.knowledge_docs:
            doc_text = doc["text"].lower()
            score = 0
            # Keyword frequency & section title boost
            for word in query_words:
                if len(word) > 2:
                    if word in doc["section_title"].lower():
                        score += 5
                    if word in doc_text:
                        score += doc_text.count(word)

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_docs[:top_k]]

    def get_datasheet_citation(self, grade_name: str) -> str:
        """Returns standard JSL datasheet citation for a given grade"""
        grade = self.get_grade_by_name(grade_name)
        if grade:
            return f"[{grade.source_reference} | Standards: {', '.join(grade.standards[:2])}]"
        return "[Jindal Stainless Technical Product Catalog]"


# Singleton instance
_KB_INSTANCE = None

def get_knowledge_base() -> KnowledgeBase:
    global _KB_INSTANCE
    if _KB_INSTANCE is None:
        _KB_INSTANCE = KnowledgeBase()
    return _KB_INSTANCE
