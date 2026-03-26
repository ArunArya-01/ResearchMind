import networkx as nx
from typing import List, Dict

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def ingest_scholar_results(self, results: List[Dict]):
        """
        Maps Semantic Scholar JSON results into nodes and edges.
        """
        for paper in results:
            paper_id = paper.get('paperId', 'unknown')
            title = paper.get('title', 'Unknown Title')
            self.graph.add_node(paper_id, type='paper', title=title)
            
            authors = paper.get('authors', [])
            for author in authors:
                author_id = author.get('authorId')
                if author_id:
                    self.graph.add_node(author_id, type='author', name=author.get('name'))
                    self.graph.add_edge(paper_id, author_id, relation='authored_by')
                    
            references = paper.get('references', [])
            for ref in references:
                ref_id = ref.get('paperId')
                if ref_id:
                    self.graph.add_edge(paper_id, ref_id, relation='cites')

    def find_discovery_gap(self):
        """
        Identifies unconnected clusters, labeling them as the 'Red Anomaly'.
        Returns data describing the discovery gap.
        """
        components = list(nx.connected_components(self.graph))
        
        red_anomalies = []
        if len(components) > 1:
            components.sort(key=len, reverse=True)
            for idx, comp in enumerate(components[1:]):
                anomaly_nodes = []
                for node in comp:
                    node_data = self.graph.nodes[node]
                    anomaly_nodes.append({"id": node, "data": node_data})
                red_anomalies.append({
                    "anomaly_id": f"red_anomaly_{idx+1}",
                    "nodes": anomaly_nodes
                })
        
        return {
            "status": "success",
            "message": "Graph analyzed for Discovery Gaps.",
            "red_anomalies": red_anomalies
        }
