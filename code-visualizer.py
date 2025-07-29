"""
This module provides functionality to analyze and visualize dependencies between Python files in a codebase. It creates both static and interactive visualizations of the code structure,
showing hierarchical relationships, imports, and usage patterns between modules.
"""

import os
import ast
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict, Set
import matplotlib.lines as mlines


class PythonFileDependencyAnalyzer:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.import_graph = nx.DiGraph()
        self.module_map = {}  # Maps file path to module name
        self.hierarchy_edges = []
        self.flow_edges = []
        self.uses_edges = []

    def get_python_files(self) -> List[Path]:
        exclude_dirs = {
            'tests', 'test', '__pycache__', '.git', 'venv', 'env',
            'node_modules', 'build', 'dist', '.pytest_cache', 'docs',
            'examples', 'example', 'demo', 'benchmark'
        }
        python_files = []
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = Path(root) / file
                    if file_path.stat().st_size < 500_000:
                        python_files.append(file_path)
        return python_files

    def path_to_module(self, file_path: Path) -> str:
        relative_path = file_path.relative_to(self.repo_root)
        parts = list(relative_path.parts)
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
        return ".".join(parts)

    def build_import_graph(self):
        python_files = self.get_python_files()
        file_to_module = {str(f): self.path_to_module(f) for f in python_files}
        module_to_file = {v: k for k, v in file_to_module.items()}
        self.module_map = file_to_module

        # Use sets to deduplicate edges
        self.hierarchy_edges = set()
        self.flow_edges = set()
        self.uses_edges = set()

        for file_path in python_files:
            src_module = file_to_module[str(file_path)]

            # Build hierarchy (app → app.routes → app.routes.router)
            parts = src_module.split('.')
            for i in range(1, len(parts)):
                parent = '.'.join(parts[:i])
                child = '.'.join(parts[:i + 1])
                if (parent, child) not in self.hierarchy_edges:
                    self.import_graph.add_edge(parent, child)
                    self.hierarchy_edges.add((parent, child))

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(file_path))
            except Exception:
                continue

            imports = set()
            used_identifiers = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
                elif isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                        used_identifiers.add(func.value.id)

            # Import edges
            for imp in imports:
                for mod in module_to_file:
                    if mod.endswith(f".{imp}") or mod == imp:
                        if (src_module, mod) not in self.flow_edges:
                            self.import_graph.add_edge(src_module, mod)
                            self.flow_edges.add((src_module, mod))

            # Usage edges
            for used in used_identifiers:
                for mod in module_to_file:
                    if mod.endswith(f".{used}") or mod == used:
                        # Only add if not already an import or hierarchy edge
                        edge = (src_module, mod)
                        if edge not in self.flow_edges and edge not in self.hierarchy_edges and edge not in self.uses_edges:
                            self.import_graph.add_edge(src_module, mod)
                            self.uses_edges.add(edge)


    def visualize_graph(self):
        import matplotlib.patches as mpatches
        import matplotlib.lines as mlines
        from matplotlib.patches import FancyArrowPatch

        graph = self.import_graph
        if not graph.nodes:
            print("No nodes found.")
            return

        # Increase figure size to fit legend outside
        plt.figure(figsize=(20, 14))  # Adjusted width for legend space
        ax = plt.gca()

        # Layout
        pos = nx.spring_layout(graph, k=0.35, iterations=150, seed=42)

        # Draw nodes
        nx.draw_networkx_nodes(graph, pos, node_size=500, node_color='lightblue', edgecolors='black', linewidths=0.5)

        # Labels
        labels = {n: n.split('.')[-1] for n in graph.nodes}
        nx.draw_networkx_labels(graph, pos, labels, font_size=9, font_weight='bold')

        def draw_arrows(edgelist, color, style):
            for src, tgt in edgelist:
                if src not in pos or tgt not in pos:
                    continue
                arrow = FancyArrowPatch(
                    pos[src], pos[tgt],
                    connectionstyle="arc3,rad=0.08",
                    arrowstyle='-|>',
                    color=color,
                    linewidth=1.6,
                    linestyle=style,
                    mutation_scale=12
                )
                ax.add_patch(arrow)

        # Draw edges with arrows
        draw_arrows(self.hierarchy_edges, color='blue', style='solid')
        draw_arrows(self.flow_edges, color='red', style='dashed')
        draw_arrows(self.uses_edges, color='green', style='dotted')

        # Legend box: add labels with colors and edge types
        legend_items = [
            mlines.Line2D([], [], color='blue', label='Hierarchy'),
            mlines.Line2D([], [], color='red', linestyle='--', label='Imports'),
            mlines.Line2D([], [], color='green', linestyle=':', label='Uses'),
        ]

        # Add the legend box outside the plot area
        plt.legend(
            handles=legend_items, 
            loc='upper left', 
            fontsize=12, 
            title="Edge Types", 
            title_fontsize=14, 
            shadow=True, 
            bbox_to_anchor=(1.05, 1),  # Move the legend outside
            borderpad=1
        )

        plt.title("Python File Flow (Hierarchy, Imports, Usage)", fontsize=14, fontweight='bold')
        plt.axis('off')
        
        # Adjust layout to ensure no clipping and no unwanted line at the bottom
        plt.tight_layout(pad=5.0)  # Increase padding to avoid clipping
        plt.subplots_adjust(right=0.85)  # Adjust to fit the legend outside

        # Save the figure
        plt.savefig("file_dependency_graph3.png", dpi=300)
        print("✅ Graph saved to file_dependency_graph.png")
        plt.close()



    def export_interactive_graph(self, filename="graph.html"):
        from pyvis.network import Network
        net = Network(height="800px", width="100%", directed=True, notebook=False)
        net.barnes_hut(gravity=-8000, spring_length=150, central_gravity=0.3)

        for node in self.import_graph.nodes:
            net.add_node(node, label=node.split('.')[-1], title=node, shape='ellipse', size=20)

        def add_edges(edges, color, dashes):
            for src, tgt in edges:
                net.add_edge(src, tgt, color=color, arrows='to', width=2, dashes=dashes)

        add_edges(self.hierarchy_edges, color="blue", dashes=False)
        add_edges(self.flow_edges, color="red", dashes=True)
        add_edges(self.uses_edges, color="green", dashes=[2, 2])

        net.set_options("""
        var options = {
        "physics": {
            "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "springLength": 100
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
        },
        "edges": {
            "color": {
            "highlight": "#FFFFFF"
            }
        }
        }
        
        """)

        legend_html = """
        <div style='position: fixed; top: 10px; right: 10px; background-color: white; padding: 10px; border: 1px solid rgba(44, 44, 44, 0.822); border-radius: 5px; box-shadow: 2px 2px 4px rgba(0,0,0,0.2); font-size: 14px; font-weight: bold; z-index: 1000;'>
            <div style='margin-bottom: 5px; text-align: center; border-bottom: 1px solid #ccc; padding-bottom: 5px;'>Legend</div>
            <div style='color: blue; margin: 5px 0;'>&#x2501; Hierarchy</div>
            <div style='color: red; margin: 5px 0;'>&#x2504; Imports</div>
            <div style='color: green; margin: 5px 0;'>&#x2505; Uses</div>
        </div>
        """
        
        net.show(filename)
        
        # Read the file content
        with open(filename, 'r') as f:
            content = f.read()
        
        # Insert the legend before the closing body tag
        content = content.replace('</body>', f'{legend_html}</body>')
        
        # Write the modified content back
        with open(filename, 'w') as f:
            f.write(content)

        net.save_graph(filename)    
        print(f"✅ Interactive graph saved as: {filename}")



    def get_dependency_flow(self) -> Dict[str, List[str]]:
        flow = {}
        for src, tgt in self.import_graph.edges:
            flow.setdefault(src, []).append(tgt)
        return flow


# Run the analysis
repo_path = "/home/.../flask"
analyzer = PythonFileDependencyAnalyzer(repo_path)
analyzer.build_import_graph()
analyzer.export_interactive_graph("code_flow_graph.html")


flow_data = analyzer.get_dependency_flow()
print("Flow Data:", flow_data)

analyzer.visualize_graph()