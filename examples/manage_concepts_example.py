#!/usr/bin/env python3
"""
Example: Manage concepts and build concept relationships

This example demonstrates how to:
1. Search for concepts
2. Create new concepts with proper naming
3. Link concepts (RELATED_TO, PREREQUISITE_FOR)
4. Update concept properties

Usage:
    python manage_concepts_example.py
"""

import requests
import json
import os
import sys
from typing import Dict, Any, List, Optional


class ConceptManager:
    """Manage concepts in RZCode Study Knowledge Base"""
    
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
    
    def search_concepts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for concepts"""
        result = self._request("GET", "/search", params={"q": query, "limit": limit})
        return result.get("results", [])
    
    def get_concept(self, name: str) -> Optional[Dict[str, Any]]:
        """Get concept details"""
        try:
            return self._request("GET", f"/concepts/{name}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def create_or_update_concept(self, name: str, canonical_name: str, kind: str,
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
    
    def delete_concept(self, name: str) -> Dict[str, Any]:
        """Delete a concept"""
        return self._request("DELETE", f"/concepts/{name}")
    
    def link_related_concepts(self, concept1: str, concept2: str,
                             relationship: str = "related") -> Dict[str, Any]:
        """Link two concepts as related"""
        data = {
            "concept_title_1": concept1,
            "concept_title_2": concept2,
            "relationship": relationship,
            "source": "agent"
        }
        # 注意：路由必须用下划线 related_to，连字符 /related-to 是 404
        return self._request("POST", "/relationships/related_to", json=data)
    
    def link_prerequisite(self, prerequisite: str, dependent: str) -> Dict[str, Any]:
        """Link two concepts as prerequisite"""
        data = {
            "prerequisite_concept_title": prerequisite,
            "dependent_concept_title": dependent,
            "source": "agent"
        }
        # 注意：路由必须用下划线 prerequisite_for，且三个字段都必填（缺一报 400）
        return self._request("POST", "/relationships/prerequisite_for", json=data)
    
    def get_concept_graph(self, name: str, depth: int = 2) -> Dict[str, Any]:
        """Get knowledge graph around a concept"""
        return self._request("GET", f"/graphs/{name}", params={"depth": depth})


def main():
    """Example workflow for managing concepts"""
    
    print("=" * 60)
    print("RZCode Study Skill - Manage Concepts Example")
    print("=" * 60)
    
    try:
        manager = ConceptManager()
    except FileNotFoundError:
        print("Error: ~/.rzcode/config.json not found")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    try:
        # Example 1: Search for existing concepts
        print("\n[Example 1] Searching for concepts...")
        results = manager.search_concepts("derivative", limit=5)
        print(f"Found {len(results)} results:")
        for r in results[:3]:
            print(f"  - {r.get('canonical_name')}: {r.get('definition', '')[:60]}...")
        
        # Example 2: Create new concepts
        print("\n[Example 2] Creating new concepts...")
        concepts_to_create = [
            {
                "name": "Chain Rule",
                "canonical_name": "Chain Rule",
                "kind": "theorem",
                "definition": "A method for finding the derivative of composite functions",
                "aliases": ["composite derivative rule"],
                "summary": "Used to differentiate nested functions"
            },
            {
                "name": "Product Rule",
                "canonical_name": "Product Rule",
                "kind": "theorem",
                "definition": "A formula for finding the derivative of a product of functions",
                "aliases": ["derivative of product"],
                "summary": "d(uv)/dx = u(dv/dx) + v(du/dx)"
            },
            {
                "name": "Quotient Rule",
                "canonical_name": "Quotient Rule",
                "kind": "theorem",
                "definition": "A formula for finding the derivative of a quotient of functions",
                "aliases": ["derivative of quotient"],
                "summary": "d(u/v)/dx = (v(du/dx) - u(dv/dx)) / v²"
            }
        ]
        
        created_concepts = []
        for concept in concepts_to_create:
            # First check if concept exists
            existing = manager.get_concept(concept["canonical_name"])
            if existing:
                print(f"✓ Concept '{concept['canonical_name']}' already exists")
                created_concepts.append(concept["canonical_name"])
            else:
                c = manager.create_or_update_concept(
                    name=concept["name"],
                    canonical_name=concept["canonical_name"],
                    kind=concept["kind"],
                    definition=concept["definition"],
                    aliases=concept.get("aliases"),
                    summary=concept.get("summary")
                )
                print(f"✓ Created concept: {c.get('canonical_name')}")
                created_concepts.append(concept["canonical_name"])
        
        # Example 3: Link concepts together
        print("\n[Example 3] Building concept relationships...")
        relationships = [
            ("Chain Rule", "Derivative", "extends_concept"),
            ("Product Rule", "Derivative", "extends_concept"),
            ("Quotient Rule", "Derivative", "extends_concept"),
            ("Chain Rule", "Product Rule", "complementary_technique"),
            ("Product Rule", "Quotient Rule", "related_formula")
        ]
        
        for c1, c2, rel in relationships:
            try:
                link = manager.link_related_concepts(c1, c2, rel)
                print(f"✓ Linked '{c1}' ↔ '{c2}' ({rel})")
            except Exception as e:
                print(f"✗ Failed to link {c1} and {c2}: {e}")
        
        # Example 4: Establish learning prerequisites
        print("\n[Example 4] Setting up learning prerequisites...")
        prerequisites = [
            ("Function", "Chain Rule"),
            ("Derivative", "Chain Rule"),
            ("Derivative", "Product Rule"),
            ("Derivative", "Quotient Rule")
        ]
        
        for prereq, dependent in prerequisites:
            try:
                link = manager.link_prerequisite(prereq, dependent)
                print(f"✓ {prereq} is a prerequisite for {dependent}")
            except Exception as e:
                print(f"✗ Failed to set prerequisite: {e}")
        
        # Example 5: Query concept graph
        print("\n[Example 5] Querying concept graph...")
        try:
            graph = manager.get_concept_graph("Chain Rule", depth=2)
            nodes = graph.get("nodes", [])
            edges = graph.get("edges", [])
            print(f"Graph has {len(nodes)} nodes and {len(edges)} edges")
            print("Key nodes:")
            for node in nodes[:5]:
                print(f"  - {node.get('properties', {}).get('canonical_name', 'Unknown')}")
        except Exception as e:
            print(f"Graph query failed: {e}")
        
        # Example 6: Get specific concept details
        print("\n[Example 6] Retrieving concept details...")
        if created_concepts:
            concept_name = created_concepts[0]
            concept = manager.get_concept(concept_name)
            if concept:
                print(f"Concept: {concept.get('canonical_name')}")
                print(f"  Kind: {concept.get('kind')}")
                print(f"  Definition: {concept.get('definition')}")
                print(f"  Aliases: {', '.join(concept.get('aliases', []))}")
        
        print("\n" + "=" * 60)
        print("✓ Concept management workflow completed!")
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
