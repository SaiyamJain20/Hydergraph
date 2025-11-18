"""
Script 6: Interactive Network Visualization
Creates interactive HTML visualizations that you can zoom, pan, and explore
"""

import pickle
import networkx as nx
from pyvis.network import Network
import json

class InteractiveNetworkVisualizer:
    def __init__(self):
        # Load networks
        with open('sentence_network.pkl', 'rb') as f:
            self.sentence_network = pickle.load(f)
        
        with open('paragraph_network.pkl', 'rb') as f:
            self.paragraph_network = pickle.load(f)
        
        with open('page_network.pkl', 'rb') as f:
            self.page_network = pickle.load(f)
        
        # Load entities for categories
        with open('hyderabad_entities.json', 'r', encoding='utf-8') as f:
            self.entities_data = json.load(f)
    
    def get_node_category(self, node):
        """Determine what category a node belongs to"""
        categorized = self.entities_data['categorized']
        
        if node in categorized.get('food_items', []):
            return 'food'
        elif node in categorized.get('restaurants', []):
            return 'restaurant'
        elif node in categorized.get('monuments', []):
            return 'monument'
        elif node in categorized.get('tourist_places', []):
            return 'tourist_place'
        return 'other'
    
    def get_node_color(self, category):
        """Get color based on category"""
        colors = {
            'food': '#FF6B6B',          # Red
            'restaurant': '#4ECDC4',    # Teal
            'monument': '#FFE66D',      # Yellow
            'tourist_place': '#95E1D3', # Mint
            'other': '#CCCCCC'          # Gray
        }
        return colors.get(category, '#CCCCCC')
    
    def create_interactive_network(self, network, name, top_n=40):
        """Create an interactive visualization for a network"""
        print(f"\nCreating interactive visualization for {name} network...")
        
        # Get top nodes by degree
        degrees = dict(network.degree())
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_node_names = [n for n, d in top_nodes]
        
        # Create subgraph
        subgraph = network.subgraph(top_node_names)
        
        # Create pyvis network with better settings
        net = Network(
            height='900px', 
            width='100%', 
            bgcolor='#1a1a1a', 
            font_color='white',
            notebook=False,
            heading=f'{name} Network - Hyderabad Cultural Connections'
        )
        
        # Configure physics for better spacing
        net.barnes_hut(
            gravity=-15000,           # Reduced gravity for more spread
            central_gravity=0.1,      # Less central pull
            spring_length=250,        # Longer springs = more spacing
            spring_strength=0.001,    # Weaker springs
            damping=0.5,
            overlap=1                 # Avoid overlap
        )
        
        # Calculate node size range
        degrees_list = [degrees[n] for n in subgraph.nodes()]
        min_degree = min(degrees_list)
        max_degree = max(degrees_list)
        
        # Add nodes with SMALLER sizes
        for node in subgraph.nodes():
            category = self.get_node_category(node)
            color = self.get_node_color(category)
            degree = degrees[node]
            
            # SMALLER node sizes (reduced from 10 + degree*3 to 5 + degree*1.5)
            # Normalize size based on degree range
            if max_degree > min_degree:
                normalized = (degree - min_degree) / (max_degree - min_degree)
                size = 8 + (normalized * 20)  # Range: 8 to 28
            else:
                size = 15
            
            # Create hover title with info
            title = f"<b style='font-size: 16px;'>{node}</b><br>"
            title += f"<span style='font-size: 14px;'>Category: {category.replace('_', ' ').title()}</span><br>"
            title += f"<span style='font-size: 14px;'>Connections: {degree}</span>"
            
            net.add_node(
                node, 
                label=node,
                color=color,
                size=size,
                title=title,
                category=category,
                font={'size': 14, 'face': 'Arial', 'color': 'white'}
            )
        
        # Add edges with BETTER visibility
        for edge in subgraph.edges(data=True):
            source, target, data = edge
            weight = data.get('weight', 1)
            
            # THICKER edges (increased from 0.5 + weight*0.5)
            width = 1.5 + (weight * 0.8)
            
            # Edge color - more visible
            edge_color = 'rgba(150, 150, 150, 0.5)'
            
            net.add_edge(
                source, 
                target, 
                value=weight,
                width=width,
                title=f"<b>Co-occurrences: {weight}</b>",
                color=edge_color
            )
        
        # Set options for better visualization
        net.set_options("""
        {
          "nodes": {
            "borderWidth": 2,
            "borderWidthSelected": 4,
            "font": {
              "size": 14,
              "face": "Arial",
              "color": "white",
              "strokeWidth": 2,
              "strokeColor": "#000000"
            },
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.5)",
              "size": 10,
              "x": 2,
              "y": 2
            }
          },
          "edges": {
            "color": {
              "inherit": false,
              "color": "rgba(150,150,150,0.5)",
              "highlight": "rgba(255,255,255,0.9)",
              "hover": "rgba(200,200,200,0.8)"
            },
            "smooth": {
              "enabled": true,
              "type": "continuous",
              "roundness": 0.5
            },
            "width": 2,
            "selectionWidth": 3,
            "hoverWidth": 1.5
          },
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -15000,
              "centralGravity": 0.1,
              "springLength": 250,
              "springConstant": 0.001,
              "damping": 0.5,
              "avoidOverlap": 1
            },
            "maxVelocity": 30,
            "minVelocity": 0.75,
            "timestep": 0.35,
            "stabilization": {
              "enabled": true,
              "iterations": 1000,
              "updateInterval": 25
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "navigationButtons": true,
            "keyboard": {
              "enabled": true,
              "speed": {
                "x": 10,
                "y": 10,
                "zoom": 0.02
              }
            },
            "zoomView": true,
            "dragView": true
          }
        }
        """)
        
        # Save
        filename = f'{name.lower()}_interactive.html'
        net.save_graph(filename)
        
        # Add custom CSS for better text visibility
        self._add_custom_styling(filename)
        
        print(f"✓ Saved: {filename}")
        print(f"  - Nodes: {len(subgraph.nodes())}")
        print(f"  - Edges: {len(subgraph.edges())}")
        
        return filename
    
    def _add_custom_styling(self, filename):
        """Add custom CSS and JavaScript for better text visibility and click highlighting"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add custom styles and click handler
        custom_code = """
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }
            #mynetwork {
                width: 100%;
                height: 100vh;
                border: none;
            }
            .vis-network .vis-label {
                text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                font-weight: 600;
            }
            .vis-tooltip {
                background-color: rgba(0, 0, 0, 0.9) !important;
                border: 2px solid #4ECDC4 !important;
                border-radius: 8px !important;
                color: white !important;
                font-family: Arial, sans-serif !important;
                padding: 10px !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5) !important;
            }
        </style>
        <script type="text/javascript">
            // Wait for network to be initialized
            window.addEventListener('load', function() {
                // Get the network instance
                var container = document.getElementById('mynetwork');
                
                // Add click event listener
                network.on("click", function(params) {
                    if (params.nodes.length > 0) {
                        // Get clicked node
                        var clickedNodeId = params.nodes[0];
                        
                        // Get all connected nodes
                        var connectedNodes = network.getConnectedNodes(clickedNodeId);
                        
                        // Get all nodes
                        var allNodes = network.body.data.nodes.get({returnType: "Object"});
                        
                        // Update nodes: highlight connected ones
                        var updates = [];
                        for (var nodeId in allNodes) {
                            var node = allNodes[nodeId];
                            
                            if (nodeId === clickedNodeId) {
                                // Clicked node - extra thick border
                                updates.push({
                                    id: nodeId,
                                    borderWidth: 8,
                                    borderWidthSelected: 8,
                                    color: {
                                        border: '#FFD700',
                                        background: node.color.background || node.color
                                    }
                                });
                            } else if (connectedNodes.indexOf(nodeId) !== -1) {
                                // Connected nodes - highlighted border
                                updates.push({
                                    id: nodeId,
                                    borderWidth: 6,
                                    borderWidthSelected: 6,
                                    color: {
                                        border: '#00FF00',
                                        background: node.color.background || node.color
                                    }
                                });
                            } else {
                                // Other nodes - dim them slightly
                                var originalColor = node.color.background || node.color;
                                updates.push({
                                    id: nodeId,
                                    borderWidth: 2,
                                    borderWidthSelected: 2,
                                    color: {
                                        border: 'rgba(100,100,100,0.5)',
                                        background: originalColor
                                    },
                                    opacity: 0.3
                                });
                            }
                        }
                        
                        // Apply updates
                        network.body.data.nodes.update(updates);
                        
                        // Also highlight connected edges
                        var connectedEdges = network.getConnectedEdges(clickedNodeId);
                        var allEdges = network.body.data.edges.get({returnType: "Object"});
                        var edgeUpdates = [];
                        
                        for (var edgeId in allEdges) {
                            if (connectedEdges.indexOf(edgeId) !== -1) {
                                edgeUpdates.push({
                                    id: edgeId,
                                    width: 4,
                                    color: {color: 'rgba(0,255,0,0.8)'}
                                });
                            } else {
                                edgeUpdates.push({
                                    id: edgeId,
                                    color: {color: 'rgba(150,150,150,0.2)'}
                                });
                            }
                        }
                        
                        network.body.data.edges.update(edgeUpdates);
                        
                    } else {
                        // Click on empty space - reset all
                        resetHighlighting();
                    }
                });
                
                // Function to reset highlighting
                function resetHighlighting() {
                    var allNodes = network.body.data.nodes.get({returnType: "Object"});
                    var updates = [];
                    
                    for (var nodeId in allNodes) {
                        var node = allNodes[nodeId];
                        var originalColor = node.color.background || node.color;
                        
                        updates.push({
                            id: nodeId,
                            borderWidth: 2,
                            borderWidthSelected: 4,
                            color: {
                                border: originalColor,
                                background: originalColor
                            },
                            opacity: 1
                        });
                    }
                    
                    network.body.data.nodes.update(updates);
                    
                    // Reset edges
                    var allEdges = network.body.data.edges.get({returnType: "Object"});
                    var edgeUpdates = [];
                    
                    for (var edgeId in allEdges) {
                        edgeUpdates.push({
                            id: edgeId,
                            color: {color: 'rgba(150,150,150,0.5)'}
                        });
                    }
                    
                    network.body.data.edges.update(edgeUpdates);
                }
                
                // Double-click to reset
                network.on("doubleClick", function() {
                    resetHighlighting();
                });
            });
        </script>
        """
        
        content = content.replace('</head>', f'{custom_code}</head>')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_legend_html(self):
        """Create a legend HTML snippet"""
        legend = """
        <div style="position: fixed; top: 10px; right: 10px; background: rgba(0,0,0,0.9); 
                    padding: 20px; border-radius: 12px; color: white; font-family: Arial; 
                    z-index: 1000; border: 2px solid #4ECDC4; min-width: 200px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <h3 style="margin: 0 0 15px 0; color: #4ECDC4; border-bottom: 2px solid #4ECDC4; padding-bottom: 10px;">
                🗺️ Legend
            </h3>
            <div style="margin: 8px 0;"><span style="color: #FF6B6B; font-size: 24px;">●</span> <b>Food Items</b></div>
            <div style="margin: 8px 0;"><span style="color: #4ECDC4; font-size: 24px;">●</span> <b>Restaurants</b></div>
            <div style="margin: 8px 0;"><span style="color: #FFE66D; font-size: 24px;">●</span> <b>Monuments</b></div>
            <div style="margin: 8px 0;"><span style="color: #95E1D3; font-size: 24px;">●</span> <b>Tourist Places</b></div>
            <hr style="border-color: #555; margin: 15px 0;">
            <div style="font-size: 12px; line-height: 1.8;">
                <b style="color: #FFE66D;">🎮 Controls:</b><br>
                • <b>Drag background:</b> Pan<br>
                • <b>Scroll:</b> Zoom in/out<br>
                • <b>Click node:</b> Highlight connections 🌟<br>
                • <b>Double-click:</b> Reset highlighting<br>
                • <b>Drag node:</b> Reposition<br>
                • <b>Hover:</b> See details
            </div>
            <hr style="border-color: #555; margin: 15px 0;">
            <div style="font-size: 11px; line-height: 1.6;">
                <b style="color: #FFD700;">💡 Highlighting:</b><br>
                <span style="color: #FFD700;">🟡 Gold border</span> = Selected<br>
                <span style="color: #00FF00;">🟢 Green border</span> = Connected<br>
                <span style="color: #888;">⚪ Dimmed</span> = Not connected
            </div>
        </div>
        """
        return legend
    
    def add_legend_to_html(self, filename):
        """Add legend to HTML file"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add legend before closing body tag
        legend = self.create_legend_html()
        content = content.replace('</body>', f'{legend}</body>')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_all_interactive_visualizations(self):
        """Create interactive visualizations for all networks"""
        print("="*70)
        print("CREATING INTERACTIVE NETWORK VISUALIZATIONS")
        print("="*70)
        print("\n✨ Features:")
        print("  • Smaller, cleaner nodes")
        print("  • Thicker, more visible edges")
        print("  • Better spacing and layout")
        print("  • Enhanced text readability")
        print("  • 🌟 NEW: Click highlighting - see connections instantly!")
        
        networks = [
            (self.sentence_network, 'Sentence'),
            (self.paragraph_network, 'Paragraph'),
            (self.page_network, 'Page')
        ]
        
        files = []
        for network, name in networks:
            filename = self.create_interactive_network(network, name, top_n=40)
            self.add_legend_to_html(filename)
            files.append(filename)
        
        print("\n" + "="*70)
        print("✓ INTERACTIVE VISUALIZATIONS CREATED!")
        print("="*70)
        print("\nGenerated files:")
        for f in files:
            print(f"  • {f}")
        
        print("\n🌟 Pro tips:")
        print("  • Click on a node to highlight its connections (gold + green borders!)")
        print("  • Double-click anywhere to reset highlighting")
        print("  • Drag nodes around to see relationships better")
        print("  • Use scroll wheel to zoom in on clusters")
        print("  • Wait a few seconds for the layout to stabilize")
        
        return files
    
    def create_comparison_dashboard(self):
        """Create a single HTML dashboard with all three networks"""
        print("\nCreating comparison dashboard...")
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hyderabad Cultural Network - Dashboard</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Arial', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: white;
                }
                .header {
                    text-align: center;
                    margin-bottom: 50px;
                    animation: fadeIn 1s ease-in;
                }
                h1 {
                    font-size: 3em;
                    margin-bottom: 10px;
                    text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
                }
                .subtitle {
                    font-size: 1.2em;
                    opacity: 0.9;
                    margin-bottom: 20px;
                }
                .description {
                    max-width: 800px;
                    margin: 0 auto 40px;
                    background: rgba(0,0,0,0.3);
                    padding: 20px;
                    border-radius: 10px;
                    backdrop-filter: blur(10px);
                }
                .container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 30px;
                    max-width: 1400px;
                    margin: 0 auto;
                }
                .network-card {
                    background: rgba(255,255,255,0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 0;
                    text-decoration: none;
                    color: white;
                    transition: all 0.3s ease;
                    border: 2px solid rgba(255,255,255,0.2);
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                .network-card:hover {
                    transform: translateY(-10px);
                    box-shadow: 0 15px 40px rgba(0,0,0,0.5);
                    border-color: rgba(255,255,255,0.4);
                }
                .card-header {
                    background: linear-gradient(135deg, rgba(78, 205, 196, 0.8), rgba(69, 184, 176, 0.8));
                    padding: 30px;
                    text-align: center;
                }
                .network-icon {
                    font-size: 3em;
                    margin-bottom: 10px;
                }
                .network-title {
                    font-size: 2em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .card-body {
                    padding: 25px;
                }
                .network-desc {
                    font-size: 1em;
                    line-height: 1.6;
                    opacity: 0.9;
                    margin-bottom: 15px;
                }
                .network-stats {
                    background: rgba(0,0,0,0.3);
                    padding: 15px;
                    border-radius: 10px;
                    margin-top: 15px;
                }
                .stat-item {
                    display: flex;
                    justify-content: space-between;
                    padding: 5px 0;
                }
                .legend-section {
                    background: rgba(0,0,0,0.4);
                    padding: 30px;
                    border-radius: 20px;
                    max-width: 900px;
                    margin: 50px auto 0;
                    backdrop-filter: blur(10px);
                    border: 2px solid rgba(255,255,255,0.2);
                }
                .legend-title {
                    text-align: center;
                    font-size: 1.8em;
                    margin-bottom: 25px;
                    color: #FFE66D;
                }
                .legend-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .legend-item {
                    text-align: center;
                    padding: 15px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                }
                .legend-dot {
                    font-size: 2em;
                    margin-bottom: 5px;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(-20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .btn {
                    display: inline-block;
                    background: linear-gradient(135deg, #4ECDC4, #45b8b0);
                    padding: 15px 30px;
                    border-radius: 30px;
                    text-decoration: none;
                    color: white;
                    font-weight: bold;
                    margin-top: 15px;
                    transition: all 0.3s;
                }
                .btn:hover {
                    transform: scale(1.05);
                    box-shadow: 0 5px 15px rgba(78, 205, 196, 0.4);
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🕸️ Hyderabad Cultural Network</h1>
                <div class="subtitle">P15: Hydergraph - Mapping Culture Through Food & Heritage</div>
            </div>
            
            <div class="description">
                <p><strong>🎯 Project Overview:</strong> This interactive network visualization maps the cultural connections 
                between food, places, and heritage in Hyderabad. Each network represents different levels of association 
                between entities based on how they co-occur in online content.</p>
            </div>
            
            <div class="container">
                <a href="sentence_interactive.html" class="network-card">
                    <div class="card-header">
                        <div class="network-icon">💬</div>
                        <div class="network-title">Sentence Network</div>
                    </div>
                    <div class="card-body">
                        <div class="network-desc">
                            <strong>Strongest Associations</strong><br>
                            Shows entities that appear together in the same sentences - 
                            the most direct and immediate cultural connections.
                        </div>
                        <div class="network-stats">
                            <div class="stat-item">
                                <span>📊 Granularity:</span>
                                <span><strong>Highest</strong></span>
                            </div>
                            <div class="stat-item">
                                <span>🔗 Connection Type:</span>
                                <span><strong>Direct</strong></span>
                            </div>
                        </div>
                        <center><div class="btn">Explore Network →</div></center>
                    </div>
                </a>
                
                <a href="paragraph_interactive.html" class="network-card">
                    <div class="card-header">
                        <div class="network-icon">📝</div>
                        <div class="network-title">Paragraph Network</div>
                    </div>
                    <div class="card-body">
                        <div class="network-desc">
                            <strong>Moderate Associations</strong><br>
                            Shows entities discussed together in paragraphs - 
                            revealing thematic and contextual relationships.
                        </div>
                        <div class="network-stats">
                            <div class="stat-item">
                                <span>📊 Granularity:</span>
                                <span><strong>Medium</strong></span>
                            </div>
                            <div class="stat-item">
                                <span>🔗 Connection Type:</span>
                                <span><strong>Contextual</strong></span>
                            </div>
                        </div>
                        <center><div class="btn">Explore Network →</div></center>
                    </div>
                </a>
                
                <a href="page_interactive.html" class="network-card">
                    <div class="card-header">
                        <div class="network-icon">📄</div>
                        <div class="network-title">Page Network</div>
                    </div>
                    <div class="card-body">
                        <div class="network-desc">
                            <strong>Broad Associations</strong><br>
                            Shows entities mentioned in the same articles/pages - 
                            capturing the wider cultural landscape.
                        </div>
                        <div class="network-stats">
                            <div class="stat-item">
                                <span>📊 Granularity:</span>
                                <span><strong>Lowest</strong></span>
                            </div>
                            <div class="stat-item">
                                <span>🔗 Connection Type:</span>
                                <span><strong>Broad</strong></span>
                            </div>
                        </div>
                        <center><div class="btn">Explore Network →</div></center>
                    </div>
                </a>
            </div>
            
            <div class="legend-section">
                <div class="legend-title">🎨 Node Categories</div>
                <div class="legend-grid">
                    <div class="legend-item">
                        <div class="legend-dot" style="color: #FF6B6B;">●</div>
                        <strong>Food Items</strong><br>
                        <small>Biryani, Haleem, etc.</small>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="color: #4ECDC4;">●</div>
                        <strong>Restaurants</strong><br>
                        <small>Paradise, Bawarchi, etc.</small>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="color: #FFE66D;">●</div>
                        <strong>Monuments</strong><br>
                        <small>Charminar, Golconda, etc.</small>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="color: #95E1D3;">●</div>
                        <strong>Tourist Places</strong><br>
                        <small>Hussain Sagar, etc.</small>
                    </div>
                </div>
                
                <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <strong style="font-size: 1.2em; color: #FFE66D;">💡 How to Use:</strong>
                    <ul style="margin-top: 10px; line-height: 2; padding-left: 20px;">
                        <li><strong>Zoom:</strong> Scroll wheel to zoom in/out</li>
                        <li><strong>Pan:</strong> Drag background to move around</li>
                        <li><strong>🌟 Click node:</strong> Highlights all connected nodes with colored borders!</li>
                        <li><strong>Double-click:</strong> Reset highlighting</li>
                        <li><strong>Drag node:</strong> Reposition nodes</li>
                        <li><strong>Hover:</strong> See node details</li>
                    </ul>
                    <div style="margin-top: 15px; padding: 10px; background: rgba(255,215,0,0.1); border-left: 3px solid #FFD700; border-radius: 5px;">
                        <strong style="color: #FFD700;">✨ NEW: Click Highlighting</strong><br>
                        <small style="line-height: 1.6;">
                        When you click a node:<br>
                        • <span style="color: #FFD700;">Gold border</span> = Selected node<br>
                        • <span style="color: #00FF00;">Green borders</span> = Connected nodes<br>
                        • Dimmed = Unconnected nodes
                        </small>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open('dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✓ Created dashboard.html")
        print("\n🎯 START HERE: Open dashboard.html in your browser!")

if __name__ == "__main__":
    visualizer = InteractiveNetworkVisualizer()
    visualizer.create_all_interactive_visualizations()
    visualizer.create_comparison_dashboard()
    
    print("\n" + "="*70)
    print("🎉 All done! Open 'dashboard.html' in your browser!")
    print("="*70)
    print("\n✨ NEW FEATURE: Click any node to see its connections highlighted!")
    print("   • Gold border = Selected node")
    print("   • Green borders = Connected nodes")
    print("   • Double-click = Reset highlighting")
    print("="*70)