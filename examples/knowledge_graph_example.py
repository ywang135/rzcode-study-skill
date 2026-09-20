#!/usr/bin/env python3
"""
Example: Query and visualize the knowledge graph

This example demonstrates how to:
1. Search the knowledge base
2. Retrieve knowledge graph subgraphs
3. Analyze concept relationships
4. Get statistics about the knowledge base
5. Export data for visualization

Usage:
    python knowledge_graph_example.py
"""

import requests
import json
import os
import sys
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict


class KnowledgeGraphAnalyzer:
    """Analyze and visualize the knowledge graph"""
    
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
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for concepts"""
        result = self._request("GET", "/search", params={"q": query, "limit": limit})
        return result.get("results", [])
    
    def get_graph(self, concept_name: str, depth: int = 2, 
                  max_nodes: int = 100) -> Dict[str, Any]:
        """Get knowledge graph subgraph for a concept"""
        params = {"depth": depth, "max_nodes": max_nodes}
        return self._request("GET", f"/graphs/{concept_name}", params=params)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return self._request("GET", "/graphs/stats")
    
    def get_concept(self, name: str) -> Dict[str, Any]:
        """Get concept details"""
        return self._request("GET", f"/concepts/{name}")
    
    def analyze_graph_structure(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze graph structure"""
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        # Build adjacency map
        adjacency = defaultdict(list)
        relationship_types = set()
        
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            rel_type = edge.get("relationship", "unknown")
            
            adjacency[source].append((target, rel_type))
            relationship_types.add(rel_type)
        
        # Calculate centrality (simplified)
        centrality = {}
        for node in nodes:
            node_id = node.get("id")
            degree = len(adjacency.get(node_id, []))
            centrality[node_id] = degree
        
        # Find most central nodes
        top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "relationship_types": list(relationship_types),
            "top_central_nodes": top_central,
            "adjacency_size": len(adjacency)
        }
    
    def export_graph_for_visualization(self, graph: Dict[str, Any], 
                                      output_file: str) -> None:
        """Export graph in Cytoscape.js compatible format"""
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        # Convert to Cytoscape format
        cy_elements = []
        
        # Add nodes
        for node in nodes:
            cy_node = {
                "data": {
                    "id": node.get("id"),
                    "label": node.get("properties", {}).get("canonical_name", node.get("id")),
                    "type": node.get("type")
                }
            }
            cy_elements.append(cy_node)
        
        # Add edges
        for edge in edges:
            cy_edge = {
                "data": {
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "relationship": edge.get("relationship", "related")
                }
            }
            cy_elements.append(cy_edge)
        
        # Write to file
        with open(output_file, "w") as f:
            json.dump({"elements": cy_elements}, f, indent=2, ensure_ascii=False)
        
        print(f"Graph exported to {output_file}")


def print_concepts_table(concepts: List[Dict[str, Any]]) -> None:
    """Print concepts in a formatted table"""
    print(f"{'Concept':<30} {'Kind':<15} {'Definition':<40}")
    print("-" * 85)
    for c in concepts[:10]:
        name = c.get("canonical_name", "Unknown")[:28]
        kind = c.get("kind", "unknown")[:13]
        definition = c.get("definition", "")[:38]
        print(f"{name:<30} {kind:<15} {definition:<40}")


