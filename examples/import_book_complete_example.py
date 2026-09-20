#!/usr/bin/env python3
"""
Example: Complete book import workflow using RZCode Study Skill v2.0 Cloud API

This example demonstrates the complete workflow for importing a book:
1. Create a book with metadata
2. Add chapters (supporting nested hierarchy)
3. Extract and create concepts
4. Link concepts to chapters (MENTIONED_IN relationship)
5. Create concept relationships (RELATED_TO, PREREQUISITE_FOR)
6. Add notes

Usage:
    python import_book_example.py
"""

import requests
import json
import os
import sys
from typing import Dict, Any, List


class StudyAPIClient:
    """Simple client for RZCode Study API"""
    
    def __init__(self, config_path: str = None):
        """Initialize with config file"""
        if config_path is None:
            config_path = os.path.expanduser("~/.rzcode/config.json")
        
        with open(config_path) as f:
            config = json.load(f)
        
        self.api_host = config.get("api_host", "https://rzcode.vip")
        self.api_key = config.get("api_key")
        self.base_url = f"{self.api_host}/api/study"
        self.headers = {"X-API-Key": self.api_key}
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("headers", {}).update(self.headers)
        
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.text else {}
    
    def create_book(self, title: str, authors: List[str] = None, 
                   edition: str = None) -> Dict[str, Any]:
        """Create or update a book"""
        return self._request("POST", f"/books/{title}", 
                            json={"authors": authors, "edition": edition})
    
    def create_chapter(self, book_title: str, chapter_title: str, 
                      level: int, order: int, summary: str = None,
                      parent_title: str = None) -> Dict[str, Any]:
        """Create or update a chapter"""
        data = {
            "level": level,
            "order": order,
            "summary": summary,
            "parent_title": parent_title
        }
        return self._request("POST", 
                            f"/books/{book_title}/chapters/{chapter_title}",
                            json=data)
    
    def create_concept(self, name: str, canonical_name: str, kind: str,
                      definition: str, aliases: List[str] = None,
                      summary: str = None) -> Dict[str, Any]:
        """Create or update a concept"""
        data = {
            "canonical_name": canonical_name,
            "kind": kind,
            "definition": definition,
            "aliases": aliases or [],
            "summary": summary
        }
        return self._request("POST", f"/concepts/{name}", json=data)
    
    def link_concept_to_chapter(self, concept_title: str, chapter_title: str,
                               role: str = "introduced", quote: str = None) -> Dict[str, Any]:
        """Link a concept to a chapter (MENTIONED_IN relationship)"""
        data = {
            "concept_title": concept_title,
            "chapter_title": chapter_title,
            "role": role,
            "quote": quote
        }
        return self._request("POST", "/relationships/mentioned-in", json=data)
    
    def link_concepts(self, concept1: str, concept2: str,
                     relationship: str = "related") -> Dict[str, Any]:
        """Link two concepts (RELATED_TO relationship)"""
        data = {
            "concept_title_1": concept1,
            "concept_title_2": concept2,
            "relationship": relationship
        }
        return self._request("POST", "/relationships/related-to", json=data)
    
    def create_note(self, node_type: str, node_identifier: str,
                   title: str, content: str, description: str = None) -> Dict[str, Any]:
        """Create a text note"""
        data = {
            "title": title,
            "content": content,
            "description": description
        }
        return self._request("POST", f"/notes/{node_type}/{node_identifier}",
                            json=data)


