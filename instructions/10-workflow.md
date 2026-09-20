# Workflow Guide - RZCode Study Skill v2.0

**Overview**: This guide covers common workflows for managing knowledge bases using the RZCode Study Skill API backend.

## Prerequisites

- API Key configured in `~/.rzcode/config.json`
- Python 3.7+ with `requests` library
- Base URL: `https://rzcode.vip/api/study` (production) or `http://localhost:8000/api/study` (development)

```python
import requests
import json
import os

# Load configuration
def load_config():
    with open(os.path.expanduser("~/.rzcode/config.json")) as f:
        config = json.load(f)
    return config

# Initialize API client
config = load_config()
API_URL = config.get("api_host", "https://rzcode.vip") + "/api/study"
HEADERS = {"X-API-Key": config["api_key"]}

def api_call(method, endpoint, **kwargs):
    """Make an API call with proper headers."""
    url = f"{API_URL}{endpoint}"
    kwargs["headers"] = HEADERS
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response.json() if response.text else None
```

---

## Workflow 1: Import Book from PDF/File

**Goal**: Upload a book file and create structured chapters.

**Duration**: 10-15 minutes per book

### Steps

1. **Create the book entry**
2. **Upload book file** (PDF or text)
3. **Parse and create chapters**
4. **Link concepts within chapters**

### Tools Used

- `upsert_book` - Create/update book metadata
- `upload_book` - Upload book file
- `upsert_chapter` - Create chapter hierarchy
- `upsert_mentioned_in` - Link concepts to chapters

### Example Code

```python
def import_book_workflow(book_info, file_path):
    """
    Complete workflow to import a book with chapters and concepts.
    
    Args:
        book_info: {
            "title": "Deep Learning",
            "authors": ["Ian Goodfellow"],
            "edition": "1st Edition"
        }
        file_path: Path to book file
    """
    
    # Step 1: Create book entry
    print(f"Creating book: {book_info['title']}")
    book = api_call("POST", "/books", json=book_info)
    print(f"✓ Book created: {book['id']}")
    
    # Step 2: Upload book file
    print(f"Uploading file: {file_path}")
    with open(file_path, 'rb') as f:
        files = {'file': f}
        upload = requests.post(
            f"{API_URL}/books/{book_info['title']}/upload",
            headers={"X-API-Key": HEADERS["X-API-Key"]},
            files=files
        )
        upload.raise_for_status()
    print("✓ File uploaded")
    
    # Step 3: Create chapters (example for 3-level hierarchy)
    chapters_data = [
        {
            "book_title": book_info["title"],
            "title": "Part I: Foundations",
            "level": 1,
            "order": 1,
            "summary": "Basic concepts and mathematics"
        },
        {
            "book_title": book_info["title"],
            "title": "Linear Algebra",
            "level": 2,
            "order": 1,
            "parent_title": "Part I: Foundations",
            "summary": "Vectors, matrices, and eigenvalues"
        }
    ]
    
    for chapter in chapters_data:
        print(f"Creating chapter: {chapter['title']}")
        api_call("POST", "/chapters", json=chapter)
    
    print("✓ Book import complete")
    return book

# Usage
book_info = {
    "title": "Deep Learning",
    "authors": ["Ian Goodfellow", "Yoshua Bengio"],
    "edition": "1st Edition"
}
book = import_book_workflow(book_info, "./deeplearning.pdf")
```

### Best Practices

- **Validate file format** before uploading (PDF, TXT, MD supported)
- **Use meaningful chapter titles** that match the book's structure
- **Set correct levels and order** for proper hierarchy (level 1 = top level)
- **Add summaries** for better context in searches

---

## Workflow 2: Extract and Link Concepts

**Goal**: Extract concepts from a chapter and establish relationships.

**Duration**: 15-20 minutes per chapter

### Steps

1. **Identify concepts** in the chapter (manual or automated)
2. **Create concept definitions**
3. **Link concepts to the chapter** (mentioned_in relationship)
4. **Establish concept relationships** (related_to, prerequisite_for)

### Tools Used

- `upsert_concept` - Create/update concepts
- `upsert_mentioned_in` - Link concept to chapter
- `upsert_related_to` - Link concept to concept
- `upsert_prerequisite_for` - Establish learning path

### Example Code

