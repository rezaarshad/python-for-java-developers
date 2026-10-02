# Retrieval augmented generation

RAG answers questions using your own documents. First retrieve the most relevant chunks with embeddings and
similarity search, then put those chunks into the prompt as context. Claude then answers grounded in that context
and can cite which note each fact came from. Chunk long documents so each piece fits a single topic.
