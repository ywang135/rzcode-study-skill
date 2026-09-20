# Advanced Guide - RZCode Study Skill v2.0

This guide covers advanced topics including batch operations, performance optimization, error handling, troubleshooting, and migration from v1.0.

---

## 1. Batch Operations

### Strategy and Planning

Large-scale imports require careful planning to ensure data consistency and performance:

```python
def batch_import_strategy(books_config):
    """
    Execute batch import following best practices.
    
    Strategy:
    1. Validate all data before submission
    2. Import books first (no dependencies)
    3. Import chapters by book (depends on books)
    4. Import concepts independently
    5. Link relationships last
    """
    
    import json
    from datetime import datetime
    
    # Step 1: Validation
    print("Step 1: Validating data...")
    validation_results = validate_all_data(books_config)
    if validation_results['errors']:
        print(f"Validation failed: {validation_results['errors']}")
        return
    
    # Step 2: Import books
    print("Step 2: Importing books...")
    books_created = []
    for book_data in books_config:
        try:
            response = requests.post(
                "https://rzcode.vip/api/study/books",
                headers={"X-API-Key": api_key},
                json=book_data
            )
            response.raise_for_status()
            books_created.append(response.json())
            print(f"  ✓ {book_data['title']}")
        except Exception as e:
            print(f"  ✗ {book_data['title']}: {e}")
    
    # Step 3: Import chapters
    print(f"Step 3: Importing chapters for {len(books_created)} books...")
    chapters_created = []
    for book in books_created:
        chapters = books_config_chapters.get(book['id'], [])
        for chapter in chapters:
            chapter['book_title'] = book['title']
            try:
                response = requests.post(
                    "https://rzcode.vip/api/study/chapters",
                    headers={"X-API-Key": api_key},
                    json=chapter
                )
                response.raise_for_status()
                chapters_created.append(response.json())
            except Exception as e:
                print(f"  ✗ {chapter['title']}: {e}")
    
    # Step 4: Import concepts
    print("Step 4: Importing concepts...")
    concepts_created = []
    concepts_to_create = get_all_unique_concepts()
    
    for concept in concepts_to_create:
        # Deduplicate by canonical_name
        if concept_exists(concept['canonical_name']):
            print(f"  ~ {concept['name']} (already exists)")
            continue
        
        try:
            response = requests.post(
                "https://rzcode.vip/api/study/concepts",
                headers={"X-API-Key": api_key},
                json=concept
            )
            response.raise_for_status()
            concepts_created.append(response.json())
            print(f"  ✓ {concept['name']}")
        except Exception as e:
            print(f"  ✗ {concept['name']}: {e}")
    
    # Step 5: Link relationships
    print("Step 5: Creating relationships...")
    relationships_created = 0
    for rel_data in get_all_relationships():
        try:
            endpoint = rel_data['type']  # mentioned_in, related_to, prerequisite_for, part_of
            response = requests.post(
                f"https://rzcode.vip/api/study/relationships/{endpoint}",
                headers={"X-API-Key": api_key},
                json=rel_data['data']
            )
            response.raise_for_status()
            relationships_created += 1
        except Exception as e:
            print(f"  ⚠ Warning: {rel_data} - {e}")
    
    # Summary report
    print(f"\n{'='*60}")
    print(f"Batch Import Complete - {datetime.now().isoformat()}")
    print(f"  Books created: {len(books_created)}")
    print(f"  Chapters created: {len(chapters_created)}")
    print(f"  Concepts created: {len(concepts_created)}")
    print(f"  Relationships created: {relationships_created}")
    print(f"{'='*60}")
    
    return {
        "books": len(books_created),
        "chapters": len(chapters_created),
        "concepts": len(concepts_created),
        "relationships": relationships_created
    }

def validate_all_data(books_config):
    """Validate data before batch import."""
    errors = []
    warnings = []
    
    # Check for required fields
    for book in books_config:
        if not book.get('title'):
            errors.append(f"Book missing title")
        if not book.get('authors'):
            warnings.append(f"Book '{book.get('title')}' missing authors")
    
    # Check for duplicate titles
    titles = [b['title'] for b in books_config]
    if len(titles) != len(set(titles)):
        errors.append("Duplicate book titles found")
    
    # Check chapter hierarchy
    for book in books_config:
        chapters = books_config_chapters.get(book['id'], [])
        for chapter in chapters:
            if not chapter.get('title'):
                errors.append(f"Chapter in '{book['title']}' missing title")
            if not chapter.get('level'):
                errors.append(f"Chapter '{chapter.get('title')}' missing level")
    
    return {"errors": errors, "warnings": warnings}

def concept_exists(canonical_name):
    """Check if concept already exists (avoid duplicates)."""
    try:
        response = requests.get(
            f"https://rzcode.vip/api/study/concepts/{canonical_name}",
            headers={"X-API-Key": api_key}
        )
        return response.status_code == 200
    except:
        return False
```