def main():
    """Complete import workflow example"""
    
    print("=" * 60)
    print("RZCode Study Skill - Complete Import Example")
    print("=" * 60)
    
    try:
        client = StudyAPIClient()
    except FileNotFoundError:
        print("Error: ~/.rzcode/config.json not found")
        print("Please create it with: api_key and api_host")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    try:
        # Step 1: Create book
        print("\n[Step 1] Creating book...")
        book_title = "Introduction to Physics"
        book = client.create_book(
            title=book_title,
            authors=["Isaac Newton", "Albert Einstein"],
            edition="2nd Edition"
        )
        print(f"✓ Book created: {book.get('title')}")
        
        # Step 2: Create chapters (with hierarchy)
        print("\n[Step 2] Creating chapters...")
        chapters = [
            {
                "title": "Part I: Classical Mechanics",
                "level": 1,
                "order": 1,
                "summary": "Introduction to classical mechanics"
            },
            {
                "title": "Chapter 1: Motion and Forces",
                "level": 2,
                "order": 1,
                "parent_title": "Part I: Classical Mechanics",
                "summary": "Description of motion and Newton's laws"
            },
            {
                "title": "Chapter 2: Energy and Momentum",
                "level": 2,
                "order": 2,
                "parent_title": "Part I: Classical Mechanics",
                "summary": "Conservation laws and energy"
            }
        ]
        
        for ch in chapters:
            chapter = client.create_chapter(
                book_title=book_title,
                chapter_title=ch["title"],
                level=ch["level"],
                order=ch["order"],
                summary=ch.get("summary"),
                parent_title=ch.get("parent_title")
            )
            print(f"✓ Chapter created: {chapter.get('title')}")
        
        # Step 3: Create concepts
        print("\n[Step 3] Creating concepts...")
        concepts = [
            {
                "name": "Velocity",
                "canonical_name": "Velocity",
                "kind": "definition",
                "definition": "The rate of change of position with respect to time",
                "aliases": ["speed", "v"]
            },
            {
                "name": "Acceleration",
                "canonical_name": "Acceleration",
                "kind": "definition",
                "definition": "The rate of change of velocity with respect to time",
                "aliases": ["a"]
            },
            {
                "name": "Force",
                "canonical_name": "Force",
                "kind": "definition",
                "definition": "A push or pull acting on an object",
                "aliases": ["F"]
            },
            {
                "name": "Energy",
                "canonical_name": "Energy",
                "kind": "definition",
                "definition": "The capacity to do work",
                "aliases": ["E"]
            }
        ]
        
        for concept in concepts:
            c = client.create_concept(
                name=concept["name"],
                canonical_name=concept["canonical_name"],
                kind=concept["kind"],
                definition=concept["definition"],
                aliases=concept.get("aliases")
            )
            print(f"✓ Concept created: {c.get('canonical_name')}")
        
        # Step 4: Link concepts to chapters
        print("\n[Step 4] Linking concepts to chapters...")
        links = [
            ("Velocity", "Chapter 1: Motion and Forces", "introduced"),
            ("Acceleration", "Chapter 1: Motion and Forces", "introduced"),
            ("Force", "Chapter 1: Motion and Forces", "core_concept"),
            ("Energy", "Chapter 2: Energy and Momentum", "introduced")
        ]
        
        for concept, chapter, role in links:
            link = client.link_concept_to_chapter(
                concept_title=concept,
                chapter_title=chapter,
                role=role
            )
            print(f"✓ Linked '{concept}' to '{chapter}' as '{role}'")
        
        # Step 5: Link concepts to each other
        print("\n[Step 5] Linking related concepts...")
        related = [
            ("Velocity", "Acceleration", "derived_from"),
            ("Force", "Acceleration", "related_via_newton_2nd_law"),
            ("Energy", "Force", "physical_property")
        ]
        
        for c1, c2, rel in related:
            link = client.link_concepts(c1, c2, rel)
            print(f"✓ Linked '{c1}' ↔ '{c2}' ({rel})")
        
        # Step 6: Create notes
        print("\n[Step 6] Adding notes...")
        note = client.create_note(
            node_type="chapter",
            node_identifier="Chapter 1: Motion and Forces",
            title="Key Formulas",
            content="v = dx/dt\na = dv/dt\nF = ma",
            description="Important equations for this chapter"
        )
        print(f"✓ Note created for chapter")
        
        print("\n" + "=" * 60)
        print("✓ Complete import workflow finished successfully!")
        print("=" * 60)
        return 0
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ API Error: {e.response.status_code}")
        print(f"  Response: {e.response.text}")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

            {
                "canonical_name": "加速度",
                "aliases": ["acceleration"],
                "kind": "definition",
                "definition": "单位时间内速度改变量的矢量。",
                "summary": "描述速度变化快慢",
                "chapter_title": "第1章 物体的运动",
                "pages": "21-25",
            },
        ]

        for c in concepts:
            existing = api.search_concepts(c["canonical_name"], limit=1)
            if not existing.get("results"):
                api.create_concept(
                    canonical_name=c["canonical_name"],
                    aliases=c["aliases"],
                    kind=c["kind"],
                    definition=c["definition"],
                    summary=c["summary"],
                )

            api.create_mentioned_in_edge(
                concept_name=c["canonical_name"],
                chapter_title=c["chapter_title"],
                book_title=book_title,
                pages=c["pages"],
                role="introduced",
            )

        stats = api.get_stats()
        print("导入完成:", stats)
        return 0
    finally:
        api.close_db()


if __name__ == "__main__":
    raise SystemExit(main())