def main():
    """Example workflow for knowledge graph analysis"""
    
    print("=" * 80)
    print("RZCode Study Skill - Knowledge Graph Analysis Example")
    print("=" * 80)
    
    try:
        analyzer = KnowledgeGraphAnalyzer()
    except FileNotFoundError:
        print("Error: ~/.rzcode/config.json not found")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    try:
        # Example 1: Get knowledge base statistics
        print("\n[Example 1] Knowledge Base Statistics")
        print("-" * 40)
        try:
            stats = analyzer.get_stats()
            print(f"Total Concepts:     {stats.get('total_concepts', 0):>5}")
            print(f"Total Books:        {stats.get('total_books', 0):>5}")
            print(f"Total Chapters:     {stats.get('total_chapters', 0):>5}")
            print(f"Total Notes:        {stats.get('total_notes', 0):>5}")
            print(f"Total Relationships: {stats.get('total_relationships', 0):>5}")
        except Exception as e:
            print(f"Could not retrieve statistics: {e}")
        
        # Example 2: Search for concepts
        print("\n[Example 2] Searching for Concepts")
        print("-" * 40)
        search_term = "derivative"
        results = analyzer.search(search_term, limit=10)
        print(f"Search results for '{search_term}':")
        print_concepts_table(results)
        
        # Example 3: Analyze concept graph
        print("\n[Example 3] Analyzing Concept Graph")
        print("-" * 40)
        if results:
            concept_name = results[0].get("canonical_name")
            print(f"Analyzing graph around '{concept_name}'...")
            
            try:
                graph = analyzer.get_graph(concept_name, depth=2, max_nodes=50)
                analysis = analyzer.analyze_graph_structure(graph)
                
                print(f"  Total Nodes: {analysis['total_nodes']}")
                print(f"  Total Edges: {analysis['total_edges']}")
                print(f"  Relationship Types: {', '.join(analysis['relationship_types'])}")
                
                print("\n  Most Central Concepts:")
                for node_id, degree in analysis['top_central_nodes'][:5]:
                    print(f"    - {node_id}: {degree} connections")
            except Exception as e:
                print(f"  Graph analysis failed: {e}")
        
        # Example 4: Browse related concepts
        print("\n[Example 4] Related Concepts Browser")
        print("-" * 40)
        if results:
            concept_name = results[0].get("canonical_name")
            print(f"Fetching concept details for '{concept_name}'...")
            
            try:
                concept = analyzer.get_concept(concept_name)
                print(f"  Name: {concept.get('canonical_name')}")
                print(f"  Kind: {concept.get('kind')}")
                print(f"  Definition: {concept.get('definition')[:100]}...")
                
                if concept.get("aliases"):
                    print(f"  Aliases: {', '.join(concept.get('aliases'))}")
                
                # Get graph to find related concepts
                graph = analyzer.get_graph(concept_name, depth=1, max_nodes=20)
                nodes = graph.get("nodes", [])
                
                if len(nodes) > 1:
                    print(f"\n  Related Concepts ({len(nodes)-1} found):")
                    for node in nodes[1:6]:  # Skip first node (the center concept)
                        node_name = node.get("properties", {}).get("canonical_name", "Unknown")
                        print(f"    - {node_name}")
            except Exception as e:
                print(f"  Concept details failed: {e}")
        
        # Example 5: Export graph for visualization
        print("\n[Example 5] Exporting Graph for Visualization")
        print("-" * 40)
        if results:
            concept_name = results[0].get("canonical_name")
            output_file = f"/tmp/kg_graph_{concept_name.replace(' ', '_')}.json"
            
            try:
                graph = analyzer.get_graph(concept_name, depth=2, max_nodes=100)
                analyzer.export_graph_for_visualization(graph, output_file)
                print(f"✓ Graph exported successfully")
                print(f"  Location: {output_file}")
                print(f"  Nodes: {len(graph.get('nodes', []))}")
                print(f"  Edges: {len(graph.get('edges', []))}")
            except Exception as e:
                print(f"Export failed: {e}")
        
        # Example 6: Multi-level traversal
        print("\n[Example 6] Multi-level Knowledge Traversal")
        print("-" * 40)
        print("Attempting to traverse knowledge graph at different depths...")
        
        if results:
            concept_name = results[0].get("canonical_name")
            
            for depth in [1, 2, 3]:
                try:
                    graph = analyzer.get_graph(concept_name, depth=depth, max_nodes=100)
                    nodes = len(graph.get("nodes", []))
                    edges = len(graph.get("edges", []))
                    print(f"  Depth {depth}: {nodes} nodes, {edges} edges")
                except Exception as e:
                    print(f"  Depth {depth}: Error - {e}")
        
        print("\n" + "=" * 80)
        print("✓ Knowledge graph analysis completed!")
        print("=" * 80)
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
