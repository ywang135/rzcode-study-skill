# Tools Reference - RZCode Study Skill v2.0

**Complete API Reference** - This document provides a comprehensive complete API reference for all 25 API tools organized by category. All tools use a RESTful API with JSON request/response format.

### Authentication

All API calls require the `X-API-Key` header with your API key:

```bash
curl -H "X-API-Key: sk.your.api.key" https://rzcode.vip/api/study/books
```

### Base URLs

- **Production**: `https://rzcode.vip/api/study`
- **Development**: `http://localhost:8000/api/study`

### HTTP Methods

- `GET` - Retrieve resources
- `POST` - Create or upsert resources
- `PUT` - Update resources
- `DELETE` - Delete resources

---

## Category 1: Books (5 tools)

### 1. list_books

**Purpose**: List all books for the current user.

**Endpoint**: `GET /books`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Maximum results (default: 100, max: 100) |
| offset | integer | No | Number of results to skip (default: 0) |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" "https://rzcode.vip/api/study/books?limit=20&offset=0"
```

**Response Schema**:
```json
{
  "books": [
    {
      "id": "book_1",
      "title": "Deep Learning",
      "authors": ["Ian Goodfellow"],
      "edition": "1st Edition",
      "file_path": "/uploads/deeplearning.pdf",
      "created_at": "2026-09-16T10:00:00Z",
      "updated_at": "2026-09-16T10:00:00Z"
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0
}
```

**Example Usage**:
```python
import requests

response = requests.get(
    "https://rzcode.vip/api/study/books",
    headers={"X-API-Key": "sk.xxx.yyy"},
    params={"limit": 10, "offset": 0}
)
books = response.json()["books"]
for book in books:
    print(f"- {book['title']} by {', '.join(book['authors'])}")
```

**Error Cases**:
- `401 Unauthorized` - Invalid or missing API key
- `429 Too Many Requests` - Rate limit exceeded

---

### 2. upsert_book

**Purpose**: Create or update a book. Uses upsert semantics (create if not exists, update if exists).

**Endpoint**: `POST /books`

**Method**: POST

**Request Schema**:
```json
{
  "title": "string (required, unique)",
  "authors": "array[string] (optional)",
  "edition": "string (optional)",
  "file_path": "string (optional)"
}
```

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/books" \
  -H "X-API-Key: sk.xxx.yyy" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deep Learning",
    "authors": ["Ian Goodfellow", "Yoshua Bengio"],
    "edition": "1st Edition"
  }'
```

**Response Schema**:
```json
{
  "id": "book_1",
  "title": "Deep Learning",
  "authors": ["Ian Goodfellow", "Yoshua Bengio"],
  "edition": "1st Edition",
  "file_path": null,
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
book_data = {
    "title": "Machine Learning Basics",
    "authors": ["Andrew Ng"],
    "edition": "2nd Edition"
}

response = requests.post(
    "https://rzcode.vip/api/study/books",
    headers={"X-API-Key": "sk.xxx.yyy"},
    json=book_data
)
result = response.json()
print(f"Book {result['id']} created/updated")
```

**Error Cases**:
- `400 Bad Request` - Invalid field values or missing required fields
- `409 Conflict` - Title already exists with conflicting data

---

### 3. get_book

**Purpose**: Retrieve book details including metadata and chapter list.

**Endpoint**: `GET /books/{title}`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Book title (URL-encoded) |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" "https://rzcode.vip/api/study/books/Deep%20Learning"
```

**Response Schema**:
```json
{
  "id": "book_1",
  "title": "Deep Learning",
  "authors": ["Ian Goodfellow"],
  "edition": "1st Edition",
  "file_path": "/uploads/deeplearning.pdf",
  "chapters": [
    {
      "id": "ch_1",
      "title": "Introduction",
      "level": 1,
      "order": 1,
      "summary": "Basic concepts of deep learning"
    }
  ],
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/books/Deep%20Learning",
    headers={"X-API-Key": "sk.xxx.yyy"}
)
book = response.json()
print(f"Book: {book['title']}")
print(f"Chapters: {len(book['chapters'])}")
for chapter in book['chapters']:
    print(f"  - {chapter['title']}")
```

**Error Cases**:
- `404 Not Found` - Book with specified title does not exist

---

### 4. upload_book

**Purpose**: Upload a book file (PDF, TXT, MD) for an existing book.

**Endpoint**: `POST /books/{title}/upload`

**Method**: POST (multipart/form-data)

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | file | Yes | Book file (PDF, TXT, MD) |

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/books/Deep%20Learning/upload" \
  -H "X-API-Key: sk.xxx.yyy" \
  -F "file=@deeplearning.pdf"
```

**Response Schema**:
```json
{
  "id": "book_1",
  "title": "Deep Learning",
  "file_path": "/uploads/deeplearning.pdf",
  "file_size": 5242880,
  "uploaded_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
with open("deeplearning.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "https://rzcode.vip/api/study/books/Deep%20Learning/upload",
        headers={"X-API-Key": "sk.xxx.yyy"},
        files=files
    )
result = response.json()
print(f"File uploaded: {result['file_path']}")
```

**Error Cases**:
- `400 Bad Request` - No file provided or invalid file format
- `404 Not Found` - Book does not exist
- `413 Payload Too Large` - File exceeds 100MB limit
- `415 Unsupported Media Type` - File format not supported

---

### 5. delete_book

**Purpose**: Delete a book and all related resources (chapters, notes, relationships).

**Endpoint**: `DELETE /books/{title}`

**Method**: DELETE

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Book title |

**Request Example**:
```bash
curl -X DELETE "https://rzcode.vip/api/study/books/Deep%20Learning" \
  -H "X-API-Key: sk.xxx.yyy"
```

**Response Schema**:
```json
{
  "id": "book_1",
  "title": "Deep Learning",
  "deleted_at": "2026-09-16T10:00:00Z",
  "resources_deleted": {
    "chapters": 5,
    "concepts": 0,
    "notes": 2,
    "relationships": 8
  }
}
```

**Example Usage**:
```python
response = requests.delete(
    "https://rzcode.vip/api/study/books/Deep%20Learning",
    headers={"X-API-Key": "sk.xxx.yyy"}
)
result = response.json()
print(f"Book deleted. Chapters: {result['resources_deleted']['chapters']}")
```

**Error Cases**:
- `404 Not Found` - Book does not exist
- `409 Conflict` - Book has references preventing deletion

---

## Category 2: Chapters (5 tools)

### 6. list_chapters

**Purpose**: List all chapters for a specific book.

**Endpoint**: `GET /books/{title}/chapters`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| title | string | Yes | Book title |
| limit | integer | No | Max results (default: 100) |
| offset | integer | No | Results to skip (default: 0) |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" "https://rzcode.vip/api/study/books/Deep%20Learning/chapters"
```

**Response Schema**:
```json
{
  "chapters": [
    {
      "id": "ch_1",
      "title": "Introduction",
      "level": 1,
      "order": 1,
      "summary": "Basic concepts",
      "parent_title": null
    },
    {
      "id": "ch_2",
      "title": "Linear Algebra",
      "level": 2,
      "order": 1,
      "summary": "Vectors and matrices",
      "parent_title": "Part I: Foundations"
    }
  ],
  "total": 12,
  "limit": 100,
  "offset": 0
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/books/Deep%20Learning/chapters",
    headers={"X-API-Key": "sk.xxx.yyy"}
)
chapters = response.json()["chapters"]
for chapter in chapters:
    indent = "  " * (chapter['level'] - 1)
    print(f"{indent}- {chapter['title']}")
```

**Error Cases**:
- `404 Not Found` - Book does not exist

---

### 7. get_chapter

**Purpose**: Get details for a specific chapter, including its concepts.

**Endpoint**: `GET /books/{book_title}/chapters/{chapter_title}`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| book_title | string | Yes | Book title |
| chapter_title | string | Yes | Chapter title |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" \
  "https://rzcode.vip/api/study/books/Deep%20Learning/chapters/Introduction"
```

**Response Schema**:
```json
{
  "id": "ch_1",
  "title": "Introduction",
  "level": 1,
  "order": 1,
  "summary": "Basic concepts of deep learning",
  "parent_title": null,
  "book_title": "Deep Learning",
  "concepts": [
    {
      "name": "Neural Network",
      "role": "introduced"
    }
  ],
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/books/Deep%20Learning/chapters/Introduction",
    headers={"X-API-Key": "sk.xxx.yyy"}
)
chapter = response.json()
print(f"Chapter: {chapter['title']}")
print(f"Concepts: {len(chapter['concepts'])}")
```

**Error Cases**:
- `404 Not Found` - Book or chapter does not exist

---

### 8. upsert_chapter

**Purpose**: Create or update a chapter in a book with support for nested hierarchy.

**Endpoint**: `POST /chapters`

**Method**: POST

**Request Schema**:
```json
{
  "book_title": "string (required)",
  "title": "string (required)",
  "level": "integer (required)",
  "order": "integer (required)",
  "summary": "string (optional)",
  "parent_title": "string (optional)"
}
```

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/chapters" \
  -H "X-API-Key: sk.xxx.yyy" \
  -H "Content-Type: application/json" \
  -d '{
    "book_title": "Deep Learning",
    "title": "Linear Algebra",
    "level": 2,
    "order": 1,
    "parent_title": "Part I: Foundations",
    "summary": "Vectors, matrices, and eigenvalues"
  }'
```

**Response Schema**:
```json
{
  "id": "ch_2",
  "title": "Linear Algebra",
  "level": 2,
  "order": 1,
  "parent_title": "Part I: Foundations",
  "book_title": "Deep Learning",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
chapters = [
    {
        "book_title": "Deep Learning",
        "title": "Part I: Foundations",
        "level": 1,
        "order": 1
    },
    {
        "book_title": "Deep Learning",
        "title": "Linear Algebra",
        "level": 2,
        "order": 1,
        "parent_title": "Part I: Foundations"
    }
]

for chapter in chapters:
    response = requests.post(
        "https://rzcode.vip/api/study/chapters",
        headers={"X-API-Key": "sk.xxx.yyy"},
        json=chapter
    )
    print(f"Created: {response.json()['title']}")
```

**Error Cases**:
- `400 Bad Request` - Invalid hierarchy (parent not found, invalid level)
- `404 Not Found` - Book does not exist
- `409 Conflict` - Chapter already exists with conflicting data

---

### 9. delete_chapter

**Purpose**: Delete a chapter and all related resources.

**Endpoint**: `DELETE /books/{book_title}/chapters/{chapter_title}`

**Method**: DELETE

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| book_title | string | Yes | Book title |
| chapter_title | string | Yes | Chapter title |

**Request Example**:
```bash
curl -X DELETE "https://rzcode.vip/api/study/books/Deep%20Learning/chapters/Introduction" \
  -H "X-API-Key: sk.xxx.yyy"
```

**Response Schema**:
```json
{
  "id": "ch_1",
  "title": "Introduction",
  "deleted_at": "2026-09-16T10:00:00Z",
  "resources_deleted": {
    "notes": 2,
    "relationships": 5
  }
}
```

**Error Cases**:
- `404 Not Found` - Book or chapter does not exist

---

## Category 3: Concepts (4 tools)

### 10. get_concept

**Purpose**: Retrieve concept details by name.

**Endpoint**: `GET /concepts/{name}`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Concept name |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" "https://rzcode.vip/api/study/concepts/Gradient%20Descent"
```

**Response Schema**:
```json
{
  "name": "Gradient Descent",
  "canonical_name": "gradient_descent",
  "kind": "method",
  "definition": "An optimization algorithm that iteratively moves in the direction of steepest descent",
  "aliases": ["GD", "Steepest Descent"],
  "summary": "Core optimization technique in machine learning",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/concepts/Gradient%20Descent",
    headers={"X-API-Key": "sk.xxx.yyy"}
)
concept = response.json()
print(f"Concept: {concept['name']}")
print(f"Kind: {concept['kind']}")
print(f"Definition: {concept['definition']}")
```

**Error Cases**:
- `404 Not Found` - Concept does not exist

---

### 11. upsert_concept

**Purpose**: Create or update a concept definition.

**Endpoint**: `POST /concepts`

**Method**: POST

**Request Schema**:
```json
{
  "name": "string (required)",
  "canonical_name": "string (required, unique)",
  "kind": "enum (required): concept|theorem|definition|method|person|term",
  "definition": "string (required)",
  "aliases": "array[string] (optional)",
  "summary": "string (optional)"
}
```

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/concepts" \
  -H "X-API-Key: sk.xxx.yyy" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Backpropagation",
    "canonical_name": "backpropagation",
    "kind": "method",
    "definition": "Algorithm for computing gradients in neural networks using chain rule",
    "aliases": ["BP", "Reverse-mode AD"],
    "summary": "Efficient gradient computation in deep learning"
  }'
```

**Response Schema**:
```json
{
  "name": "Backpropagation",
  "canonical_name": "backpropagation",
  "kind": "method",
  "definition": "Algorithm for computing gradients in neural networks using chain rule",
  "aliases": ["BP", "Reverse-mode AD"],
  "summary": "Efficient gradient computation in deep learning",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
concept_data = {
    "name": "Neural Network",
    "canonical_name": "neural_network",
    "kind": "concept",
    "definition": "Interconnected artificial neurons that process information"
}

response = requests.post(
    "https://rzcode.vip/api/study/concepts",
    headers={"X-API-Key": "sk.xxx.yyy"},
    json=concept_data
)
print(f"Concept created: {response.json()['canonical_name']}")
```

**Error Cases**:
- `400 Bad Request` - Invalid kind or missing required fields
- `409 Conflict` - Canonical name already exists

---

### 12. delete_concept

**Purpose**: Delete a concept and all related resources.

**Endpoint**: `DELETE /concepts/{name}`

**Method**: DELETE

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Concept name |

**Request Example**:
```bash
curl -X DELETE "https://rzcode.vip/api/study/concepts/Gradient%20Descent" \
  -H "X-API-Key: sk.xxx.yyy"
```

**Response Schema**:
```json
{
  "name": "Gradient Descent",
  "deleted_at": "2026-09-16T10:00:00Z",
  "resources_deleted": {
    "notes": 3,
    "relationships": 8
  }
}
```

**Error Cases**:
- `404 Not Found` - Concept does not exist

---

### 13. get_book_file

**Purpose**: Get book file content in JSON or raw format.

**Endpoint**: `GET /books/{encoded_file_path}`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| encoded_file_path | string | Yes | URL-encoded file path |
| format | string | No | Response format: json or raw (default: raw) |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" \
  "https://rzcode.vip/api/study/books/uploads%2Fdeeplearning.pdf?format=json"
```

**Response Schema** (format=json):
```json
{
  "filename": "deeplearning.pdf",
  "size": 5242880,
  "type": "application/pdf",
  "content": "base64_encoded_content_or_text_content"
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/books/uploads%2Fdeeplearning.pdf",
    headers={"X-API-Key": "sk.xxx.yyy"},
    params={"format": "raw"}
)
with open("local_copy.pdf", "wb") as f:
    f.write(response.content)
```

**Error Cases**:
- `404 Not Found` - File does not exist
- `400 Bad Request` - Invalid format parameter

---

## Category 4: Concepts and Relationships (6 tools)

### 14. search_knowledge

**Purpose**: Full-text search for concepts in the knowledge graph.

**Endpoint**: `GET /search`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query |
| limit | integer | No | Max results (default: 20, max: 100) |
| offset | integer | No | Results to skip (default: 0) |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" \
  "https://rzcode.vip/api/study/search?q=gradient&limit=10"
```

**Response Schema**:
```json
{
  "results": [
    {
      "name": "Gradient Descent",
      "kind": "method",
      "score": 0.95
    },
    {
      "name": "Gradient",
      "kind": "concept",
      "score": 0.88
    }
  ],
  "total": 2,
  "query": "gradient"
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/search",
    headers={"X-API-Key": "sk.xxx.yyy"},
    params={"q": "neural", "limit": 5}
)
results = response.json()["results"]
for result in results:
    print(f"- {result['name']} ({result['kind']})")
```

**Error Cases**:
- `400 Bad Request` - Query string is empty or too long

---

### 15. get_knowledge_graph

**Purpose**: Get knowledge graph subgraph for a concept showing relationships.

**Endpoint**: `GET /graph/{name}`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Concept name |
| depth | integer | No | Graph depth (1-5, default: 1) |
| max_nodes | integer | No | Max nodes (1-500, default: 100) |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" \
  "https://rzcode.vip/api/study/graph/Gradient%20Descent?depth=2&max_nodes=50"
```

**Response Schema**:
```json
{
  "nodes": [
    {
      "id": "node_1",
      "name": "Gradient Descent",
      "kind": "method"
    },
    {
      "id": "node_2",
      "name": "Backpropagation",
      "kind": "method"
    }
  ],
  "relationships": [
    {
      "source": "node_1",
      "target": "node_2",
      "type": "related_to"
    }
  ],
  "depth": 2
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/graph/Neural%20Network",
    headers={"X-API-Key": "sk.xxx.yyy"},
    params={"depth": 2, "max_nodes": 100}
)
graph = response.json()
print(f"Nodes: {len(graph['nodes'])}")
print(f"Relationships: {len(graph['relationships'])}")
```

**Error Cases**:
- `404 Not Found` - Concept does not exist
- `400 Bad Request` - Invalid depth or max_nodes

---

### 16. get_graph_stats

**Purpose**: Get overall knowledge graph statistics.

**Endpoint**: `GET /graph-stats`

**Method**: GET

**Request Parameters**: None

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" "https://rzcode.vip/api/study/graph-stats"
```

**Response Schema**:
```json
{
  "concepts": 245,
  "books": 8,
  "chapters": 67,
  "notes": 89,
  "relationships": {
    "mentioned_in": 156,
    "related_to": 203,
    "prerequisite_for": 87,
    "part_of": 67
  },
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/graph-stats",
    headers={"X-API-Key": "sk.xxx.yyy"}
)
stats = response.json()
print(f"Knowledge Graph Statistics:")
print(f"  Concepts: {stats['concepts']}")
print(f"  Books: {stats['books']}")
print(f"  Chapters: {stats['chapters']}")
print(f"  Notes: {stats['notes']}")
```

---

### 17. upsert_related_to

**Purpose**: Create or update concept-to-concept relationships.

**Endpoint**: `POST /relationships/related_to`

**Method**: POST

**Request Schema**:
```json
{
  "concept_title_1": "string (required)",
  "concept_title_2": "string (required)",
  "relationship": "string (optional)",
  "source": "enum (optional): agent|user (default: user)"
}
```

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/relationships/related_to" \
  -H "X-API-Key: sk.xxx.yyy" \
  -H "Content-Type: application/json" \
  -d '{
    "concept_title_1": "Gradient Descent",
    "concept_title_2": "Backpropagation",
    "relationship": "used_by"
  }'
```

**Response Schema**:
```json
{
  "concept_title_1": "Gradient Descent",
  "concept_title_2": "Backpropagation",
  "relationship": "used_by",
  "created_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
relationships = [
    {
        "concept_title_1": "Gradient Descent",
        "concept_title_2": "Backpropagation",
        "relationship": "used_by"
    },
    {
        "concept_title_1": "Linear Algebra",
        "concept_title_2": "Neural Networks",
        "relationship": "foundation_for"
    }
]

for rel in relationships:
    response = requests.post(
        "https://rzcode.vip/api/study/relationships/related_to",
        headers={"X-API-Key": "sk.xxx.yyy"},
        json=rel
    )
    print(f"Relationship created: {rel['concept_title_1']} -> {rel['concept_title_2']}")
```

**Error Cases**:
- `404 Not Found` - One or both concepts do not exist
- `409 Conflict` - Relationship already exists

---

### 18. upsert_prerequisite_for

**Purpose**: Create or update concept prerequisite relationships for learning paths.

**Endpoint**: `POST /relationships/prerequisites`

**Method**: POST

**Request Schema**:
```json
{
  "prerequisite_concept_title": "string (required)",
  "dependent_concept_title": "string (required)",
  "source": "enum (optional): agent|user (default: user)"
}
```

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/relationships/prerequisites" \
  -H "X-API-Key: sk.xxx.yyy" \
  -H "Content-Type: application/json" \
  -d '{
    "prerequisite_concept_title": "Calculus",
    "dependent_concept_title": "Gradient Descent"
  }'
```

**Response Schema**:
```json
{
  "prerequisite_concept_title": "Calculus",
  "dependent_concept_title": "Gradient Descent",
  "created_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
# Define learning path
prerequisites = [
    ("Linear Algebra", "Neural Networks"),
    ("Calculus", "Gradient Descent"),
    ("Probability", "Bayesian Methods")
]

for prereq, dependent in prerequisites:
    response = requests.post(
        "https://rzcode.vip/api/study/relationships/prerequisites",
        headers={"X-API-Key": "sk.xxx.yyy"},
        json={
            "prerequisite_concept_title": prereq,
            "dependent_concept_title": dependent
        }
    )
```

**Error Cases**:
- `404 Not Found` - One or both concepts do not exist
- `409 Conflict` - Relationship already exists

---

### 19. upsert_mentioned_in

**Purpose**: Create or update concept-to-chapter relationships.

**Endpoint**: `POST /relationships/mentioned_in`

**Method**: POST

**Request Schema**:
```json
{
  "concept_title": "string (required)",
  "chapter_title": "string (required)",
  "role": "string (optional): introduced|explained|applied|referenced",
  "quote": "string (optional)",
  "source": "enum (optional): agent|user (default: user)"
}
```

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/relationships/mentioned_in" \
  -H "X-API-Key: sk.xxx.yyy" \
  -H "Content-Type: application/json" \
  -d '{
    "concept_title": "Gradient Descent",
    "chapter_title": "Optimization Algorithms",
    "role": "introduced",
    "quote": "Gradient descent is the foundation of modern optimization..."
  }'
```

**Response Schema**:
```json
{
  "concept_title": "Gradient Descent",
  "chapter_title": "Optimization Algorithms",
  "role": "introduced",
  "quote": "Gradient descent is the foundation...",
  "created_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
concepts_in_chapter = [
    ("Gradient Descent", "introduced"),
    ("Learning Rate", "explained"),
    ("Momentum", "applied")
]

for concept, role in concepts_in_chapter:
    response = requests.post(
        "https://rzcode.vip/api/study/relationships/mentioned_in",
        headers={"X-API-Key": "sk.xxx.yyy"},
        json={
            "concept_title": concept,
            "chapter_title": "Optimization Algorithms",
            "role": role
        }
    )
```

**Error Cases**:
- `404 Not Found` - Concept or chapter does not exist
- `409 Conflict` - Relationship already exists

---

### 20. upsert_part_of

**Purpose**: Create or update chapter hierarchy relationships (part_of).

**Endpoint**: `POST /relationships/part_of`

**Method**: POST

**Request Schema**:
```json
{
  "parent_title": "string (required)",
  "parent_type": "enum (required): book|chapter",
  "child_title": "string (required)",
  "level": "integer (required)",
  "order": "integer (required)",
  "source": "enum (optional): agent|user (default: user)"
}
```

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/relationships/part_of" \
  -H "X-API-Key: sk.xxx.yyy" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_title": "Deep Learning",
    "parent_type": "book",
    "child_title": "Part I: Foundations",
    "level": 1,
    "order": 1
  }'
```

**Response Schema**:
```json
{
  "parent_title": "Deep Learning",
  "parent_type": "book",
  "child_title": "Part I: Foundations",
  "level": 1,
  "order": 1,
  "created_at": "2026-09-16T10:00:00Z"
}
```

**Error Cases**:
- `404 Not Found` - Parent or child does not exist
- `400 Bad Request` - Invalid hierarchy (parent_type mismatch, invalid level)

---

## Category 5: Notes (5 tools)

### 21. create_note

**Purpose**: Create or update a text note for a node (book, chapter, or concept).

**Endpoint**: `POST /notes/{node_type}/{node_identifier}`

**Method**: POST

**Request Schema**:
```json
{
  "node_type": "enum (required): book|chapter|concept",
  "node_identifier": "string (required)",
  "title": "string (required)",
  "content": "string (required)",
  "description": "string (optional)",
  "file_type": "string (optional): md|json|txt (default: md)",
  "note_id": "string (optional, for updates)"
}
```

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/notes/concept/Gradient%20Descent" \
  -H "X-API-Key: sk.xxx.yyy" \
  -H "Content-Type: application/json" \
  -d '{
    "node_type": "concept",
    "node_identifier": "Gradient Descent",
    "title": "Learning Notes",
    "content": "# Gradient Descent\n\n## Definition\n...",
    "file_type": "md",
    "description": "Personal learning notes"
  }'
```

**Response Schema**:
```json
{
  "id": "note_1",
  "node_type": "concept",
  "node_identifier": "Gradient Descent",
  "title": "Learning Notes",
  "file_type": "md",
  "description": "Personal learning notes",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
note = {
    "node_type": "chapter",
    "node_identifier": "Deep Learning - Chapter 6",
    "title": "Key Takeaways",
    "content": """# Key Takeaways

- Point 1
- Point 2
- Point 3
""",
    "file_type": "md"
}

response = requests.post(
    "https://rzcode.vip/api/study/notes/chapter/Deep%20Learning%20-%20Chapter%206",
    headers={"X-API-Key": "sk.xxx.yyy"},
    json=note
)
print(f"Note created: {response.json()['id']}")
```

**Error Cases**:
- `404 Not Found` - Node does not exist
- `400 Bad Request` - Invalid file_type

---

### 22. upload_note

**Purpose**: Upload a file-based note for a node.

**Endpoint**: `POST /notes/{node_type}/{node_identifier}/upload`

**Method**: POST (multipart/form-data)

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| node_type | enum | Yes | book, chapter, or concept |
| node_identifier | string | Yes | Node identifier |
| file | file | Yes | File to upload (MD, PDF, TXT, etc.) |
| title | string | No | Note title |
| description | string | No | Note description |

**Request Example**:
```bash
curl -X POST "https://rzcode.vip/api/study/notes/chapter/Introduction/upload" \
  -H "X-API-Key: sk.xxx.yyy" \
  -F "file=@notes.md" \
  -F "title=Chapter Notes" \
  -F "description=Comprehensive notes"
```

**Response Schema**:
```json
{
  "id": "note_2",
  "node_type": "chapter",
  "node_identifier": "Introduction",
  "title": "Chapter Notes",
  "file_type": "md",
  "file_size": 2048,
  "created_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
with open("my_notes.md", "rb") as f:
    files = {"file": f}
    data = {
        "title": "Study Notes",
        "description": "My personal study notes"
    }
    response = requests.post(
        "https://rzcode.vip/api/study/notes/chapter/Introduction/upload",
        headers={"X-API-Key": "sk.xxx.yyy"},
        files=files,
        data=data
    )
```

**Error Cases**:
- `404 Not Found` - Node does not exist
- `413 Payload Too Large` - File exceeds 50MB limit
- `415 Unsupported Media Type` - File format not supported

---

### 23. get_note

**Purpose**: Get the content of a specific note.

**Endpoint**: `GET /notes/{node_type}/{node_identifier}/{note_id}`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| node_type | enum | Yes | book, chapter, or concept |
| node_identifier | string | Yes | Node identifier |
| note_id | string | Yes | Note ID |
| format | enum | No | json or raw (default: json) |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" \
  "https://rzcode.vip/api/study/notes/concept/Gradient%20Descent/note_1?format=raw"
```

**Response Schema** (format=json):
```json
{
  "id": "note_1",
  "node_type": "concept",
  "node_identifier": "Gradient Descent",
  "title": "Learning Notes",
  "content": "# Gradient Descent\n\n## Definition\n...",
  "file_type": "md",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/notes/concept/Gradient%20Descent/note_1",
    headers={"X-API-Key": "sk.xxx.yyy"},
    params={"format": "json"}
)
note = response.json()
print(f"Note: {note['title']}")
print(note['content'])
```

**Error Cases**:
- `404 Not Found` - Node or note does not exist

---

### 24. list_notes

**Purpose**: List all notes for a node with pagination.

**Endpoint**: `GET /notes/{node_type}/{node_identifier}`

**Method**: GET

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| node_type | enum | Yes | book, chapter, or concept |
| node_identifier | string | Yes | Node identifier |
| limit | integer | No | Max results (default: 100, max: 100) |
| offset | integer | No | Results to skip (default: 0) |

**Request Example**:
```bash
curl -H "X-API-Key: sk.xxx.yyy" \
  "https://rzcode.vip/api/study/notes/chapter/Introduction?limit=10&offset=0"
```

**Response Schema**:
```json
{
  "node_type": "chapter",
  "node_identifier": "Introduction",
  "total": 3,
  "notes": [
    {
      "id": "note_1",
      "title": "Key Takeaways",
      "description": "Summary of main concepts",
      "file_type": "md",
      "created_at": "2026-09-16T10:00:00Z",
      "updated_at": "2026-09-16T10:00:00Z"
    }
  ],
  "limit": 10,
  "offset": 0
}
```

**Example Usage**:
```python
response = requests.get(
    "https://rzcode.vip/api/study/notes/concept/Neural%20Network",
    headers={"X-API-Key": "sk.xxx.yyy"},
    params={"limit": 20}
)
notes_data = response.json()
print(f"Total notes: {notes_data['total']}")
for note in notes_data['notes']:
    print(f"  - {note['title']}")
```

**Error Cases**:
- `404 Not Found` - Node does not exist

---

### 25. delete_note

**Purpose**: Delete a note from a node.

**Endpoint**: `DELETE /notes/{node_type}/{node_identifier}/{note_id}`

**Method**: DELETE

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| node_type | enum | Yes | book, chapter, or concept |
| node_identifier | string | Yes | Node identifier |
| note_id | string | Yes | Note ID |

**Request Example**:
```bash
curl -X DELETE "https://rzcode.vip/api/study/notes/concept/Gradient%20Descent/note_1" \
  -H "X-API-Key: sk.xxx.yyy"
```

**Response Schema**:
```json
{
  "id": "note_1",
  "deleted_at": "2026-09-16T10:00:00Z"
}
```

**Example Usage**:
```python
response = requests.delete(
    "https://rzcode.vip/api/study/notes/concept/Gradient%20Descent/note_1",
    headers={"X-API-Key": "sk.xxx.yyy"}
)
print(f"Note deleted")
```

**Error Cases**:
- `404 Not Found` - Node or note does not exist

---

## Pagination and Rate Limiting

### Pagination

Most list endpoints support pagination:

```python
def fetch_all_results(endpoint, initial_params=None):
    """Fetch all paginated results."""
    params = initial_params or {}
    all_results = []
    limit = 100
    offset = 0
    
    while True:
        params['limit'] = limit
        params['offset'] = offset
        response = requests.get(
            endpoint,
            headers={"X-API-Key": api_key},
            params=params
        )
        data = response.json()
        results = data.get('books') or data.get('chapters') or data.get('notes') or data.get('results')
        
        if not results:
            break
        
        all_results.extend(results)
        if len(results) < limit:
            break
        
        offset += limit
    
    return all_results
```

### Rate Limiting

API rate limits are enforced per API key:

- **Default limit**: 1,000 requests per hour
- **Rate limit header**: `X-RateLimit-Remaining` in response
- **Reset time**: `X-RateLimit-Reset` in response headers
- **Status code**: `429 Too Many Requests` when exceeded

```python
if response.status_code == 429:
    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
    wait_seconds = reset_time - time.time()
    print(f"Rate limited. Retry after {wait_seconds:.0f} seconds")
    time.sleep(max(wait_seconds, 0))
```

---

## Error Responses

All error responses follow a standard format:

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {}
}
```

### Common Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| BAD_REQUEST | 400 | Invalid parameters or malformed request |
| UNAUTHORIZED | 401 | Invalid/missing API key |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists or data conflict |
| RATE_LIMITED | 429 | Too many requests (rate limited) |
| SERVER_ERROR | 500 | Internal server error |

### Error Handling Pattern

```python
import requests
from requests.exceptions import HTTPError

def api_call_safe(method, endpoint, **kwargs):
    """Make API call with comprehensive error handling."""
    try:
        response = requests.request(
            method,
            f"https://rzcode.vip/api/study{endpoint}",
            headers={"X-API-Key": api_key},
            **kwargs
        )
        response.raise_for_status()
        return response.json() if response.text else None
    
    except HTTPError as e:
        error_data = e.response.json()
        error_code = error_data.get('error', 'UNKNOWN')
        message = error_data.get('message', str(e))
        
        if e.response.status_code == 400:
            print(f"Validation error: {message}")
        elif e.response.status_code == 401:
            print("Authentication failed - check API key")
        elif e.response.status_code == 404:
            print("Resource not found")
        elif e.response.status_code == 409:
            print(f"Data conflict: {message}")
        elif e.response.status_code == 429:
            print("Rate limited - please retry later")
        else:
            print(f"API error: {message}")
        
        raise
```

---

## Next Steps

- See [10-workflow.md](10-workflow.md) for common workflow patterns
- See [30-advanced.md](30-advanced.md) for optimization and migration guides