### Batch Job Monitoring

```python
import json
from datetime import datetime

class BatchJobMonitor:
    """Monitor batch import jobs with logging and recovery."""
    
    def __init__(self, job_id):
        self.job_id = job_id
        self.log_file = f"batch_job_{job_id}.log"
        self.checkpoint_file = f"batch_job_{job_id}.checkpoint"
        self.start_time = datetime.now()
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
    
    def log_operation(self, operation_type, status, details):
        """Log each operation."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": operation_type,
            "status": status,
            "details": details
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def save_checkpoint(self, processed_items):
        """Save progress checkpoint for recovery."""
        checkpoint = {
            "job_id": self.job_id,
            "checkpoint_time": datetime.now().isoformat(),
            "processed_items": processed_items,
            "stats": self.stats
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)
    
    def resume_from_checkpoint(self):
        """Resume interrupted job."""
        try:
            with open(self.checkpoint_file) as f:
                checkpoint = json.load(f)
            return checkpoint["processed_items"]
        except FileNotFoundError:
            return []
    
    def get_report(self):
        """Generate final report."""
        duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "job_id": self.job_id,
            "duration_seconds": duration,
            "total_operations": self.stats["total"],
            "success": self.stats["success"],
            "failed": self.stats["failed"],
            "skipped": self.stats["skipped"],
            "success_rate": self.stats["success"] / max(self.stats["total"], 1) * 100
        }
```

---

## 2. Performance Optimization

### Query Optimization

```python
def optimized_concept_search(query):
    """
    Optimized search with client-side caching and batching.
    
    Techniques:
    - Cache frequently searched terms
    - Use pagination efficiently
    - Batch multiple queries
    """
    
    import time
    from functools import lru_cache
    
    # Simple in-memory cache
    search_cache = {}
    cache_ttl = 300  # 5 minutes
    
    @lru_cache(maxsize=100)
    def cached_search(query, limit=20):
        """Cache search results."""
        cache_key = f"{query}:{limit}"
        
        # Check cache
        if cache_key in search_cache:
            cached_entry = search_cache[cache_key]
            if time.time() - cached_entry['timestamp'] < cache_ttl:
                return cached_entry['data']
        
        # Fetch from API
        response = requests.get(
            "https://rzcode.vip/api/study/search",
            headers={"X-API-Key": api_key},
            params={"q": query, "limit": limit}
        )
        results = response.json()['results']
        
        # Store in cache
        search_cache[cache_key] = {
            'timestamp': time.time(),
            'data': results
        }
        
        return results
    
    return cached_search(query)

def batch_fetch_concepts(concept_names):
    """
    Fetch multiple concepts efficiently.
    
    Instead of N individual requests, batch similar operations.
    """
    
    concepts = {}
    not_found = []
    
    for name in concept_names:
        try:
            response = requests.get(
                f"https://rzcode.vip/api/study/concepts/{name}",
                headers={"X-API-Key": api_key}
            )
            if response.status_code == 200:
                concepts[name] = response.json()
            else:
                not_found.append(name)
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            not_found.append(name)
    
    return {
        "found": concepts,
        "not_found": not_found
    }

def efficient_pagination(endpoint, params=None, batch_size=100):
    """
    Efficiently fetch all results with proper pagination.
    
    Yields results as they come instead of loading everything.
    """
    params = params or {}
    offset = 0
    
    while True:
        params['limit'] = batch_size
        params['offset'] = offset
        
        response = requests.get(
            f"https://rzcode.vip/api/study{endpoint}",
            headers={"X-API-Key": api_key},
            params=params
        )
        
        data = response.json()
        
        # Extract results based on endpoint type
        if 'books' in data:
            results = data['books']
        elif 'chapters' in data:
            results = data['chapters']
        elif 'notes' in data:
            results = data['notes']
        elif 'results' in data:
            results = data['results']
        else:
            break
        
        if not results:
            break
        
        for item in results:
            yield item
        
        if len(results) < batch_size:
            break
        
        offset += batch_size
```

### Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    """
    Create requests session with connection pooling and retry strategy.
    
    Benefits:
    - Reuse connections
    - Automatic retry on transient failures
    - Better performance for batch operations
    """
    
    session = requests.Session()
    
    # Retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
        backoff_factor=1  # 1, 2, 4 second delays
    )
    
    # Mount adapters
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default headers
    session.headers.update({"X-API-Key": api_key})
    
    return session

# Usage
session = create_session_with_retry()

# Reuse session for multiple requests
response1 = session.get("https://rzcode.vip/api/study/books")
response2 = session.get("https://rzcode.vip/api/study/concepts/neural_network")
response3 = session.post("https://rzcode.vip/api/study/books", json={...})
```

---

## 3. Pagination Handling

### Complete Pagination Implementation

```python
class PaginationHandler:
    """Handle all pagination scenarios."""
    
    def __init__(self, api_url, api_key, batch_size=100):
        self.api_url = api_url
        self.api_key = api_key
        self.batch_size = batch_size
        self.session = self._create_session()
    
    def _create_session(self):
        """Create session with retry logic."""
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.headers.update({"X-API-Key": self.api_key})
        return session
    
    def fetch_all(self, endpoint, params=None):
        """
        Fetch all results from a paginated endpoint.
        
        Args:
            endpoint: API endpoint (e.g., "/books", "/chapters")
            params: Optional query parameters
        
        Returns:
            List of all results
        """
        all_results = []
        offset = 0
        
        while True:
            query_params = params or {}
            query_params['limit'] = self.batch_size
            query_params['offset'] = offset
            
            response = self.session.get(
                f"{self.api_url}{endpoint}",
                params=query_params
            )
            response.raise_for_status()
            
            data = response.json()
            results = self._extract_results(data)
            
            if not results:
                break
            
            all_results.extend(results)
            
            if len(results) < self.batch_size:
                break
            
            offset += self.batch_size
            print(f"  Fetched {len(all_results)} items...")
        
        return all_results
    
    def fetch_iterator(self, endpoint, params=None):
        """
        Fetch results as an iterator (memory efficient).
        
        Yields one result at a time instead of loading all at once.
        """
        offset = 0
        
        while True:
            query_params = params or {}
            query_params['limit'] = self.batch_size
            query_params['offset'] = offset
            
            response = self.session.get(
                f"{self.api_url}{endpoint}",
                params=query_params
            )
            response.raise_for_status()
            
            data = response.json()
            results = self._extract_results(data)
            
            if not results:
                break
            
            for item in results:
                yield item
            
            if len(results) < self.batch_size:
                break
            
            offset += self.batch_size
    
    def _extract_results(self, response_data):
        """Extract results from various response formats."""
        if 'books' in response_data:
            return response_data['books']
        elif 'chapters' in response_data:
            return response_data['chapters']
        elif 'notes' in response_data:
            return response_data['notes']
        elif 'results' in response_data:
            return response_data['results']
        else:
            return []

# Usage examples

# Fetch all books
paginator = PaginationHandler("https://rzcode.vip/api/study", api_key)
all_books = paginator.fetch_all("/books")
print(f"Total books: {len(all_books)}")

# Fetch all chapters with iterator (memory efficient)
all_chapters = []
for chapter in paginator.fetch_iterator("/books/Deep%20Learning/chapters"):
    all_chapters.append(chapter)
    if len(all_chapters) % 50 == 0:
        print(f"Processed {len(all_chapters)} chapters...")
```

---

## 4. Error Handling and Resilience

### Comprehensive Error Handling

```python
import time
from enum import Enum
from dataclasses import dataclass

class ErrorCategory(Enum):
    """Classification of API errors."""
    VALIDATION_ERROR = "validation"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMITED = "rate_limited"
    SERVER_ERROR = "server_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown"

@dataclass
class APIError:
    """Structured error information."""
    category: ErrorCategory
    code: str
    message: str
    status_code: int
    details: dict = None
    retriable: bool = False

def classify_error(exception, response=None):
    """Classify errors for appropriate handling."""
    
    if isinstance(exception, requests.exceptions.Timeout):
        return APIError(
            category=ErrorCategory.NETWORK_ERROR,
            code="TIMEOUT",
            message="Request timeout",
            status_code=0,
            retriable=True
        )
    
    if isinstance(exception, requests.exceptions.ConnectionError):
        return APIError(
            category=ErrorCategory.NETWORK_ERROR,
            code="CONNECTION_ERROR",
            message="Connection failed",
            status_code=0,
            retriable=True
        )
    
    if response is None:
        return APIError(
            category=ErrorCategory.UNKNOWN_ERROR,
            code="UNKNOWN",
            message=str(exception),
            status_code=0
        )
    
    status_code = response.status_code
    try:
        error_data = response.json()
    except:
        error_data = {}
    
    # Classification by status code
    if status_code == 400:
        return APIError(
            category=ErrorCategory.VALIDATION_ERROR,
            code=error_data.get('error', 'BAD_REQUEST'),
            message=error_data.get('message', 'Invalid request'),
            status_code=status_code,
            details=error_data.get('details', {}),
            retriable=False
        )
    
    elif status_code == 401:
        return APIError(
            category=ErrorCategory.VALIDATION_ERROR,
            code="UNAUTHORIZED",
            message="Invalid or missing API key",
            status_code=status_code,
            retriable=False
        )
    
    elif status_code == 404:
        return APIError(
            category=ErrorCategory.NOT_FOUND,
            code="NOT_FOUND",
            message=error_data.get('message', 'Resource not found'),
            status_code=status_code,
            retriable=False
        )
    
    elif status_code == 409:
        return APIError(
            category=ErrorCategory.CONFLICT,
            code="CONFLICT",
            message=error_data.get('message', 'Resource conflict'),
            status_code=status_code,
            retriable=False
        )
    
    elif status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        return APIError(
            category=ErrorCategory.RATE_LIMITED,
            code="RATE_LIMITED",
            message="Rate limit exceeded",
            status_code=status_code,
            details={'retry_after': retry_after},
            retriable=True
        )
    
    elif status_code >= 500:
        return APIError(
            category=ErrorCategory.SERVER_ERROR,
            code=error_data.get('error', 'SERVER_ERROR'),
            message=error_data.get('message', 'Server error'),
            status_code=status_code,
            retriable=True
        )
    
    return APIError(
        category=ErrorCategory.UNKNOWN_ERROR,
        code="UNKNOWN",
        message=str(exception),
        status_code=status_code
    )

def api_call_with_retry(method, endpoint, max_retries=3, **kwargs):
    """
    Make API call with automatic retry and backoff.
    
    Strategies:
    - Exponential backoff for retriable errors
    - Skip retries for non-retriable errors
    - Respect rate limit headers
    """
    
    base_url = "https://rzcode.vip/api/study"
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.request(
                method,
                f"{base_url}{endpoint}",
                headers={"X-API-Key": api_key},
                timeout=10,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.text else None
        
        except (requests.exceptions.RequestException, Exception) as e:
            error = classify_error(e, response if 'response' in locals() else None)
            
            # Log error
            print(f"[Attempt {attempt + 1}/{max_retries + 1}] "
                  f"{error.category.value}: {error.message}")
            
            # Don't retry non-retriable errors
            if not error.retriable:
                raise
            
            # Last attempt failed
            if attempt == max_retries:
                raise
            
            # Calculate backoff
            if error.category == ErrorCategory.RATE_LIMITED:
                wait_time = error.details.get('retry_after', 2 ** attempt)
            else:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8...
            
            print(f"  Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
```

### Transactional-style Operations

```python
class TransactionalBatchOperation:
    """
    Perform batch operations with transaction-like semantics.
    
    If any operation fails critically, can rollback previous operations.
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.operations = []
        self.results = []
        self.rollback_stack = []
    
    def add_operation(self, method, endpoint, data, rollback_endpoint=None):
        """
        Add operation to batch.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            rollback_endpoint: Endpoint to call for rollback (e.g., DELETE)
        """
        self.operations.append({
            'method': method,
            'endpoint': endpoint,
            'data': data,
            'rollback_endpoint': rollback_endpoint
        })
    
    def execute(self, stop_on_error=False):
        """
        Execute all operations.
        
        Args:
            stop_on_error: If True, stop on first error and rollback
        """
        for op in self.operations:
            try:
                response = requests.request(
                    op['method'],
                    f"https://rzcode.vip/api/study{op['endpoint']}",
                    headers={"X-API-Key": self.api_key},
                    json=op['data']
                )
                response.raise_for_status()
                result = response.json()
                self.results.append({'status': 'success', 'result': result})
                
                # Store for potential rollback
                if op['rollback_endpoint']:
                    self.rollback_stack.append({
                        'method': 'DELETE',
                        'endpoint': op['rollback_endpoint'],
                        'id': result.get('id')
                    })
            
            except Exception as e:
                self.results.append({'status': 'failed', 'error': str(e)})
                
                if stop_on_error:
                    print(f"Error during batch operation: {e}")
                    print(f"Rolling back {len(self.rollback_stack)} operations...")
                    self.rollback()
                    return False
        
        return True
    
    def rollback(self):
        """Rollback all successful operations."""
        for op in reversed(self.rollback_stack):
            try:
                response = requests.delete(
                    f"https://rzcode.vip/api/study{op['endpoint']}",
                    headers={"X-API-Key": self.api_key}
                )
                response.raise_for_status()
                print(f"  ✓ Rolled back: {op['endpoint']}")
            except Exception as e:
                print(f"  ⚠ Rollback failed for {op['endpoint']}: {e}")
        
        self.rollback_stack = []

