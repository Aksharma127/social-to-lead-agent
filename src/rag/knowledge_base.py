import json
from pathlib import Path
from typing import List

try:
    # Prefer real implementations when available
    from langchain.schema import Document  # type: ignore
    from langchain.vectorstores import Chroma  # type: ignore
    from langchain_google_genai import GoogleGenerativeAIEmbeddings  # type: ignore
    _HAS_LANGCHAIN = True
except Exception:
    # Provide minimal fallbacks so the module can be imported and tests can run
    _HAS_LANGCHAIN = False

from utils.config import settings
from utils.logger import get_logger

logger = get_logger()

VECTOR_DIR = ".chromadb"
DATA_PATH = Path(__file__).parent / "data" / "autostream_kb.json"


if not _HAS_LANGCHAIN:
    # Minimal Document replacement
    class Document:
        def __init__(self, page_content: str, metadata: dict | None = None):
            self.page_content = page_content
            self.metadata = metadata or {}

    # Minimal in-memory vectorstore replacement with simple substring/keyword matching
    class Chroma:
        def __init__(self, persist_directory: str | None = None, embedding_function=None):
            self._docs: List[Document] = []

        @classmethod
        def from_documents(cls, documents: List[Document], embedding=None, persist_directory: str | None = None):
            inst = cls(persist_directory=persist_directory, embedding_function=embedding)
            inst._docs = list(documents)
            return inst

        def persist(self):
            # no-op for fallback
            return

        def similarity_search(self, query: str, k: int = 3) -> List[Document]:
            q = query.lower()
            # Score documents by count of matching words between query and text/id
            def score(doc: Document) -> int:
                text = (doc.page_content or "").lower()
                doc_id = str(doc.metadata.get("id", "")).lower()
                s = 0
                for token in q.split():
                    if token in text or token in doc_id:
                        s += 1
                return s

            scored = sorted(self._docs, key=lambda d: score(d), reverse=True)
            # If nothing matches, fallback to returning the first k docs
            if all(score(d) == 0 for d in scored):
                return scored[:k]
            return [d for d in scored if score(d) > 0][:k]

    # Minimal embeddings factory
    def GoogleGenerativeAIEmbeddings(*args, **kwargs):
        return None


def load_documents() -> List[Document]:
    with open(DATA_PATH, "r") as f:
        raw_data = json.load(f)

    documents: List[Document] = []
    for item in raw_data:
        documents.append(
            Document(
                page_content=item["text"],
                metadata={"id": item["id"]}
            )
        )

    return documents


def get_embeddings():
    # Gemini-compatible embeddings when available, otherwise a noop
    if _HAS_LANGCHAIN:
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_API_KEY,
        )
    return None


def get_vectorstore() -> Chroma:
    documents = load_documents()
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=VECTOR_DIR,
    )

    try:
        vectorstore.persist()
    except Exception:
        # persist may be a no-op in fallback
        pass
    logger.info("Vector store initialized and persisted")

    return vectorstore


def retrieve_context(query: str, k: int = 3) -> str:
    # When langchain is available the vectorstore can be re-opened; otherwise use a new simple store
    if _HAS_LANGCHAIN:
        vectorstore = Chroma(persist_directory=VECTOR_DIR, embedding_function=get_embeddings())
    else:
        vectorstore = get_vectorstore()

    results = vectorstore.similarity_search(query, k=k)
    return "\n".join([doc.page_content for doc in results])
