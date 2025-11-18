from flask import Flask, request, jsonify, render_template_string
import networkx as nx
import spacy
import numpy as np
import random
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Import your visualizer
from visualizer import RecommendationVisualizer

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- MODIFIED: Load all graphs ---
GRAPHS = {
    "sentence": None,
    "paragraph": None,
    "page": None
}
IDF_WEIGHTS = {
    "sentence": {},
    "paragraph": {},
    "page": {}
}
# --- END MODIFIED ---

nlp = None
gemini_model = "gemini-2.5-flash-lite"
viz = RecommendationVisualizer() 

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-api-key-here')

def load_graph_and_models():
    """Load ALL graphs and the NLP model"""
    global GRAPHS, IDF_WEIGHTS, nlp, gemini_model
    
    # Load spacy model
    try:
        nlp = spacy.load("en_core_web_sm")
        print("✅ Spacy 'en_core_web_sm' model loaded.")
    except IOError:
        print("❌ Spacy model 'en_core_web_sm' not found. Please install it with:")
        print("   python -m spacy download en_core_web_sm")
        exit()

    # --- MODIFIED: Load all three graphs ---
    for network_type in GRAPHS.keys():
        graph_path = f"{network_type}_network.graphml"
        modified_path = f"{network_type}_network_modified.graphml"
        
        load_path = None
        if os.path.exists(modified_path):
            load_path = modified_path
        elif os.path.exists(graph_path):
            load_path = graph_path
            
        if load_path:
            try:
                G = nx.read_graphml(load_path)
                GRAPHS[network_type] = G
                IDF_WEIGHTS[network_type] = calculate_inverse_frequency_weights(G)
                print(f"✅ Graph '{load_path}' loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
            except Exception as e:
                print(f"❌ Error loading graph '{load_path}': {e}")
                # Create dummy graph to avoid crash
                GRAPHS[network_type] = nx.Graph() 
        else:
            print(f"⚠️ WARNING: Graph file '{graph_path}' not found. {network_type} network will be empty.")
            GRAPHS[network_type] = nx.Graph() # Create empty graph
    # --- END MODIFIED ---

    # Initialize Gemini API
    try:
        if GEMINI_API_KEY and GEMINI_API_KEY != 'your-api-key-here':
            genai.configure(api_key=GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')
            print("✅ Gemini API initialized successfully.")
        else:
            print("⚠️ WARNING: Gemini API key not set. Natural language recommendations will be disabled.")
            gemini_model = None
    except Exception as e:
        print(f"⚠️ WARNING: Failed to initialize Gemini API: {e}")
        gemini_model = None

# ... (Keep all your helper functions: extract_entities, update_graph_with_entities) ...
def extract_entities(text, G, nlp):
    doc = nlp(text)
    ents = [ent.text for ent in doc.ents]
    filtered = [ent for ent in ents if ent in G.nodes]
    return filtered

def update_graph_with_entities(G, entities):
    for i in range(len(entities)):
        for j in range(i+1, len(entities)):
            e1 = entities[i]
            e2 = entities[j]
            if G.has_edge(e1, e2):
                G[e1][e2]["weight"] = G[e1][e2].get("weight", 1) + 1
            else:
                G.add_edge(e1, e2, weight=1)

def calculate_inverse_frequency_weights(G):
    N = G.number_of_nodes()
    if N == 0: return {}
    idf_weights = {}
    for node in G.nodes():
        degree = G.degree(node) 
        idf_weights[node] = np.log(N / (1 + degree))
    return idf_weights

def calculate_all_distances_to_node(G, end_node):
    if end_node not in G: return {}
    return nx.shortest_path_length(G, source=end_node)

# --- ALGORITHM DEFINITIONS (with **kwargs fix) ---

def recommend_simple(G, entity, top_k=5, **kwargs):
    """Recommends the top_k most co-occurring neighbors."""
    if entity not in G:
        return []

    neighbors = list(G.neighbors(entity))
    sorted_neighbors = sorted(
        neighbors,
        key=lambda x: G[entity][x].get("weight", 1),
        reverse=True
    )
    return sorted_neighbors[:top_k]

def recommend_pagerank(G, entity, top_k=5, **kwargs):
    """Recommends using personalized PageRank."""
    if entity not in G:
        return []

    pr = nx.pagerank(G, personalization={entity: 1})
    ranked = sorted(pr.items(), key=lambda x: x[1], reverse=True)
    ranked = [node for node, score in ranked if node != entity]
    return ranked[:top_k]

def calculate_inverse_frequency_weights(G):
    """Calculates the 'rarity' score for each node."""
    N = G.number_of_nodes()
    idf_weights = {}
    for node in G.nodes():
        degree = G.degree(node) 
        idf_weights[node] = np.log(N / (1 + degree))
    return idf_weights

def recommend_inverse_frequency(G, entity, top_k=5, **kwargs):
    """Recommends neighbors based on edge weight and node rarity."""
    if entity not in G:
        return []
    
    idf_weights = calculate_inverse_frequency_weights(G)
    
    neighbors = list(G.neighbors(entity))
    scored_neighbors = []
    
    for n in neighbors:
        original_weight = G[entity][n].get("weight", 1)
        idf_weight = idf_weights.get(n, 0)
        final_score = original_weight * idf_weight
        scored_neighbors.append((n, final_score))

    sorted_recs = sorted(scored_neighbors, key=lambda x: x[1], reverse=True)
    return [node for node, score in sorted_recs[:top_k]]

def recommend_random_walk(G, entity, length=None, **kwargs):
    """Performs a weighted random walk from a starting node."""
    if entity not in G:
        return []
    
    path = [entity]
    current_node = entity
    
    if length is None:
        length = random.randint(3, 8)
    
    for _ in range(length):
        neighbors = list(G.neighbors(current_node))
        valid_neighbors = [n for n in neighbors if n not in path]
        
        if not valid_neighbors:
            valid_neighbors = neighbors
            if not valid_neighbors:
                break
        
        weights = [G[current_node][n].get("weight", 1) for n in valid_neighbors]
        next_node = random.choices(valid_neighbors, weights=weights, k=1)[0]
        
        path.append(next_node)
        current_node = next_node
        
    return path # Return the path

def calculate_all_distances_to_node(G, end_node):
    """Calculates the shortest path length from every node TO the end_node."""
    if end_node not in G:
        return {}
    return nx.shortest_path_length(G, source=end_node)

def recommend_guided_walk(G, start_entity, end_entity, max_steps=None, **kwargs):
    """Generates an 'interesting' path from a start to an end entity."""
    if start_entity not in G or end_entity not in G:
        return []
    
    distances_to_end = calculate_all_distances_to_node(G, end_entity)
    path = [start_entity]
    current_node = start_entity
    
    if max_steps is None:
        max_steps = random.randint(7, 12)
    
    for _ in range(max_steps):
        if current_node == end_entity:
            break
            
        neighbors = list(G.neighbors(current_node))
        if len(path) > 1:
            neighbors = [n for n in neighbors if n != path[-2]]
        
        if not neighbors:
            break
        
        valid_neighbors = [n for n in neighbors if n not in path]
        
        if not valid_neighbors:
            valid_neighbors = neighbors
            if not valid_neighbors:
                break
            
        scored_neighbors = []
        for n in valid_neighbors:
            edge_weight = G[current_node][n].get("weight", 1)
            distance = distances_to_end.get(n, 99) 
            attraction_score = 1.0 / (1.0 + distance)
            final_score = edge_weight * attraction_score
            scored_neighbors.append((n, final_score))
        
        weights = [score for node, score in scored_neighbors]
        nodes = [node for node, score in scored_neighbors]
        next_node = random.choices(nodes, weights=weights, k=1)[0]
        
        path.append(next_node)
        current_node = next_node
        
    return path

def recommend_exploratory_walk(G, entity, length=None, teleport_prob=None, **kwargs):
    """Performs a weighted random walk with teleport probability."""
    if entity not in G:
        return []
    
    all_nodes = list(G.nodes())
    path = [entity]
    current_node = entity
    if length is None:
        length = random.randint(4, 10)
    if teleport_prob is None:
        teleport_prob = random.uniform(0.05, 0.4)
    
    for _ in range(length):
        p = random.random()
        valid_nodes = [n for n in all_nodes if n not in path]
        
        if p < teleport_prob:
            next_node = random.choice(valid_nodes)
            path.append(f"{next_node} (Detour!)")
            current_node = next_node
            continue
            
        neighbors = list(G.neighbors(current_node))
        if not neighbors:
            break
            
        valid_neighbors = [n for n in neighbors if n not in path]
        
        if not valid_neighbors:
            next_node = random.choice(valid_nodes)
            path.append(f"{next_node} (Detour!)")
            current_node = next_node
            continue
            
        weights = [G[current_node][n].get("weight", 1) for n in valid_neighbors]
        next_node = random.choices(valid_neighbors, weights=weights, k=1)[0]
        
        path.append(next_node)
        current_node = next_node
        
    return path

def recommend_guided_exploratory_walk(G, start_entity, end_entity, max_steps=None, teleport_prob=None, **kwargs):
    """Generates a 'guided but adventurous' path from a start to an end entity."""
    if start_entity not in G or end_entity not in G:
        return []
    
    distances_to_end = calculate_all_distances_to_node(G, end_entity)
    all_nodes = list(G.nodes())
    path = [start_entity]
    current_node = start_entity
    if max_steps is None:
        max_steps = random.randint(12, 18)
    if teleport_prob is None:
        teleport_prob = random.uniform(0.05, 0.4)
    
    for _ in range(max_steps):
        if current_node == end_entity:
            break
        
        valid_nodes = [n for n in all_nodes if n not in path]
        
        p = random.random()
        if p < teleport_prob:
            teleport_target = random.choice(valid_nodes)
            while teleport_target in [start_entity, end_entity]:
                teleport_target = random.choice(valid_nodes)
            
            path.append(f"{teleport_target} (Detour!)")
            current_node = teleport_target
            continue

        neighbors = list(G.neighbors(current_node))
        if len(path) > 1 and path[-2] in neighbors:
            prev_node = path[-2].split(' ')[0]
            if prev_node in neighbors:
                neighbors.remove(prev_node)
        
        if not neighbors:
            next_node = random.choice(valid_nodes)
            path.append(f"{next_node} (Detour!)")
            current_node = next_node
            continue
        
        valid_neighbors = [n for n in neighbors if n not in path]
        
        if not valid_neighbors:
            next_node = random.choice(valid_nodes)
            path.append(f"{next_node} (Detour!)")
            current_node = next_node
            continue
            
        scored_neighbors = []
        for n in valid_neighbors:
            edge_weight = G[current_node][n].get("weight", 1)
            distance = distances_to_end.get(n, 99)
            attraction_score = 1.0 / (1.0 + distance)
            final_score = edge_weight * attraction_score
            scored_neighbors.append((n, final_score))
        
        weights = [score for node, score in scored_neighbors]
        nodes = [node for node, score in scored_neighbors]
        next_node = random.choices(nodes, weights=weights, k=1)[0]
        
        path.append(next_node)
        current_node = next_node
        
    return path

# --- END ALGORITHM DEFINITIONS ---

RECOMMENDERS = {
    'simple': {'name': 'Simple Co-occurrence', 'description': 'Most frequently co-occurring neighbors', 'function': recommend_simple},
    'pagerank': {'name': 'PageRank', 'description': 'Personalized PageRank-based recommendations', 'function': recommend_pagerank},
    'inverse_frequency': {'name': 'Inverse Frequency', 'description': 'Balances popularity with rarity', 'function': recommend_inverse_frequency},
    'random_walk': {'name': 'Random Walk (Explore)', 'description': 'Weighted random walk paths', 'function': recommend_random_walk},
    'guided_walk': {'name': 'Guided Walk (A->B)', 'description': 'Finds a smart path between two entities', 'function': recommend_guided_walk},
    'exploratory_walk': {'name': 'Exploratory Walk (Explore + Detours)', 'description': 'Random walk with teleportation', 'function': recommend_exploratory_walk},
    'guided_exploratory_walk': {'name': 'Guided Exploratory (A->B + Detours)', 'description': 'Guided path with random "detours"', 'function': recommend_guided_exploratory_walk}
}

# ... (Keep your generate_natural_language_recommendation function) ...
def generate_natural_language_recommendation(user_text, entities, recommendations, recommender_name):
    """Use Gemini API to convert recommendations into natural language"""
    if not gemini_model:
        return None
    try:
        recs_text = ""
        for entity, recs in recommendations.items():
            if isinstance(recs, list):
                recs_str = ", ".join(recs)
            else:
                recs_str = str(recs)
            recs_text += f"For {entity}: {recs_str}\n"
        is_guided_path = "→" in list(recommendations.keys())[0] if recommendations else False
        is_question = any(word in user_text.lower() for word in ['?', 'what', 'where', 'how', 'which', 'recommend', 'suggest', 'looking for', 'need', 'want'])
        
        if is_guided_path:
            context_type = "path/route"
            user_context = f"User requested a path: {user_text}"
        elif is_question:
            context_type = "question/request"
            user_context = f"User asked: {user_text}"
        else:
            context_type = "experience"
            user_context = f"User shared: {user_text}"
        
        prompt = f"""You are a knowledgeable local guide for Hyderabad, India. Based on the user's input and algorithmic recommendations, provide a helpful response.

{user_context}
Algorithm Used: {recommender_name}
Entities/Locations: {', '.join(entities)}
Recommendations:
{recs_text}

Context: This is a {context_type} where the user {"wants navigation between specific places" if is_guided_path else ("is asking for suggestions" if is_question else "shared their experience")}.

CRITICAL REQUIREMENTS:
- Respond with EXACTLY 1-2 sentences
- Be natural, conversational, and helpful
- Integrate all the required places/food that the recommendations include and also don't change the order of the recommendation, just try to connect them
- Do not at any point change the order of recommendation even if it is required, it must stay the same as the recommender outputs
- Do not remove any place/food from the recommendation at any cost
- Adapt your tone to the user's input type (experience sharing, question asking, or route planning)
- Do NOT list items; integrate them into sentences

Generate an appropriate response and make sure to not remove orr change the ordering of the recommendation:"""
        response = gemini_model.generate_content(prompt)
        
        if response and response.text:
            sentences = response.text.strip().split('.')
            if len(sentences) > 2:
                result = '. '.join(sentences[:2]) + '.'
            else:
                result = response.text.strip()
            result = result.strip()
            if not result.endswith(('.', '!', '?')):
                result += '.'
            return result
        
    except Exception as e:
        print(f"Error generating natural language recommendation: {e}")
        return None
    return None

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """API endpoint for recommendations"""
    global GRAPHS, IDF_WEIGHTS, nlp, viz
    
    data = request.json
    text = data.get('text', '')
    recommender_type = data.get('recommender', 'simple')
    start_entity = data.get('start_entity', '')
    end_entity = data.get('end_entity', '')
    
    # --- NEW: Get Network Type and Walk Parameters ---
    network_type = data.get('network', 'sentence') # Default to sentence
    try:
        max_steps = int(data.get('max_steps', 10))
        teleport_prob = float(data.get('teleport_prob', 0.1))
    except ValueError:
        return jsonify({'error': 'Invalid max_steps or teleport_prob'}), 400
    # --- END NEW ---

    if recommender_type not in RECOMMENDERS:
        return jsonify({'error': 'Invalid recommender type'}), 400
    
    # --- NEW: Select the correct graph ---
    if network_type not in GRAPHS:
        return jsonify({'error': 'Invalid network type'}), 400
        
    G = GRAPHS[network_type]
    idf_weights = IDF_WEIGHTS[network_type]
    if G.number_of_nodes() == 0:
        return jsonify({'error': f'Network "{network_type}" is not loaded or is empty.'}), 500
    # --- END NEW ---
    
    is_guided_algorithm = recommender_type in ['guided_walk', 'guided_exploratory_walk']
    
    if is_guided_algorithm:
        if not start_entity.strip() or not end_entity.strip():
            return jsonify({'error': 'Guided algorithms require both start and end locations'}), 400
    else:
        if not text.strip():
            return jsonify({'error': 'Please provide text to analyze'}), 400
    
    try:
        recommender_func = RECOMMENDERS[recommender_type]['function']
        recommendations = {}
        entities = []
        
        # --- NEW: Pack all parameters for the algorithm ---
        algo_kwargs = {
            'idf_weights': idf_weights,
            'length': max_steps,
            'max_steps': max_steps,
            'teleport_prob': teleport_prob
        }
        
        if is_guided_algorithm:
            if start_entity not in G.nodes():
                return jsonify({'error': f'Starting location "{start_entity}" not found in {network_type} network.'}), 400
            if end_entity not in G.nodes():
                return jsonify({'error': f'Destination "{end_entity}" not found in {network_type} network.'}), 400
            
            path = recommender_func(G, start_entity, end_entity, **algo_kwargs)
            recommendations[f'{start_entity} → {end_entity}'] = path
            entities = [start_entity, end_entity]
            update_graph_with_entities(G, [start_entity, end_entity])
        else:
            entities = extract_entities(text, G, nlp)
            
            if not entities:
                return jsonify({
                    'text': text, 'entities': [], 'recommendations': {},
                    'message': f'No entities from your text were found in the {network_type} network.'
                })
            
            for entity in entities:
                recs = recommender_func(G, entity, **algo_kwargs)
                if recs:
                    recommendations[entity] = recs
            
            update_graph_with_entities(G, entities)
        
        viz_type = "walk" if 'walk' in recommender_type else "simple"
        viz_html = viz.generate_viz(G, recommendations, viz_type=viz_type)
        
        # --- NEW: Save the specific graph that was modified ---
        nx.write_graphml(G, f"{network_type}_network_modified.graphml")
        
        if is_guided_algorithm:
            optional_text = f" ({text})" if text.strip() else ""
            context_text = f"Find a route from {start_entity} to {end_entity}{optional_text}"
        else:
            context_text = text
            
        natural_language_rec = generate_natural_language_recommendation(
            context_text, entities, recommendations, RECOMMENDERS[recommender_type]['name']
        )
        
        response_data = {
            'text': context_text,
            'entities': entities,
            'recommendations': recommendations,
            'recommender': RECOMMENDERS[recommender_type]['name'],
            'visualization_html': viz_html,
            'network_used': network_type # Let the front-end know which network was used
        }
        
        if natural_language_rec:
            response_data['natural_language'] = natural_language_rec
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in /api/recommend: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/api/recommenders', methods=['GET'])
def get_recommenders():
    return jsonify({
        'recommenders': {k: {'name': v['name'], 'description': v['description']} 
                        for k, v in RECOMMENDERS.items()}
    })

@app.route('/')
def dashboard():
    with open('dashboard.html', 'r', encoding='utf-8') as f:
        return f.read()

# ... (Keep your other static routes: /sentence_interactive.html, etc.) ...
@app.route('/sentence_interactive.html')
def sentence_network():
    try:
        with open('sentence_interactive.html', 'r', encoding='utf-8') as f: return f.read()
    except FileNotFoundError: return "File not found", 404

@app.route('/paragraph_interactive.html')
def paragraph_network():
    try:
        with open('paragraph_interactive.html', 'r', encoding='utf-8') as f: return f.read()
    except FileNotFoundError: return "File not found", 404

@app.route('/page_interactive.html')
def page_network():
    try:
        with open('page_interactive.html', 'r', encoding='utf-8') as f: return f.read()
    except FileNotFoundError: return "File not found", 404

@app.route('/lib/<path:filename>')
def serve_lib_files(filename):
    """Serve library files"""
    try:
        file_path = f'lib/{filename}'
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Set appropriate content type based on file extension
        if filename.endswith('.css'):
            return content, 200, {'Content-Type': 'text/css'}
        elif filename.endswith('.js'):
            return content, 200, {'Content-Type': 'application/javascript'}
        else:
            return content
    except FileNotFoundError:
        return "File not found", 404
    except UnicodeDecodeError:
        # For binary files, serve them as binary
        try:
            with open(f'lib/{filename}', 'rb') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return "File not found", 404

if __name__ == '__main__':
    load_graph_and_models()
    app.run(debug=True, host='0.0.0.0', port=5000)