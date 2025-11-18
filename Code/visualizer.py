import networkx as nx
from pyvis.network import Network
import json
import os

class RecommendationVisualizer:
    def __init__(self):
        self.categories = self._load_categories()
        
        # Categorical Colors (Bright/Neon versions for Dark Mode)
        self.cat_colors = {
            'food': '#FF4444',          # Bright Red
            'restaurant': '#00E5FF',    # Cyan
            'monument': '#FFD700',      # Gold
            'tourist_place': '#76FF03', # Lime Green
            'other': '#CCCCCC'          # Light Grey
        }
        
        # Edge Styling
        self.style = {
            'bg_edge_color': 'rgba(80, 80, 80, 0.2)',    # Dim grey
            'bg_edge_width': 1,
            'path_edge_color': '#00FFFF',                # NEON CYAN for highlighted connections
            'path_edge_width': 6,                        # Thick highlight
            'teleport_edge_color': '#FF00FF',            # Neon Magenta
            'node_font_size': 20,                        # Readable font
            'highlight_font_size': 32                    # Bigger font for highlights
        }

    def _load_categories(self):
        try:
            if os.path.exists('hyderabad_entities.json'):
                with open('hyderabad_entities.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lookup = {}
                    for cat, items in data.get('categorized', {}).items():
                        simple_cat = 'other'
                        if cat == 'food_items': simple_cat = 'food'
                        elif cat == 'restaurants': simple_cat = 'restaurant'
                        elif cat == 'monuments': simple_cat = 'monument'
                        elif cat == 'tourist_places': simple_cat = 'tourist_place'
                        for item in items:
                            lookup[item] = simple_cat
                    return lookup
            return {}
        except:
            return {}

    def get_node_color(self, node_name):
        cat = self.categories.get(node_name, 'other')
        return self.cat_colors.get(cat, '#CCCCCC')

    def _process_walk_data(self, G, recommendations):
        """Process data for Walk algorithms (Sequential Path)"""
        highlight_nodes = set()
        highlight_edges = set()
        teleport_edges = []
        path_sequence = []

        if recommendations:
            # Walks usually return {StartNode: [Path...]}
            values = list(recommendations.values())
            if values:
                raw_path = values[0] # Take the first path
                if isinstance(raw_path, list):
                    # Clean names
                    path_sequence = [item.split(' (')[0] if isinstance(item, str) else str(item) for item in raw_path]
                    
                    # 1. Add nodes
                    for n in path_sequence:
                        highlight_nodes.add(n)
                    
                    # 2. Add Start Key if missing
                    for k in recommendations.keys():
                         if "->" not in k: highlight_nodes.add(k)

                    # 3. Identify Sequential Edges
                    for i in range(len(path_sequence) - 1):
                        u, v = path_sequence[i], path_sequence[i+1]
                        if G.has_edge(u, v):
                            highlight_edges.add((u, v))
                            highlight_edges.add((v, u))
                        else:
                            teleport_edges.append((u, v))
                            
        return highlight_nodes, highlight_edges, teleport_edges, path_sequence

    def _process_simple_data(self, G, recommendations):
        """Process data for Simple/TF-IDF (Star Topology)"""
        highlight_nodes = set()
        highlight_edges = set()
        teleport_edges = [] # No teleports in simple mode
        path_sequence = []  # No sequence in simple mode

        if recommendations:
            for center, neighbors in recommendations.items():
                # Add Center
                highlight_nodes.add(center)
                
                # Add Neighbors and Connections
                if isinstance(neighbors, list):
                    for neighbor in neighbors:
                        # Clean name just in case
                        n_clean = neighbor.split(' (')[0]
                        highlight_nodes.add(n_clean)
                        
                        # In simple mode, we highlight the direct connection
                        if G.has_edge(center, n_clean):
                            highlight_edges.add((center, n_clean))
                            highlight_edges.add((n_clean, center))

        return highlight_nodes, highlight_edges, teleport_edges, path_sequence

    def generate_viz(self, G, recommendations, viz_type="simple"):
        # 1. Initialize Network
        net = Network(height="700px", width="100%", bgcolor="#000000", font_color="white")
        net.barnes_hut(gravity=-4000, central_gravity=0.1, spring_length=100, spring_strength=0.05, damping=0.4)

        # 2. Process Data based on Type
        if viz_type == "walk":
            highlight_nodes, highlight_edges, teleport_edges, path_sequence = self._process_walk_data(G, recommendations)
        else:
            highlight_nodes, highlight_edges, teleport_edges, path_sequence = self._process_simple_data(G, recommendations)

        # 3. Add ALL Nodes
        for node in G.nodes():
            is_highlight = node in highlight_nodes
            
            size = 45 if is_highlight else 20 
            font_size = self.style['highlight_font_size'] if is_highlight else 14 
            base_color = self.get_node_color(node)
            
            node_options = {
                'n_id': node,
                'label': node,
                'title': node,
                'size': size,
                'font': {'size': font_size, 'color': 'white', 'strokeWidth': 4, 'strokeColor': 'black'},
                'borderWidth': 4 if is_highlight else 1,
                'borderWidthSelected': 6,
                'color': {
                    'background': base_color,
                    'border': 'white' if is_highlight else base_color,
                    'highlight': {'border': '#FFFFFF', 'background': base_color}
                },
                'opacity': 1.0 if is_highlight else 0.3
            }

            net.add_node(**node_options)

        # 4. Add Edges
        for u, v in G.edges():
            # Check if this edge is in our highlight set
            is_path_edge = (u, v) in highlight_edges
            
            if is_path_edge:
                color = self.style['path_edge_color']
                width = self.style['path_edge_width']
            else:
                color = self.style['bg_edge_color']
                width = self.style['bg_edge_width']

            net.add_edge(u, v, color=color, width=width)

        # 5. Add Teleport Edges
        for u, v in teleport_edges:
            net.add_edge(u, v, color=self.style['teleport_edge_color'], width=4, dashes=True, title="Teleport")

        # Output
        try:
            return net.generate_html()
        except AttributeError:
            net.save_graph("temp.html")
            with open("temp.html", "r") as f:
                return f.read()