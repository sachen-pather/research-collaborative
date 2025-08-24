"""
Intelligent caching system for performance optimization
"""
import hashlib
import json
import pickle
import os
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

class CacheManager:
    """Intelligent caching system with TTL and size management"""
    
    def __init__(self, cache_dir: str = "data/cache", max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = timedelta(hours=24)
        
        # Cache metadata
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
        
        return {"entries": {}, "total_size": 0, "created": datetime.now().isoformat()}
    
    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save cache metadata: {e}")
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: Dict[str, Any]) -> str:
        """Generate unique cache key"""
        # Create deterministic key from function name and arguments
        key_data = {
            'function': func_name,
            'args': str(args),
            'kwargs': sorted(kwargs.items()) if kwargs else []
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[Any]:
        """Retrieve item from cache"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            if not cache_file.exists():
                return None
            
            # Check if expired
            metadata_entry = self.metadata["entries"].get(cache_key)
            if metadata_entry:
                created_time = datetime.fromisoformat(metadata_entry["created"])
                ttl = timedelta(seconds=metadata_entry.get("ttl_seconds", self.default_ttl.total_seconds()))
                
                if datetime.now() - created_time > ttl:
                    logger.info(f"🗑️ Cache entry expired: {cache_key[:8]}...")
                    self._delete_entry(cache_key)
                    return None
            
            # Load cached data
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            logger.info(f"✅ Cache hit: {cache_key[:8]}...")
            return data
            
        except Exception as e:
            logger.warning(f"Failed to retrieve from cache {cache_key[:8]}...: {e}")
            return None
    
    def set(self, cache_key: str, data: Any, ttl: Optional[timedelta] = None) -> bool:
        """Store item in cache"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            # Check cache size limits
            self._cleanup_if_needed()
            
            # Serialize data
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # Update metadata
            file_size = cache_file.stat().st_size
            ttl_seconds = (ttl or self.default_ttl).total_seconds()
            
            self.metadata["entries"][cache_key] = {
                "created": datetime.now().isoformat(),
                "size": file_size,
                "ttl_seconds": ttl_seconds,
                "access_count": 1,
                "last_accessed": datetime.now().isoformat()
            }
            
            self.metadata["total_size"] += file_size
            self._save_metadata()
            
            logger.info(f"💾 Cached: {cache_key[:8]}... ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to cache {cache_key[:8]}...: {e}")
            return False
    
    def _delete_entry(self, cache_key: str):
        """Delete cache entry"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            if cache_file.exists():
                cache_file.unlink()
            
            if cache_key in self.metadata["entries"]:
                entry = self.metadata["entries"][cache_key]
                self.metadata["total_size"] -= entry.get("size", 0)
                del self.metadata["entries"][cache_key]
                self._save_metadata()
                
        except Exception as e:
            logger.warning(f"Failed to delete cache entry {cache_key[:8]}...: {e}")
    
    def _cleanup_if_needed(self):
        """Clean up cache if size limit exceeded"""
        if self.metadata["total_size"] <= self.max_size_bytes:
            return
        
        logger.info("🧹 Cache size limit exceeded, cleaning up...")
        
        # Sort entries by last access time (LRU)
        entries = list(self.metadata["entries"].items())
        entries.sort(key=lambda x: x[1].get("last_accessed", ""))
        
        # Remove oldest entries until under limit
        for cache_key, _ in entries:
            if self.metadata["total_size"] <= self.max_size_bytes * 0.8:  # Keep 20% buffer
                break
            
            self._delete_entry(cache_key)
            logger.info(f"🗑️ Removed old cache entry: {cache_key[:8]}...")
    
    def clear_expired(self):
        """Clear all expired entries"""
        logger.info("🧹 Clearing expired cache entries...")
        
        expired_keys = []
        now = datetime.now()
        
        for cache_key, entry in self.metadata["entries"].items():
            created_time = datetime.fromisoformat(entry["created"])
            ttl = timedelta(seconds=entry.get("ttl_seconds", self.default_ttl.total_seconds()))
            
            if now - created_time > ttl:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            self._delete_entry(cache_key)
        
        logger.info(f"🗑️ Cleared {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.metadata["entries"]),
            "total_size_mb": self.metadata["total_size"] / (1024 * 1024),
            "hit_rate": self._calculate_hit_rate(),
            "oldest_entry": self._get_oldest_entry(),
            "cache_utilization": self.metadata["total_size"] / self.max_size_bytes
        }
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_accesses = sum(entry.get("access_count", 0) for entry in self.metadata["entries"].values())
        return len(self.metadata["entries"]) / max(total_accesses, 1)
    
    def _get_oldest_entry(self) -> Optional[str]:
        """Get oldest cache entry timestamp"""
        if not self.metadata["entries"]:
            return None
        
        oldest_time = min(entry["created"] for entry in self.metadata["entries"].values())
        return oldest_time

def cached(ttl: Optional[timedelta] = None, cache_manager: Optional[CacheManager] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Use global cache manager if none provided
            cm = cache_manager or global_cache_manager
            
            # Generate cache key
            cache_key = cm._generate_cache_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            cached_result = cm.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cm.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Global cache manager instance
global_cache_manager = CacheManager()

# Cache cleanup on module import
global_cache_manager.clear_expired()