```python
def extract_concepts_workflow(book_title, chapter_title, concepts):
    """
    Extract and link concepts for a chapter.
    
    Args:
        book_title: Name of the book
        chapter_title: Name of the chapter
        concepts: List of concept definitions
    """
    
    created_concepts = []
    
    # Step 1: Create concepts
    print(f"Processing {len(concepts)} concepts for {chapter_title}")
    for concept in concepts:
        print(f"  Creating concept: {concept['name']}")
        
        # Add canonical_name if not provided
        if "canonical_name" not in concept:
            concept["canonical_name"] = concept["name"].lower().replace(" ", "_")
        
        result = api_call("POST", "/concepts", json=concept)
        created_concepts.append(concept["name"])
    
    # Step 2: Link concepts to chapter
    print(f"Linking {len(created_concepts)} concepts to chapter")
    for concept_name in created_concepts:
        api_call("POST", "/relationships/mentioned_in", json={
            "concept_title": concept_name,
            "chapter_title": chapter_title,
            "role": "introduced",
            "source": "agent"
        })
    
    # Step 3: Establish concept relationships
    print("Establishing concept relationships")
    relationships = [
        {
            "concept_title_1": "Gradient Descent",
            "concept_title_2": "Backpropagation",
            "relationship": "used_by"
        }
    ]
    
    for rel in relationships:
        try:
            api_call("POST", "/relationships/related_to", json=rel)
        except Exception as e:
            print(f"  ⚠ Warning: {e}")
    
    print(f"✓ Concept extraction complete: {len(created_concepts)} concepts")
    return created_concepts

# Usage
concepts = [
    {
        "name": "Gradient Descent",
        "kind": "method",
        "definition": "An optimization algorithm that iteratively moves in the direction of steepest descent",
        "aliases": ["GD", "Steepest Descent"],
        "summary": "Core optimization technique in machine learning"
    }
]

concepts_created = extract_concepts_workflow(
    "Deep Learning",
    "Optimization Algorithms",
    concepts
)
```

### Best Practices

- **Use consistent naming** for concepts (capitalized, descriptive)
- **Provide canonical names** for unique identification across the system
- **Set concept kinds** appropriately (method, theorem, definition, concept, etc.)
- **Include aliases** for alternative names
- **Document relationships explicitly** for better knowledge graph navigation

---

## Workflow 3: Add and Manage Notes

**Goal**: Attach detailed notes, examples, and annotations to books, chapters, or concepts.

**Duration**: 5-10 minutes per note

### Steps

1. **Create text notes** (inline content)
2. **Upload file notes** (external files: MD, PDF, etc.)
3. **Link notes to nodes** (books, chapters, concepts)
4. **Organize with tags** and descriptions

### Tools Used

- `create_note` - Create inline text notes
- `upload_note` - Upload file-based notes
- `list_notes` - Retrieve notes for a node
- `get_note` - Fetch specific note content

### Example Code

```python
def add_notes_workflow(node_type, node_identifier):
    """
    Add comprehensive notes to a node.
    
    Args:
        node_type: "book", "chapter", or "concept"
        node_identifier: Book title, chapter title, or concept name
    """
    
    print(f"Adding notes to {node_type}: {node_identifier}")
    
    # Step 1: Add inline text notes
    text_notes = [
        {
            "title": "Key Takeaways",
            "content": "## Main Ideas\n- Concept A is fundamental\n",
            "file_type": "md",
            "description": "Summary of main learning points"
        }
    ]
    
    created_notes = []
    for note in text_notes:
        print(f"  Creating text note: {note['title']}")
        result = api_call("POST", "/notes", json={
            "node_type": node_type,
            "node_identifier": node_identifier,
            "title": note["title"],
            "content": note["content"],
            "file_type": note.get("file_type", "md"),
            "description": note.get("description", "")
        })
        created_notes.append(result["id"])
    
    # Step 2: List and verify notes
    print(f"Listing all notes for {node_identifier}")
    notes_list = api_call("GET", f"/notes?node_type={node_type}&node_identifier={node_identifier}")
    print(f"✓ Total notes: {len(notes_list)}")
    
    return created_notes

# Usage
notes = add_notes_workflow("chapter", "Deep Learning - Chapter 6")
```

### Best Practices

- **Use Markdown format** for text notes
- **Create separate notes** for different topics
- **Add descriptions** to help identify note purpose
- **Review notes** periodically and update outdated information

---

## Workflow 4: Query and Navigate Knowledge Graph

**Goal**: Search concepts and explore relationships in the knowledge graph.

**Duration**: 5-10 minutes per query

### Steps

1. **Search for concepts** by name or keywords
2. **Retrieve concept details** and relationships
3. **Explore knowledge graph** (depth and breadth)
4. **Analyze graph statistics**

### Tools Used

- `search_knowledge` - Full-text search
- `get_concept` - Retrieve concept details
- `get_knowledge_graph` - Explore relationships
- `get_graph_stats` - View overall statistics

### Example Code

