from rag.knowledge_base import get_vectorstore, retrieve_context


def test_vectorstore_initialization():
    store = get_vectorstore()
    assert store is not None


def test_retrieval_returns_context():
    context = retrieve_context("pricing details")
    assert "pricing" in context.lower()
