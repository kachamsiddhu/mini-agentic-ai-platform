import networkx as nx
import json
import os
import glob

class DependencyGraph:
    def __init__(self, metadata_dir: str = "data/service_metadata"):
        self.graph = nx.DiGraph()
        self.metadata_dir = metadata_dir
        self.load_graph()

    def load_graph(self):
        if not os.path.exists(self.metadata_dir):
            return
        for file_path in glob.glob(f"{self.metadata_dir}/*.json"):
            with open(file_path, "r") as f:
                data = json.load(f)
                service_name = data.get("service_name")
                if service_name:
                    self.graph.add_node(service_name, **data)
                    for dep in data.get("dependencies", []):
                        self.graph.add_edge(service_name, dep)

    def get_blast_radius(self, service_name: str, max_depth: int = 2):
        if service_name not in self.graph:
            return []
        rev_graph = self.graph.reverse()
        if service_name not in rev_graph:
            return []
        affected = list(nx.single_source_shortest_path_length(rev_graph, service_name, cutoff=max_depth).keys())
        if service_name in affected:
            affected.remove(service_name)
        return affected

    def check_cross_env_action(self, service_name: str, target_env: str):
        if service_name not in self.graph:
            return False
        service_env = self.graph.nodes[service_name].get("environment")
        return service_env == target_env