# Usage
transaction = TransactionalBatchOperation(api_key)

# Add operations
transaction.add_operation(
    "POST", "/books",
    {"title": "New Book", "authors": ["Author"]},
    rollback_endpoint="/books/New%20Book"
)
transaction.add_operation(
    "POST", "/chapters",
    {"book_title": "New Book", "title": "Chapter 1", "level": 1, "order": 1}
)

# Execute with automatic rollback on error
if not transaction.execute(stop_on_error=True):
    print("Batch operation failed and rolled back")
```

---

## 5. Troubleshooting Guide

### Common Issues and Solutions

```python
# Issue 1: Authentication fails
# Solution: Verify API key and header format
def verify_authentication():
    """Verify API key is valid."""
    try:
        response = requests.get(
            "https://rzcode.vip/api/study/graph-stats",
            headers={"X-API-Key": api_key}
        )
        if response.status_code == 401:
            print("ERROR: Invalid API key")
            print("  - Check config.json")
            print("  - Verify X-API-Key header is set")
            return False
        print("✓ Authentication successful")
        return True
    except Exception as e:
        print(f"ERROR: Cannot connect to API: {e}")
        return False

# Issue 2: Rate limiting
# Solution: Implement backoff and respect rate limit headers
def handle_rate_limiting(response):
    """Handle 429 Too Many Requests."""
    remaining = response.headers.get('X-RateLimit-Remaining')
    reset_time = response.headers.get('X-RateLimit-Reset')
    
    print(f"Rate limited!")
    print(f"  Remaining requests: {remaining}")
    print(f"  Reset time: {reset_time}")
    print(f"  Recommendation: Wait {reset_time - time.time():.0f} seconds before retrying")

