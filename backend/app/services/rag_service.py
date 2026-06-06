"""
RAG Service — handles local schema metadata ingestion and similarity search using ChromaDB.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)

# Base directory for local ChromaDB storage
CHROMA_DB_DIR = Path(__file__).resolve().parents[2] / "chroma_db"
os.makedirs(CHROMA_DB_DIR, exist_ok=True)


class RAGService:
    """Service to manage local schema embeddings and similarity retrieval."""

    def __init__(self, persist_directory: str = str(CHROMA_DB_DIR)) -> None:
        self.persist_directory = persist_directory
        self._client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        # Get or create the collection for schemas
        self.collection = self._client.get_or_create_collection(
            name="schema_metadata",
            metadata={"hnsw:space": "cosine"}
        )

    def add_schema(
        self,
        collection_name: str,
        fields_metadata: List[Dict[str, Any]],
        description: str = ""
    ) -> None:
        """Add or update the schema description of a specific database collection.
        
        fields_metadata structure:
        [
            {"field_name": "status", "type": "string", "description": "SUCCESS / FAILED"},
            ...
        ]
        """
        # Convert field metadata list to a text blob for embedding & searching
        fields_lines = []
        for f in fields_metadata:
            fields_lines.append(f"- {f['field_name']} ({f.get('type', 'string')}) — {f.get('description', '')}")
        fields_text = "\n".join(fields_lines)

        document_content = f"Collection: {collection_name}\nDescription: {description}\nFields:\n{fields_text}"

        metadata = {
            "collection_name": collection_name,
            "description": description,
            "fields_json": chromadb.utils.json.dumps(fields_metadata) if hasattr(chromadb.utils, "json") else str(fields_metadata)
        }

        # Use collection name as unique ID
        self.collection.upsert(
            documents=[document_content],
            metadatas=[metadata],
            ids=[collection_name]
        )
        logger.info("Successfully ingested schema metadata for collection: %s", collection_name)

    def retrieve_relevant_schemas(self, user_query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant collections and their schemas based on a natural language query."""
        try:
            results = self.collection.query(
                query_texts=[user_query],
                n_results=limit
            )
            
            retrieved = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                docs = results["documents"][0]
                metadatas = results["metadatas"][0]
                ids = results["ids"][0]
                
                for doc, meta, doc_id in zip(docs, metadatas, ids):
                    retrieved.append({
                        "collection_name": doc_id,
                        "document": doc,
                        "metadata": meta
                    })
            return retrieved
        except Exception as exc:
            logger.error("Failed to query ChromaDB schemas: %s", exc)
            return []

    def reset_db(self) -> None:
        """Delete all items in the schema collection."""
        try:
            self._client.delete_collection("schema_metadata")
            self.collection = self._client.get_or_create_collection(
                name="schema_metadata",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB schema collection reset completed successfully")
        except Exception as exc:
            logger.error("Failed to reset ChromaDB: %s", exc)