```python
def query_knowledge_graph_workflow(search_term):
    """Search and explore the knowledge graph."""
    
    print(f"Searching knowledge graph for: {search_term}")
    
    # Step 1: Search concepts
    results = api_call("GET", f"/search?q={search_term}&limit=20")
    print(f"Found {len(results)} concepts")
    
    if not results:
        print("No results found")
        return
    
    # Step 2: Get details for top result
    top_concept = results[0]["name"]
    print(f"\nExploring concept: {top_concept}")
    
    concept_details = api_call("GET", f"/concepts/{top_concept}")
    print(f"  Kind: {concept_details.get('kind')}")
    
    # Step 3: Explore knowledge graph
    print(f"\nExploring relationships (depth=2)")
    graph = api_call("GET", f"/graph/{top_concept}?depth=2&max_nodes=50")
    
    # Step 4: Get graph statistics
    stats = api_call("GET", "/graph-stats")
    print(f"\nGraph Statistics:")
    print(f"  Total Concepts: {stats['concepts']}")
    print(f"  Total Books: {stats['books']}")
    
    return results

# Usage
results = query_knowledge_graph_workflow("gradient descent")
```

### Best Practices

- **Start with broad searches** to understand concept landscape
- **Use depth=1-2** for initial exploration
- **Check graph statistics** regularly to monitor knowledge base growth
- **Follow prerequisite chains** to understand learning paths

---

## Workflow 5: Batch Operations

**Goal**: Perform bulk operations on multiple items (create, update, delete).

**Duration**: Varies by batch size

### Steps

1. **Prepare batch data** (CSV, JSON)
2. **Validate data** before submission
3. **Execute operations** in batches
4. **Monitor and report** results

### Tools Used

- `upsert_book`, `upsert_chapter`, `upsert_concept` (multiple calls)
- Error handling and retry logic

### Example Code

```python
def batch_operations_workflow(operations_file):
    """Execute batch operations from a file."""
    
    with open(operations_file) as f:
        operations = json.load(f)
    
    print(f"Processing {len(operations)} operations")
    
    results = {
        "success": [],
        "failed": []
    }
    
    # Process batch operations
    for op in operations:
        try:
            if op["type"] == "book":
                result = api_call("POST", "/books", json=op["data"])
            elif op["type"] == "chapter":
                result = api_call("POST", "/chapters", json=op["data"])
            elif op["type"] == "concept":
                result = api_call("POST", "/concepts", json=op["data"])
            
            results["success"].append(op["data"]["title"])
            print(f"  ✓ {op['type'].upper()}: {op['data'].get('title', op['data'].get('name'))}")
        except Exception as e:
            results["failed"].append((op["data"], str(e)))
            print(f"  ✗ {op['type'].upper()}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Batch Operations Complete")
    print(f"  Success: {len(results['success'])}")
    print(f"  Failed: {len(results['failed'])}")
    
    return results

# Usage
results = batch_operations_workflow("operations.json")
```

### Batch File Format (JSON)

```json
{
  "operations": [
    {
      "type": "book",
      "data": {
        "title": "Book Title",
        "authors": ["Author 1"],
        "edition": "1st"
      }
    },
    {
      "type": "concept",
      "data": {
        "name": "Concept Name",
        "canonical_name": "concept_name",
        "kind": "method",
        "definition": "Concept definition"
      }
    }
  ]
}
```

### Best Practices

- **Validate all data** before batch submission
- **Use batch size of 50-100** to balance speed and error recovery
- **Implement retry logic** for failed operations
- **Log all results** for auditing and debugging
- **Process in dependency order** (books → chapters → concepts)

---

## Common Patterns and Tips

### Error Handling Template

```python
try:
    result = api_call("POST", "/books", json=book_data)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print(f"Validation error: {e.response.json()}")
    elif e.response.status_code == 401:
        print("Authentication failed - check API key")
    elif e.response.status_code == 404:
        print("Resource not found")
    elif e.response.status_code == 429:
        print("Rate limited - wait and retry")
```

### Pagination Pattern

```python
def fetch_all_paginated(endpoint, limit=100):
    """Fetch all results with pagination."""
    all_results = []
    offset = 0
    
    while True:
        results = api_call("GET", f"{endpoint}?limit={limit}&offset={offset}")
        if not results:
            break
        all_results.extend(results)
        if len(results) < limit:
            break
        offset += limit
    
    return all_results
```

---

## Next Steps

- Review [20-tools.md](20-tools.md) for complete API reference
- See [30-advanced.md](30-advanced.md) for optimization and troubleshooting
- Check [examples/](../examples/) for complete working code samples
