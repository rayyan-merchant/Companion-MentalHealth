"""
Production-Grade Multi-Provider Embedding Service

Provides embeddings from multiple cloud providers with automatic failover:
1. HuggingFace Inference API (Primary - 3 keys)
2. Jina AI Embeddings (Fallback 1)
3. Google Gemini Embeddings (Fallback 2)

Features:
- Automatic key rotation within each provider
- Provider-level failover when all keys exhausted
- Circuit breaker pattern to skip failing providers
- Configurable retry logic
"""

import os
import time
import random
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ProviderHealth:
    """Tracks the health status of each provider for circuit breaker pattern."""
    failures: int = 0
    last_failure: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    
    def record_failure(self, cooldown_seconds: int = 60):
        self.failures += 1
        self.last_failure = datetime.utcnow()
        # After 3 failures, put provider on cooldown
        if self.failures >= 3:
            self.cooldown_until = datetime.utcnow() + timedelta(seconds=cooldown_seconds)
    
    def record_success(self):
        self.failures = 0
        self.last_failure = None
        self.cooldown_until = None
    
    def is_available(self) -> bool:
        if self.cooldown_until and datetime.utcnow() < self.cooldown_until:
            return False
        return True


class EmbeddingProvider:
    """Base class for embedding providers."""
    
    def __init__(self, name: str, keys: List[str]):
        self.name = name
        self.keys = keys
        self.current_key_index = 0
        self.health = ProviderHealth()
    
    def get_next_key(self) -> Optional[str]:
        if not self.keys:
            return None
        key = self.keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        return key
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        raise NotImplementedError


class HuggingFaceProvider(EmbeddingProvider):
    """HuggingFace Inference API provider using InferenceClient."""
    
    def __init__(self, keys: List[str]):
        super().__init__("HuggingFace", keys)
        self.model = "sentence-transformers/all-MiniLM-L6-v2"
        self._clients = {}  # Cache clients per key
    
    def _get_client(self, key: str):
        """Get or create an InferenceClient for the given key."""
        if key not in self._clients:
            try:
                from huggingface_hub import InferenceClient
                self._clients[key] = InferenceClient(
                    provider="hf-inference",
                    api_key=key,
                )
            except ImportError:
                print(f"[{self.name}] huggingface_hub not installed, falling back to REST API")
                return None
        return self._clients[key]
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        for attempt in range(len(self.keys)):
            key = self.get_next_key()
            if not key:
                return None
            
            try:
                client = self._get_client(key)
                if client is None:
                    continue
                
                result = client.feature_extraction(
                    text,
                    model=self.model,
                )
                
                # Convert numpy array to list if needed
                if hasattr(result, 'tolist'):
                    result = result.tolist()
                
                if isinstance(result, list) and len(result) > 0:
                    # Handle nested list (batch response)
                    if isinstance(result[0], list):
                        self.health.record_success()
                        return result[0]
                    else:
                        self.health.record_success()
                        return result
                        
            except Exception as e:
                print(f"[{self.name}] Error with key ...{key[-4:]}: {e}")
                time.sleep(1)  # Small delay before retry
                continue
        
        self.health.record_failure()
        return None


class JinaProvider(EmbeddingProvider):
    """Jina AI Embeddings provider."""
    
    def __init__(self, keys: List[str]):
        super().__init__("Jina", keys)
        self.api_url = "https://api.jina.ai/v1/embeddings"
        self.model = "jina-embeddings-v3"
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        for _ in range(len(self.keys)):
            key = self.get_next_key()
            if not key:
                return None
            
            try:
                response = requests.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": [text]
                    },
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    embedding = data["data"][0].get("embedding")
                    if embedding:
                        self.health.record_success()
                        return embedding
                        
            except Exception as e:
                print(f"[{self.name}] Error with key ...{key[-4:]}: {e}")
                continue
        
        self.health.record_failure()
        return None


class GeminiProvider(EmbeddingProvider):
    """Google Gemini Embeddings provider."""
    
    def __init__(self, keys: List[str]):
        super().__init__("Gemini", keys)
        self.model = "gemini-embedding-001"
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        for _ in range(len(self.keys)):
            key = self.get_next_key()
            if not key:
                return None
            
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent?key={key}"
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": f"models/{self.model}",
                        "content": {"parts": [{"text": text}]}
                    },
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                if "embedding" in data and "values" in data["embedding"]:
                    self.health.record_success()
                    return data["embedding"]["values"]
                        
            except Exception as e:
                print(f"[{self.name}] Error with key ...{key[-4:]}: {e}")
                continue
        
        self.health.record_failure()
        return None