# Issue 3: Data validation errors
# Solution: Validate data before submission
def validate_book_data(book):
    """Validate book data before creating."""
    errors = []
    
    if not book.get('title'):
        errors.append("Missing required field: title")
    
    if not book.get('authors'):
        errors.append("Missing recommended field: authors (should be array)")
    elif not isinstance(book['authors'], list):
        errors.append("Field 'authors' should be array, got: " + type(book['authors']).__name__)
    
    if 'edition' in book and not isinstance(book['edition'], str):
        errors.append("Field 'edition' should be string")
    
    return errors

# Issue 4: Duplicate concepts
# Solution: Check before creating
def check_concept_exists(name, canonical_name):
    """Check if concept already exists."""
    try:
        response = requests.get(
            f"https://rzcode.vip/api/study/concepts/{canonical_name}",
            headers={"X-API-Key": api_key}
        )
        if response.status_code == 200:
            print(f"✓ Concept '{name}' already exists")
            return True
        return False
    except:
        return False

# Issue 5: File upload fails
# Solution: Verify file format and size
def validate_file_for_upload(file_path):
    """Validate file before upload."""
    import os
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    max_size = 100 * 1024 * 1024  # 100MB
    
    if file_size > max_size:
        print(f"ERROR: File too large ({file_size} bytes, max {max_size})")
        return False
    
    # Check format
    supported_formats = ['.pdf', '.txt', '.md']
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() not in supported_formats:
        print(f"ERROR: Unsupported file format: {ext}")
        print(f"  Supported: {', '.join(supported_formats)}")
        return False
    
    print(f"✓ File validation passed: {file_size} bytes")
    return True
