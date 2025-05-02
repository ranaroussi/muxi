"""
Long-term memory implementation using PostgreSQL with pgvector.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from loguru import logger
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, String, Text, create_engine, desc, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from packages.core.config import config
from packages.core.utils.id_generator import get_default_nanoid

# Create SQLAlchemy Base
Base = declarative_base()


class Memory(Base):
    """Memory table for storing vector embeddings and metadata."""

    __tablename__ = "memories"

    id = Column(String(21), primary_key=True, default=get_default_nanoid)
    embedding = Column(Vector(config.memory.vector_dimension))
    text = Column(Text, nullable=False)
    meta_data = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    collection = Column(String(255), nullable=False, index=True)


class Collection(Base):
    """Collection table for organizing memories."""

    __tablename__ = "collections"

    id = Column(String(21), primary_key=True, default=get_default_nanoid)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LongTermMemory:
    """
    Long-term memory implementation using PostgreSQL with pgvector.
    This class provides a persistent vector database for storing and retrieving
    information based on semantic similarity.
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        dimension: int = config.memory.vector_dimension,
        default_collection: str = "default",
    ):
        """
        Initialize the long-term memory.

        Args:
            connection_string: The PostgreSQL connection string. If None, it
                will be loaded from the configuration.
            dimension: The dimension of the vectors to store.
            default_collection: The default collection to use.
        """
        self.dimension = dimension
        self.default_collection = default_collection
        self.connection_string = connection_string or config.database.connection_string

        # Create engine and session
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        self._create_tables()

        # Create default collection if it doesn't exist
        self._create_default_collection()

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        try:
            # Create extension if it doesn't exist
            with self.engine.connect() as conn:
                conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                conn.commit()

            # Create tables
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created or already exist")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def _create_default_collection(self) -> None:
        """Create the default collection if it doesn't exist."""
        with self.Session() as session:
            # Check if default collection exists
            collection = session.query(Collection).filter_by(name=self.default_collection).first()

            if not collection:
                # Create default collection
                collection = Collection(
                    name=self.default_collection, description="Default collection for memories"
                )
                session.add(collection)
                session.commit()
                logger.info(f"Created default collection: {self.default_collection}")

    async def add(
        self,
        content: str,
        metadata: Dict[str, Any] = None,
        embedding: Optional[Union[List[float], np.ndarray]] = None,
    ) -> str:
        """
        Add content to long-term memory.

        Args:
            content: The text content to store.
            metadata: Optional metadata to associate with the content.
            embedding: Optional pre-computed embedding vector.

        Returns:
            The ID of the newly created memory entry.
        """
        if metadata is None:
            metadata = {}

        # Generate embedding if not provided
        if embedding is None:
            embedding = await self.embedding_provider.get_embedding(content)

        # Insert into database
        memory_id = self._add_internal(content, embedding, metadata, self.default_collection)

        return memory_id

    def _add_internal(
        self,
        text: str,
        embedding: Union[List[float], np.ndarray],
        metadata: Dict[str, Any] = None,
        collection: Optional[str] = None,
    ) -> str:
        """
        Internal method to add a memory to the database.

        Args:
            text: The text content to store.
            embedding: The vector embedding of the text.
            metadata: Optional metadata to associate with the content.
            collection: The collection to store the memory in.

        Returns:
            The ID of the newly created memory entry.
        """
        if metadata is None:
            metadata = {}

        if collection is None:
            collection = self.default_collection

        # Add timestamp to metadata
        metadata["timestamp"] = time.time()

        with self.Session() as session:
            # Ensure collection exists
            self._ensure_collection_exists(session, collection)

            # Convert numpy array to list if necessary
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()

            # Create memory
            memory = Memory(
                text=text,
                embedding=embedding,
                meta_data=metadata,
                collection=collection,
            )

            # Add to database
            session.add(memory)
            session.commit()

            # Return ID
            return memory.id

    def _ensure_collection_exists(self, session: Session, collection_name: str) -> None:
        """
        Ensure that a collection exists, creating it if necessary.

        Args:
            session: The database session.
            collection_name: The name of the collection.
        """
        collection = session.query(Collection).filter_by(name=collection_name).first()

        if not collection:
            collection = Collection(
                name=collection_name, description=f"Collection: {collection_name}"
            )
            session.add(collection)
            session.flush()

    async def search(
        self,
        query: str,
        limit: int = 5,
        query_embedding: Optional[Union[List[float], np.ndarray]] = None,
        collection: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query.

        Args:
            query: The text query to search for.
            limit: Maximum number of results to return.
            query_embedding: Optional pre-computed embedding vector for the query.
            collection: The collection to search in. If None, uses the default collection.
            filter_metadata: Optional metadata filters to apply.

        Returns:
            A list of dictionaries containing the search results, ordered by relevance.
        """
        # Generate embedding if not provided
        if query_embedding is None:
            query_embedding = await self.embedding_provider.get_embedding(query)

        # Use default collection if not specified
        if collection is None:
            collection = self.default_collection

        # Search in database
        results = self._search_internal(query_embedding, limit, collection, filter_metadata)

        # Format results
        formatted_results = []
        for score, memory in results:
            formatted_results.append(
                {
                    "id": memory["id"],
                    "text": memory["text"],
                    "metadata": memory["meta_data"],
                    "score": score,
                }
            )

        return formatted_results

    def _search_internal(
        self,
        query_embedding: Union[List[float], np.ndarray],
        k: int = 5,
        collection: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Internal method to search for similar embeddings in the database.

        Args:
            query_embedding: The vector embedding to search for.
            k: Maximum number of results to return.
            collection: The collection to search in. If None, uses the default collection.
            filter_metadata: Optional metadata filters to apply.

        Returns:
            A list of tuples containing (similarity_score, memory_dict).
        """
        # Convert numpy array to list if necessary
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()

        # Use default collection if not specified
        if collection is None:
            collection = self.default_collection

        with self.Session() as session:
            # Build query
            query = (
                select(
                    Memory,
                    func.l2_distance(Memory.embedding, query_embedding).label("distance"),
                )
                .filter(Memory.collection == collection)
                .order_by("distance")
                .limit(k)
            )

            # Add metadata filters if provided
            if filter_metadata:
                for key, value in filter_metadata.items():
                    query = query.filter(Memory.meta_data[key].astext == str(value))

            # Execute query
            results = session.execute(query).all()

            # Format results
            return [
                (
                    1.0 / (1.0 + float(result.distance)),  # Convert distance to similarity score
                    {
                        "id": result.Memory.id,
                        "text": result.Memory.text,
                        "meta_data": result.Memory.meta_data,
                        "created_at": (
                            result.Memory.created_at.isoformat()
                            if result.Memory.created_at
                            else None
                        ),
                    },
                )
                for result in results
            ]

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: The ID of the memory to retrieve.

        Returns:
            The memory object if found, otherwise None.
        """
        with self.Session() as session:
            memory = session.query(Memory).filter_by(id=memory_id).first()

            if not memory:
                return None

            return {
                "id": memory.id,
                "text": memory.text,
                "embedding": memory.embedding,
                "meta_data": memory.meta_data,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat(),
                "collection": memory.collection,
            }

    def update(
        self,
        memory_id: str,
        text: Optional[str] = None,
        embedding: Optional[Union[List[float], np.ndarray]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update an existing memory.

        Args:
            memory_id: The ID of the memory to update.
            text: Optional new text content.
            embedding: Optional new embedding vector.
            metadata: Optional new metadata.

        Returns:
            True if the update was successful, False otherwise.
        """
        with self.Session() as session:
            memory = session.query(Memory).filter_by(id=memory_id).first()

            if not memory:
                return False

            if text is not None:
                memory.text = text

            if embedding is not None:
                # Convert numpy array to list if necessary
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                memory.embedding = embedding

            if metadata is not None:
                # Update timestamp
                metadata["timestamp"] = time.time()
                memory.meta_data = metadata

            session.commit()
            return True

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            True if the deletion was successful, False otherwise.
        """
        with self.Session() as session:
            memory = session.query(Memory).filter_by(id=memory_id).first()

            if not memory:
                return False

            session.delete(memory)
            session.commit()
            return True

    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections.

        Returns:
            A list of dictionaries containing collection information.
        """
        with self.Session() as session:
            collections = session.query(Collection).all()

            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                }
                for c in collections
            ]

    def create_collection(self, name: str, description: Optional[str] = None) -> str:
        """
        Create a new collection.

        Args:
            name: The name of the collection.
            description: Optional description of the collection.

        Returns:
            The ID of the newly created collection.
        """
        with self.Session() as session:
            # Check if collection already exists
            existing = session.query(Collection).filter_by(name=name).first()

            if existing:
                return existing.id

            # Create new collection
            collection = Collection(name=name, description=description or f"Collection: {name}")

            session.add(collection)
            session.commit()

            return collection.id

    def delete_collection(self, name: str, delete_memories: bool = False) -> bool:
        """
        Delete a collection.

        Args:
            name: The name of the collection to delete.
            delete_memories: Whether to also delete all memories in the
                collection.

        Returns:
            True if the collection was deleted, False if not found.
        """
        if name == self.default_collection:
            raise ValueError("Cannot delete the default collection")

        with self.Session() as session:
            collection = session.query(Collection).filter_by(name=name).first()

            if not collection:
                return False

            if delete_memories:
                # Delete all memories in the collection
                session.query(Memory).filter_by(collection=name).delete()
            else:
                # Move memories to default collection
                session.query(Memory).filter_by(collection=name).update(
                    {"collection": self.default_collection}
                )

            # Delete the collection
            session.delete(collection)
            session.commit()

            return True

    def get_recent_memories(
        self, limit: int = 10, collection: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the most recent memories.

        Args:
            limit: The maximum number of memories to return.
            collection: The collection to get memories from. If None, the
                default collection will be used.

        Returns:
            A list of dictionaries containing memory information.
        """
        collection_name = collection or self.default_collection

        with self.Session() as session:
            memories = (
                session.query(Memory)
                .filter_by(collection=collection_name)
                .order_by(desc(Memory.created_at))
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": m.id,
                    "text": m.text,
                    "meta_data": m.meta_data,
                    "created_at": m.created_at.isoformat(),
                    "updated_at": m.updated_at.isoformat(),
                    "collection": m.collection,
                }
                for m in memories
            ]
