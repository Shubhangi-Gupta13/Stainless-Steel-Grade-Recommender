from pathlib import Path

from src.state.ragstate import RAGstate
from src.config.config import Config

from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults


class Nodes:

    # Maps keywords found in the PDF filenames to clean, citable names.
    # Adjust the keys to match your actual filenames in data/.
    SOURCE_NAMES = {
        "bnss": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "nagarik": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "it_act": "Information Technology Act, 2000",
        "information_technology": "Information Technology Act, 2000",
        "consumer": "Consumer Protection Act, 2019",
    }

    def __init__(self, retriever, llm):

        self.retriever = retriever

        self.llm = llm

        self.evaluator_llm = Config.get_evaluator_llm()

        self.tavily = TavilySearchResults(max_results=5)

    # ----------------------------------------------------------------- #
    # Helpers
    # ----------------------------------------------------------------- #

    def _friendly_source(self, raw: str) -> str:
        """Turn a raw file path into a clean, citable law name."""

        stem = Path(str(raw)).stem
        low = stem.lower()

        for key, name in self.SOURCE_NAMES.items():
            if key in low:
                return name

        return stem.replace("_", " ").replace("-", " ").title()

    def _format_external(self, raw_results):
        """
        Turn Tavily output into (context_text, sources_list).

        Tavily returns a list of dicts with 'url'/'content' (and sometimes
        'title'). On failure external_search returns an error string, which
        we pass through unchanged with no sources.
        """

        if isinstance(raw_results, str):
            return raw_results, []

        if isinstance(raw_results, list):

            parts = []
            sources = []

            for r in raw_results:

                if isinstance(r, dict):

                    url = r.get("url", "")
                    title = r.get("title") or url or "Web result"
                    content = r.get("content", "")

                    if url:
                        sources.append(f"{title} — {url}")

                    parts.append(f"{content}\n(Source: {url})")

                else:
                    parts.append(str(r))

            return "\n\n".join(parts), sources

        return str(raw_results), []

    # ----------------------------------------------------------------- #
    # LLM steps
    # ----------------------------------------------------------------- #

    def rewrite_question(
        self,
        question: str,
        chat_history: list
    ) -> str:

        if not chat_history:

            return question

        recent_history = chat_history[-6:]

        history_text = "\n".join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in recent_history
            ]
        )

        prompt = f"""
You are a query rewriting assistant.

Conversation History:

{history_text}

Latest User Question:

{question}

Rewrite the latest question into a standalone question.

The rewritten question must preserve the original meaning while incorporating any necessary context from the conversation history.

Return ONLY the rewritten question.
"""

        response = self.llm.invoke(prompt)

        rewritten_question = response.content.strip()

        print(f"\nOriginal Question: {question}")
        print(f"Rewritten Question: {rewritten_question}")

        return rewritten_question

    def evaluate_context(self, question: str, context: str) -> str:

        prompt = f"""
You are a retrieval evaluator.

Question:
{question}

Retrieved Context:
{context}

Can the question be answered accurately and completely using ONLY the retrieved context?

Return ONLY one word:

SUFFICIENT

or

INSUFFICIENT
"""

        response = self.evaluator_llm.invoke(prompt)

        result = response.content.strip().upper()

        print(f"Evaluator Output: {result}")

        if result.startswith("INSUFFICIENT"):
            return "INSUFFICIENT"

        if result.startswith("SUFFICIENT"):
            return "SUFFICIENT"

        return "INSUFFICIENT"

    def external_search(self, question: str):

        try:

            result = self.tavily.invoke(question)

            print("Tavily Search Triggered")

            return result

        except Exception as e:

            return f"External search failed: {str(e)}"

    def generate_corrective_answer(
        self,
        question: str,
        external_context: str,
        sources: list,
        mode: str = "normal"
    ) -> str:

        source_block = (
            "\n".join(f"- {s}" for s in sources)
            if sources
            else "- External web search"
        )

        if mode == "professional":

            style = f"""
Provide a DETAILED answer aimed at a legal professional.
- Use clear bullet points, one distinct point per bullet.
- Where possible, attribute each point to the specific web source it came from.
- If information comes from a proposed bill, draft amendment, consultation paper,
  or news report, explicitly flag this on the relevant point.
- Use precise legal terminology.
- After the answer, add a "Sources:" section listing:
{source_block}
"""

        else:

            style = """
Provide a SHORT, plain-language overview for a non-lawyer.
- Use 3 to 6 simple bullet points, with no legal jargon.
- If anything is only a proposal, draft, or news (not settled law), say so plainly.
- End with one simple line naming where this came from, e.g. "Based on: web search".
"""

        prompt = f"""
You are an AI legal assistant specialized in Indian laws.

QUESTION:
{question}

EXTERNAL INFORMATION:
{external_context}

Instructions:

1. Begin with:

Source: External Search

2. Explain that the answer was not found in the uploaded legal corpus.

3. Use the external information to answer.

{style}

End with:

Confidence Level: Medium
"""

        response = self.llm.invoke(prompt)

        return response.content

    def generate_rag_answer(
        self,
        question: str,
        context: str,
        mode: str = "normal"
    ) -> str:

        if mode == "professional":

            style = """
Provide a DETAILED answer aimed at a legal professional.
- Use clear bullet points, one distinct point per bullet.
- After each point, cite the exact source shown in the context in brackets,
  e.g. [Bharatiya Nagarik Suraksha Sanhita, 2023, p. 4].
- Reference specific sections or provisions where they appear in the context.
- Use precise legal terminology.
- End with a "Sources:" section listing every law referenced.
"""

        else:

            style = """
Provide a SHORT, plain-language overview for a non-lawyer.
- Use 3 to 6 simple bullet points, with no legal jargon.
- Keep it easy to understand.
- End with one simple line: "Based on: <law name(s)>" naming the source law(s)
  from the context above.
"""

        prompt = f"""
You are an AI legal assistant specialized in Indian laws.

Use ONLY the legal context below.

LEGAL CONTEXT:
{context}

QUESTION:
{question}

{style}

ANSWER:
"""

        response = self.llm.invoke(prompt)

        return response.content

    # ----------------------------------------------------------------- #
    # Main node
    # ----------------------------------------------------------------- #

    def generate_ans(self, state: RAGstate) -> RAGstate:

        try:

            rewritten_question = self.rewrite_question(
                state.question,
                state.chat_history
            )

            docs: list[Document] = self.retriever.retrieve(
                rewritten_question
            )

            if not docs:

                print("No documents retrieved. Switching to Tavily.")

                raw = self.external_search(rewritten_question)

                external_context, ext_sources = self._format_external(raw)

                answer = self.generate_corrective_answer(
                    rewritten_question,
                    external_context,
                    ext_sources,
                    state.mode
                )

                return RAGstate(
                    question=state.question,
                    chat_history=state.chat_history,
                    mode=state.mode,
                    retrieved_docs=[],
                    answer=answer,
                    context_quality="INSUFFICIENT",
                    source_type="external",
                    confidence="MEDIUM",
                    external_context=external_context
                )

            context = []

            for i, d in enumerate(docs, start=1):

                friendly = self._friendly_source(
                    d.metadata.get("source", "Unknown")
                )

                page = d.metadata.get("page", "N/A")

                context.append(
                    f"[Document {i} | Source: {friendly}, page {page}]\n{d.page_content}"
                )

            merged_context = "\n\n".join(context)

            context_quality = self.evaluate_context(
                rewritten_question,
                merged_context
            )

            print(f"Context Quality Decision: {context_quality}")

            if context_quality == "INSUFFICIENT":

                print("Using Tavily corrective search...")

                raw = self.external_search(rewritten_question)

                external_context, ext_sources = self._format_external(raw)

                answer = self.generate_corrective_answer(
                    rewritten_question,
                    external_context,
                    ext_sources,
                    state.mode
                )

                return RAGstate(
                    question=state.question,
                    chat_history=state.chat_history,
                    mode=state.mode,
                    retrieved_docs=docs,
                    answer=answer,
                    context_quality="INSUFFICIENT",
                    source_type="external",
                    confidence="MEDIUM",
                    external_context=external_context
                )

            answer = self.generate_rag_answer(
                rewritten_question,
                merged_context,
                state.mode
            )

            return RAGstate(
                question=state.question,
                chat_history=state.chat_history,
                mode=state.mode,
                retrieved_docs=docs,
                answer=answer,
                context_quality="SUFFICIENT",
                source_type="vectorstore",
                confidence="HIGH",
                external_context=""
            )

        except Exception as e:

            return RAGstate(
                question=state.question,
                chat_history=state.chat_history,
                mode=state.mode,
                retrieved_docs=[],
                answer=f"Error: {str(e)}",
                context_quality="ERROR",
                source_type="system",
                confidence="LOW",
                external_context=""
            )