```

### Debugging Techniques

```python
def enable_debug_logging():
    """Enable detailed logging for debugging."""
    import logging
    
    # Enable requests logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)
    
    # Log all API requests
    http_log = logging.getLogger("http.client")
    http_log.setLevel(logging.DEBUG)
    
    def log_request_details(method, url, headers=None, data=None):
        """Log request details."""
        logger = logging.getLogger("api_debug")
        logger.debug(f"\n{'='*60}")
        logger.debug(f"REQUEST: {method} {url}")
        if headers:
            for k, v in headers.items():
                if k != 'X-API-Key':  # Don't log sensitive data
                    logger.debug(f"  {k}: {v}")
        if data:
            logger.debug(f"  Body: {str(data)[:200]}...")
        logger.debug(f"{'='*60}")
    
    return log_request_details

def diagnose_api_health():
    """Check API health and provide diagnostics."""
    print("Diagnosing API health...")
    
    checks = {
        "Authentication": verify_authentication,
        "Basic connectivity": lambda: requests.get(
            "https://rzcode.vip/api/study/graph-stats",
            headers={"X-API-Key": api_key}
        ).status_code == 200,
        "Book operations": lambda: requests.get(
            "https://rzcode.vip/api/study/books",
            headers={"X-API-Key": api_key}
        ).status_code == 200,
    }
    
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {check_name}")
        except Exception as e:
            print(f"✗ ERROR: {check_name} - {e}")