class MultiProviderEmbeddingService:
    """
    Production-grade embedding service with multi-provider failover.
    
    Strategy:
    1. Try primary provider (HuggingFace) first
    2. If failed, try Jina
    3. If failed, try Gemini
    4. Circuit breaker pattern skips providers that have failed repeatedly
    """
    
    def __init__(self):
        # Load keys from environment
        hf_keys = self._parse_keys(os.getenv("HF_TOKEN", ""))
        jina_keys = self._parse_keys(os.getenv("JINA_API_KEY", ""))
        gemini_keys = self._parse_keys(os.getenv("GEMINI_API_KEY", ""))
        
        self.providers: List[EmbeddingProvider] = []
        
        if hf_keys:
            self.providers.append(HuggingFaceProvider(hf_keys))
            print(f"[Embeddings] HuggingFace: {len(hf_keys)} keys loaded")
        
        if jina_keys:
            self.providers.append(JinaProvider(jina_keys))
            print(f"[Embeddings] Jina: {len(jina_keys)} keys loaded")
        
        if gemini_keys:
            self.providers.append(GeminiProvider(gemini_keys))
            print(f"[Embeddings] Gemini: {len(gemini_keys)} keys loaded")
        
        if not self.providers:
            print("[Embeddings] WARNING: No embedding providers configured!")
    
    def _parse_keys(self, key_string: str) -> List[str]:
        if not key_string:
            return []
        return [k.strip() for k in key_string.split(",") if k.strip()]
    
    def get_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        Get embedding with automatic failover across providers.
        Returns None only if ALL providers fail.
        
        Args:
            text: Text to embed
            use_cache: If True, check cache first and store result in cache
        """
        # Check cache first (if enabled)
        if use_cache:
            cached = self._get_from_cache(text)
            if cached is not None:
                return cached
        
        # Try each provider
        for provider in self.providers:
            if not provider.health.is_available():
                print(f"[Embeddings] Skipping {provider.name} (circuit breaker active)")
                continue
            
            embedding = provider.get_embedding(text)
            if embedding:
                # Store in cache for future use
                if use_cache:
                    self._store_in_cache(text, embedding)
                return embedding
            
            print(f"[Embeddings] {provider.name} failed, trying next provider...")
        
        print("[Embeddings] CRITICAL: All providers failed!")
        return None
    
    def _get_from_cache(self, text: str) -> Optional[List[float]]:
        """Check vector store cache for existing embedding."""
        try:
            from agents.vector_store import get_vector_store
            return get_vector_store().get_cached_embedding(text)
        except Exception:
            return None
    
    def _store_in_cache(self, text: str, embedding: List[float]):
        """Store embedding in vector store cache."""
        try:
            from agents.vector_store import get_vector_store
            get_vector_store().cache_embedding(text, embedding)
        except Exception:
            pass  # Cache failures shouldn't break the main flow
    
    def get_batch_embeddings(self, texts: List[str], use_cache: bool = True) -> List[Optional[List[float]]]:
        """
        Get embeddings for multiple texts with caching.
        
        Optimizations:
        - Checks cache for all texts first
        - Only fetches missing embeddings from providers
        - Stores new embeddings in cache
        """
        results = [None] * len(texts)
        texts_to_fetch = []
        fetch_indices = []
        
        # Check cache for each text
        if use_cache:
            for i, text in enumerate(texts):
                cached = self._get_from_cache(text)
                if cached is not None:
                    results[i] = cached
                else:
                    texts_to_fetch.append(text)
                    fetch_indices.append(i)
        else:
            texts_to_fetch = texts
            fetch_indices = list(range(len(texts)))
        
        # Fetch missing embeddings
        for j, text in enumerate(texts_to_fetch):
            embedding = self.get_embedding(text, use_cache=False)  # Already handling cache
            results[fetch_indices[j]] = embedding
            if embedding and use_cache:
                self._store_in_cache(text, embedding)
        
        return results


# Singleton instance
_embedding_service: Optional[MultiProviderEmbeddingService] = None


def get_embedding_service() -> MultiProviderEmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = MultiProviderEmbeddingService()
    return _embedding_service


def get_embedding(text: str, use_cache: bool = True) -> Optional[List[float]]:
    """
    Convenience function to get embedding for a single text.
    
    Uses caching by default to avoid redundant API calls.
    """
    return get_embedding_service().get_embedding(text, use_cache=use_cache)

