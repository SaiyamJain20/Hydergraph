"""
Script 3: Co-occurrence Network Builder
Builds sentence, paragraph, and page-level co-occurrence networks
"""

import json
import networkx as nx
import re
from itertools import combinations
import pickle

class CooccurrenceNetworkBuilder:
    def __init__(self, entities_file='hyderabad_entities.json', 
                 scraped_file='scraped_data.json'):
        # Load entities
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities_data = json.load(f)
            self.entities = entities_data['all_entities']
        
        # Load scraped data
        with open(scraped_file, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        
        # Initialize networks
        self.sentence_network = nx.Graph()
        self.paragraph_network = nx.Graph()
        self.page_network = nx.Graph()
        
        # Add all entities as nodes
        for entity in self.entities:
            self.sentence_network.add_node(entity)
            self.paragraph_network.add_node(entity)
            self.page_network.add_node(entity)
    
    def normalize_text(self, text):
        """Normalize text for better matching"""
        # Convert to lowercase for matching
        return text.lower()
    
    def split_into_sentences(self, text):
        """Split text into sentences"""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def split_into_paragraphs(self, text):
        """Split text into paragraphs"""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if len(p.strip()) > 50]
    
    def find_entities_in_text(self, text):
        """Find which entities appear in the given text"""
        text_lower = self.normalize_text(text)
        found_entities = []
        
        for entity in self.entities:
            entity_lower = entity.lower()
            # Check if entity appears in text
            if entity_lower in text_lower:
                found_entities.append(entity)
        
        return found_entities
    
    def build_sentence_network(self):
        """Build network based on sentence co-occurrence"""
        print("Building sentence-level network...")
        
        for doc in self.documents:
            text = doc['text']
            sentences = self.split_into_sentences(text)
            
            for sentence in sentences:
                # Find entities in this sentence
                entities_in_sentence = self.find_entities_in_text(sentence)
                
                # Create edges for all pairs
                if len(entities_in_sentence) >= 2:
                    for e1, e2 in combinations(entities_in_sentence, 2):
                        if self.sentence_network.has_edge(e1, e2):
                            self.sentence_network[e1][e2]['weight'] += 1
                        else:
                            self.sentence_network.add_edge(e1, e2, weight=1)
        
        print(f"Sentence network: {self.sentence_network.number_of_nodes()} nodes, "
              f"{self.sentence_network.number_of_edges()} edges")
    
    def build_paragraph_network(self):
        """Build network based on paragraph co-occurrence"""
        print("Building paragraph-level network...")
        
        for doc in self.documents:
            text = doc['text']
            paragraphs = self.split_into_paragraphs(text)
            
            if not paragraphs:  # If no paragraph breaks, treat whole doc as one
                paragraphs = [text]
            
            for paragraph in paragraphs:
                # Find entities in this paragraph
                entities_in_paragraph = self.find_entities_in_text(paragraph)
                
                # Create edges for all pairs
                if len(entities_in_paragraph) >= 2:
                    for e1, e2 in combinations(entities_in_paragraph, 2):
                        if self.paragraph_network.has_edge(e1, e2):
                            self.paragraph_network[e1][e2]['weight'] += 1
                        else:
                            self.paragraph_network.add_edge(e1, e2, weight=1)
        
        print(f"Paragraph network: {self.paragraph_network.number_of_nodes()} nodes, "
              f"{self.paragraph_network.number_of_edges()} edges")
    
    def build_page_network(self):
        """Build network based on page/document co-occurrence"""
        print("Building page-level network...")
        
        for doc in self.documents:
            text = doc['text']
            
            # Find entities in this entire page/document
            entities_in_page = self.find_entities_in_text(text)
            
            # Create edges for all pairs
            if len(entities_in_page) >= 2:
                for e1, e2 in combinations(entities_in_page, 2):
                    if self.page_network.has_edge(e1, e2):
                        self.page_network[e1][e2]['weight'] += 1
                    else:
                        self.page_network.add_edge(e1, e2, weight=1)
        
        print(f"Page network: {self.page_network.number_of_nodes()} nodes, "
              f"{self.page_network.number_of_edges()} edges")
    
    def remove_isolated_nodes(self):
        """Remove nodes with no edges from all networks"""
        for network in [self.sentence_network, self.paragraph_network, 
                       self.page_network]:
            isolated = list(nx.isolates(network))
            network.remove_nodes_from(isolated)
            print(f"Removed {len(isolated)} isolated nodes")
    
    def build_all_networks(self):
        """Build all three networks"""
        self.build_sentence_network()
        self.build_paragraph_network()
        self.build_page_network()
        self.remove_isolated_nodes()
    
    def save_networks(self):
        """Save networks to files"""
        # Save as pickle for later analysis
        with open('sentence_network.pkl', 'wb') as f:
            pickle.dump(self.sentence_network, f)
        
        with open('paragraph_network.pkl', 'wb') as f:
            pickle.dump(self.paragraph_network, f)
        
        with open('page_network.pkl', 'wb') as f:
            pickle.dump(self.page_network, f)
        
        # Also save as GraphML for other tools
        nx.write_graphml(self.sentence_network, 'sentence_network.graphml')
        nx.write_graphml(self.paragraph_network, 'paragraph_network.graphml')
        nx.write_graphml(self.page_network, 'page_network.graphml')
        
        print("\nNetworks saved!")
        print("Pickle files: sentence_network.pkl, paragraph_network.pkl, page_network.pkl")
        print("GraphML files: sentence_network.graphml, paragraph_network.graphml, page_network.graphml")
    
    def get_network_stats(self):
        """Get basic statistics for all networks"""
        stats = {}
        
        for name, network in [('Sentence', self.sentence_network),
                             ('Paragraph', self.paragraph_network),
                             ('Page', self.page_network)]:
            stats[name] = {
                'nodes': network.number_of_nodes(),
                'edges': network.number_of_edges(),
                'density': nx.density(network),
                'components': nx.number_connected_components(network)
            }
        
        return stats

if __name__ == "__main__":
    # Build networks
    builder = CooccurrenceNetworkBuilder()
    builder.build_all_networks()
    
    # Save networks
    builder.save_networks()
    
    # Print statistics
    print("\n=== Network Statistics ===")
    stats = builder.get_network_stats()
    for network_name, network_stats in stats.items():
        print(f"\n{network_name} Network:")
        for metric, value in network_stats.items():
            print(f"  {metric}: {value}")
