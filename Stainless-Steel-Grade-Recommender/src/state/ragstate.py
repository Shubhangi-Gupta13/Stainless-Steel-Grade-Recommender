from langchain_core.documents import Document
from pydantic import BaseModel, Field


class RAGstate(BaseModel):

    question: str

    chat_history: list[dict] = Field(default_factory=list)

    # "professional" for lawyers/law students, "normal" for laypeople.
    mode: str = "normal"

    retrieved_docs: list[Document] = Field(default_factory=list)

    answer: str = ""

    context_quality: str = ""

    source_type: str = ""

    confidence: str = ""

    external_context: str = ""