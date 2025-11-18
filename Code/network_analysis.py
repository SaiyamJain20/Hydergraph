"""
Script 4: Network Analysis
Analyzes the networks - degree distribution, centrality measures, etc.
"""

import pickle
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import pandas as pd

class NetworkAnalyzer:
    def __init__(self):
        # Load networks
        with open('sentence_network.pkl', 'rb') as f:
            self.sentence_network = pickle.load(f)
        
        with open('paragraph_network.pkl', 'rb') as f:
            self.paragraph_network = pickle.load(f)
        
        with open('page_network.pkl', 'rb') as f:
            self.page_network = pickle.load(f)
        
        self.networks = {
            'Sentence': self.sentence_network,
            'Paragraph': self.paragraph_network,
            'Page': self.page_network
        }
    
    def plot_degree_distribution(self):
        """Plot degree distribution for all networks"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        for idx, (name, network) in enumerate(self.networks.items()):
            degrees = [d for n, d in network.degree()]
            
            # Count degree frequencies
            degree_counts = Counter(degrees)
            degrees_sorted = sorted(degree_counts.keys())
            counts = [degree_counts[d] for d in degrees_sorted]
            
            # Plot
            axes[idx].bar(degrees_sorted, counts, alpha=0.7)
            axes[idx].set_xlabel('Degree', fontsize=12)
            axes[idx].set_ylabel('Frequency', fontsize=12)
            axes[idx].set_title(f'{name} Network\nDegree Distribution', fontsize=14)
            axes[idx].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('degree_distribution.png', dpi=300, bbox_inches='tight')
        print("Saved: degree_distribution.png")
        plt.close()
    
    def plot_log_degree_distribution(self):
        """Plot log-log degree distribution (check for power law)"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        for idx, (name, network) in enumerate(self.networks.items()):
            degrees = [d for n, d in network.degree() if d > 0]
            
            # Count degree frequencies
            degree_counts = Counter(degrees)
            degrees_sorted = sorted(degree_counts.keys())
            counts = [degree_counts[d] for d in degrees_sorted]
            
            # Plot log-log
            axes[idx].loglog(degrees_sorted, counts, 'o', alpha=0.6)
            axes[idx].set_xlabel('Degree (log)', fontsize=12)
            axes[idx].set_ylabel('Frequency (log)', fontsize=12)
            axes[idx].set_title(f'{name} Network\nLog-Log Degree Distribution', fontsize=14)
            axes[idx].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('log_degree_distribution.png', dpi=300, bbox_inches='tight')
        print("Saved: log_degree_distribution.png")
        plt.close()
    
    def calculate_centrality_measures(self):
        """Calculate various centrality measures"""
        results = {}
        
        for name, network in self.networks.items():
            print(f"\nCalculating centrality for {name} network...")
            
            # Degree centrality
            degree_cent = nx.degree_centrality(network)
            
            # Eigenvector centrality
            try:
                eigen_cent = nx.eigenvector_centrality(network, max_iter=1000)
            except:
                eigen_cent = {n: 0 for n in network.nodes()}
                print(f"  Warning: Eigenvector centrality failed for {name}")
            
            # Betweenness centrality
            betweenness_cent = nx.betweenness_centrality(network)
            
            # Closeness centrality
            closeness_cent = nx.closeness_centrality(network)
            
            results[name] = {
                'degree': degree_cent,
                'eigenvector': eigen_cent,
                'betweenness': betweenness_cent,
                'closeness': closeness_cent
            }
        
        return results
    
    def get_top_nodes(self, centrality_results, top_n=10):
        """Get top nodes for each centrality measure"""
        top_nodes = {}
        
        for network_name, centralities in centrality_results.items():
            top_nodes[network_name] = {}
            
            for measure_name, measure_dict in centralities.items():
                sorted_nodes = sorted(measure_dict.items(), 
                                    key=lambda x: x[1], reverse=True)
                top_nodes[network_name][measure_name] = sorted_nodes[:top_n]
        
        return top_nodes
    
    def print_top_nodes(self, top_nodes):
        """Print top nodes for each measure"""
        for network_name, measures in top_nodes.items():
            print(f"\n{'='*60}")
            print(f"{network_name} Network - Top 10 Nodes")
            print(f"{'='*60}")
            
            for measure_name, nodes in measures.items():
                print(f"\n{measure_name.upper()} Centrality:")
                for i, (node, value) in enumerate(nodes, 1):
                    print(f"  {i}. {node}: {value:.4f}")
    
    def save_centrality_to_csv(self, centrality_results):
        """Save centrality measures to CSV files"""
        for network_name, centralities in centrality_results.items():
            df_data = {}
            
            for measure_name, measure_dict in centralities.items():
                df_data[measure_name] = measure_dict
            
            df = pd.DataFrame(df_data)
            df.index.name = 'entity'
            filename = f'{network_name.lower()}_centrality.csv'
            df.to_csv(filename)
            print(f"Saved: {filename}")
    
    def plot_centrality_comparison(self, centrality_results):
        """Plot comparison of centrality measures"""
        for network_name, centralities in centrality_results.items():
            fig, axes = plt.subplots(2, 2, figsize=(14, 12))
            fig.suptitle(f'{network_name} Network - Centrality Measures', 
                        fontsize=16, fontweight='bold')
            
            measures = ['degree', 'eigenvector', 'betweenness', 'closeness']
            positions = [(0,0), (0,1), (1,0), (1,1)]
            
            for measure, pos in zip(measures, positions):
                values = list(centralities[measure].values())
                
                axes[pos].hist(values, bins=30, alpha=0.7, edgecolor='black')
                axes[pos].set_xlabel(f'{measure.capitalize()} Centrality', fontsize=11)
                axes[pos].set_ylabel('Frequency', fontsize=11)
                axes[pos].set_title(f'{measure.capitalize()} Distribution', fontsize=12)
                axes[pos].grid(True, alpha=0.3)
            
            plt.tight_layout()
            filename = f'{network_name.lower()}_centrality_distribution.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Saved: {filename}")
            plt.close()
    
    def calculate_network_metrics(self):
        """Calculate various network metrics"""
        metrics = {}
        
        for name, network in self.networks.items():
            print(f"\nCalculating metrics for {name} network...")
            
            metrics[name] = {
                'nodes': network.number_of_nodes(),
                'edges': network.number_of_edges(),
                'density': nx.density(network),
                'avg_degree': np.mean([d for n, d in network.degree()]),
                'components': nx.number_connected_components(network),
                'avg_clustering': nx.average_clustering(network),
            }
            
            # Calculate diameter and avg path length for largest component
            if nx.is_connected(network):
                metrics[name]['diameter'] = nx.diameter(network)
                metrics[name]['avg_path_length'] = nx.average_shortest_path_length(network)
            else:
                largest_cc = max(nx.connected_components(network), key=len)
                subgraph = network.subgraph(largest_cc)
                metrics[name]['diameter'] = nx.diameter(subgraph)
                metrics[name]['avg_path_length'] = nx.average_shortest_path_length(subgraph)
        
        return metrics
    
    def print_metrics(self, metrics):
        """Print network metrics"""
        print("\n" + "="*70)
        print("NETWORK METRICS SUMMARY")
        print("="*70)
        
        df = pd.DataFrame(metrics).T
        print(df.to_string())
        df.to_csv('network_metrics.csv')
        print("\nSaved: network_metrics.csv")
    
    def visualize_networks(self, top_n=30):
        """Visualize the networks (showing top nodes)"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for idx, (name, network) in enumerate(self.networks.items()):
            # Get top nodes by degree
            degrees = dict(network.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], 
                             reverse=True)[:top_n]
            top_node_names = [n for n, d in top_nodes]
            
            # Create subgraph with top nodes
            subgraph = network.subgraph(top_node_names)
            
            # Calculate layout
            pos = nx.spring_layout(subgraph, k=0.5, iterations=50, seed=42)
            
            # Draw
            node_sizes = [degrees[n] * 50 for n in subgraph.nodes()]
            
            nx.draw_networkx_nodes(subgraph, pos, 
                                  node_size=node_sizes,
                                  node_color='lightblue',
                                  alpha=0.7, ax=axes[idx])
            
            nx.draw_networkx_edges(subgraph, pos, 
                                  alpha=0.3, ax=axes[idx])
            
            # Draw labels for top 10 nodes
            top_10_nodes = [n for n, d in top_nodes[:10]]
            labels = {n: n for n in top_10_nodes}
            nx.draw_networkx_labels(subgraph, pos, labels, 
                                   font_size=8, ax=axes[idx])
            
            axes[idx].set_title(f'{name} Network\n(Top {top_n} nodes)', 
                               fontsize=14, fontweight='bold')
            axes[idx].axis('off')
        
        plt.tight_layout()
        plt.savefig('network_visualization.png', dpi=300, bbox_inches='tight')
        print("\nSaved: network_visualization.png")
        plt.close()
    
    def run_complete_analysis(self):
        """Run complete analysis pipeline"""
        print("\n" + "="*70)
        print("STARTING NETWORK ANALYSIS")
        print("="*70)
        
        # Plot degree distributions
        print("\n1. Plotting degree distributions...")
        self.plot_degree_distribution()
        self.plot_log_degree_distribution()
        
        # Calculate centrality measures
        print("\n2. Calculating centrality measures...")
        centrality_results = self.calculate_centrality_measures()
        
        # Get top nodes
        top_nodes = self.get_top_nodes(centrality_results)
        self.print_top_nodes(top_nodes)
        
        # Save centrality to CSV
        print("\n3. Saving centrality measures...")
        self.save_centrality_to_csv(centrality_results)
        
        # Plot centrality distributions
        print("\n4. Plotting centrality distributions...")
        self.plot_centrality_comparison(centrality_results)
        
        # Calculate and print metrics
        print("\n5. Calculating network metrics...")
        metrics = self.calculate_network_metrics()
        self.print_metrics(metrics)
        
        # Visualize networks
        print("\n6. Visualizing networks...")
        self.visualize_networks()
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE!")
        print("="*70)

if __name__ == "__main__":
    analyzer = NetworkAnalyzer()
    analyzer.run_complete_analysis()