```

---

## 6. Migration from v1.0

### Comparison of Versions

| Feature | v1.0 | v2.0 |
|---------|------|------|
| API Backend | Local/Self-hosted | Cloud REST API |
| Authentication | Optional | Required X-API-Key |
| Base URL | /api/* | https://rzcode.vip/api/study |
| Note Storage | File-based | Cloud storage |
| File Upload | Form data | Multipart/form-data |
| Batch Operations | Limited | Full support |
| Rate Limiting | N/A | 1000 req/hour |
| Pagination | Manual | Automatic |
| Error Handling | Variable | Standard JSON format |

### Migration Path

```python
def migrate_from_v1_to_v2():
    """
    Migrate data and workflows from v1.0 to v2.0.
    
    Steps:
    1. Export books from v1.0
    2. Export chapters from v1.0
    3. Export concepts from v1.0
    4. Transform and validate data
    5. Import to v2.0 API
    """
    
    # Step 1: Read v1.0 data files
    import json
    import glob
    
    v1_data = {
        'books': [],
        'chapters': [],
        'concepts': [],
        'notes': []
    }
    
    # Extract books
    for book_file in glob.glob('./v1.0/data/books/*.json'):
        with open(book_file) as f:
            v1_data['books'].append(json.load(f))
    
    # Step 2: Transform data to v2.0 format
    v2_data = {
        'books': [],
        'chapters': [],
        'concepts': [],
        'notes': []
    }
    
    for book in v1_data['books']:
        # Add API key requirement
        v2_book = {
            'title': book['title'],
            'authors': book.get('authors', []),
            'edition': book.get('edition'),
            'file_path': book.get('file_path')
        }
        v2_data['books'].append(v2_book)
    
    # Step 3: Validate v2 data
    print(f"Migrating {len(v1_data['books'])} books...")
    print(f"Migrating {len(v1_data['concepts'])} concepts...")
    
    # Step 4: Upload to v2.0
    print("\nUploading to v2.0 API...")
    successful = 0
    failed = 0
    
    for book in v2_data['books']:
        try:
            response = requests.post(
                "https://rzcode.vip/api/study/books",
                headers={"X-API-Key": api_key},
                json=book
            )
            response.raise_for_status()
            successful += 1
            print(f"  ✓ {book['title']}")
        except Exception as e:
            failed += 1
            print(f"  ✗ {book['title']}: {e}")
    
    print(f"\nMigration complete: {successful} successful, {failed} failed")

# Data transformation helpers

def transform_book_v1_to_v2(v1_book):
    """Transform book from v1.0 to v2.0 format."""
    return {
        'title': v1_book['name'],  # name -> title
        'authors': v1_book.get('author', []),
        'edition': v1_book.get('version'),
        'file_path': v1_book.get('path')
    }

def transform_concept_v1_to_v2(v1_concept):
    """Transform concept from v1.0 to v2.0 format."""
    return {
        'name': v1_concept['title'],
        'canonical_name': v1_concept.get('id', v1_concept['title'].lower().replace(' ', '_')),
        'kind': v1_concept.get('type', 'concept'),
        'definition': v1_concept.get('description', ''),
        'aliases': v1_concept.get('aliases', []),
        'summary': v1_concept.get('summary')
    }
```

---

## Best Practices Summary

1. **Batch Operations**: Always validate before submission, process in dependency order
2. **Performance**: Use connection pooling, implement caching, batch similar requests
3. **Error Handling**: Classify errors, implement exponential backoff, log comprehensively
4. **Pagination**: Use iterators for large datasets, respect rate limits
5. **Data Quality**: Validate before creation, check for duplicates, maintain referential integrity
6. **Monitoring**: Log all operations, track metrics, implement health checks
7. **Security**: Never log API keys, validate input, use HTTPS only
8. **Testing**: Test with small batches first, validate results, document edge cases

---

## Additional Resources

- [Workflow Guide](10-workflow.md) - Common workflows and patterns
- [Tools Reference](20-tools.md) - Complete API documentation
- [Overview](00-overview.md) - Architecture and core concepts
- Examples: See [examples/](../examples/) directory
