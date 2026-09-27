"""Main application for Agentic RAG"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.config.config import Config
from src.document_ingestion.docu import docuprocessor
from src.vectorstore.faiss import Retriever
from src.graph_builder.g_builder import GraphBuilder


class AgenticRAG:

    def __init__(self, srcs: list[str]):

        print("Initializing Agentic RAG...")

        self.srcs = srcs

        self.processor = docuprocessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )

        self.retriever = Retriever()

        if self.retriever.index_exists():

            print("Loading existing FAISS index...")

            self.retriever.load_retriever()

        else:

            print("Processing legal documents...")

            docs = self.processor.process(srcs)

            print(f"Created {len(docs)} chunks")

            self.retriever.create_retriever(docs)

        self.llm = Config.get_llm()

        self.graph_builder = GraphBuilder(
            retriever=self.retriever,
            llm=self.llm
        )

        self.graph_builder.build()

        print("System Ready")

    def ask(self, question: str, chat_history=None, mode: str = "normal"):

        if chat_history is None:
            chat_history = []

        result = self.graph_builder.run(
            question=question,
            chat_history=chat_history,
            mode=mode
        )

        answer = result["answer"]

        source_type = result.get(
         "source_type",
    ""
)

        confidence = result.get(
    "confidence",
    ""
)

        print("\nQuestion:")
        print(question)

        print("\nAnswer:")
        print(answer)

        return {
    "answer": answer,
    "source_type": source_type,
    "confidence": confidence
}

    def interactive_mode(self):

        print("\nInteractive Mode Started")

        choice = input(
            "Choose mode - [1] Professional  [2] Normal (default 2): "
        ).strip()

        mode = "professional" if choice == "1" else "normal"

        print(f"Mode: {mode.title()}")
        print("Type 'quit' to exit\n")

        history = []

        while True:

            question = input("Enter Question: ").strip()

            if question.lower() in ["quit", "exit", "q"]:
                print("Goodbye")
                break

            if question:

                answer = self.ask(
                    question,
                    history,
                    mode
                )

                history.append(
                    {
                        "role": "user",
                        "content": question
                    }
                )

                history.append(
    {
        "role": "assistant",
        "content": answer["answer"]
    }
)

                print("-" * 80)


def main():

    sources = [
        "data/legal_pdfs/Bharatiya_Nagarik_Suraksha_Sanhita,_2023.pdf",
        "data/legal_pdfs/it_act_2000_updated.pdf",
        "data/legal_pdfs/CP Act 2019_1732700731.pdf"
    ]

    rag = AgenticRAG(sources)

    rag.interactive_mode()


if __name__ == "__main__":
    main()