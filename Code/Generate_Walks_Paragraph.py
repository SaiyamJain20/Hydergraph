import networkx as nx
import numpy as np
import random
import os
import json
import itertools
import time
from tqdm import tqdm
from playwright.sync_api import sync_playwright

# Import the visualizer class from your file
# (Make sure visualizer.py is in the same directory)
try:
    from visualizer import RecommendationVisualizer
except ImportError:
    print("Error: visualizer.py not found.")
    print("Please make sure visualizer.py is in the same directory as this script.")
    exit()

# --- SETTINGS ---
SAMPLE_MODE = True  # SET TO FALSE to run all 16,815 combinations
N_EXPLORATORY_RUNS = 15
N_GUIDED_RUNS = 10
N_EXPLORATORY_SAMPLES = 3 if SAMPLE_MODE else 57
N_GUIDED_SAMPLES = 3 if SAMPLE_MODE else 1596

# --- ALGORITHMS & HELPERS ---
# (Pasted from your recommender_app.py for a self-contained script)

def calculate_idf(G):
    N = G.number_of_nodes()
    idf = {}
    if N == 0: return {}
    for node in G.nodes():
        degree = G.degree(node)
        idf[node] = np.log(N / (1 + degree)) if degree > -1 else 0
    return idf

def calculate_all_distances_to_node(G, end_node):
    if end_node not in G: return {}
    try:
        return nx.shortest_path_length(G, source=end_node)
    except:
        return {}

def recommend_exploratory_walk(G, entity, length=5, teleport_prob=0.1, **kwargs):
    if entity not in G: return []
    all_nodes = list(G.nodes())
    path = [entity]
    curr = entity
    for _ in range(length):
        if random.random() < teleport_prob:
            next_node = random.choice(all_nodes)
            path.append(f"{next_node} (Detour!)")
            curr = next_node
            continue
        neighbors = list(G.neighbors(curr))
        if not neighbors: break
        valid = [n for n in neighbors if n not in path]
        if not valid: valid = neighbors
        weights = [G[curr][n].get("weight", 1) for n in valid]
        next_node = random.choices(valid, weights=weights, k=1)[0]
        path.append(next_node)
        curr = next_node
    return path

def recommend_guided_exploratory_walk(G, start_entity, end_entity, max_steps=15, teleport_prob=0.1, **kwargs):
    if start_entity not in G or end_entity not in G: return []
    dists = calculate_all_distances_to_node(G, end_entity)
    all_nodes = list(G.nodes())
    path = [start_entity]
    curr = start_entity
    
    for _ in range(max_steps):
        if curr == end_entity: break
        
        # Teleport Logic
        if random.random() < teleport_prob:
            teleport_target = random.choice(all_nodes)
            while teleport_target in [start_entity, end_entity]:
                teleport_target = random.choice(all_nodes)
            path.append(f"{teleport_target} (Detour!)")
            curr = teleport_target
            continue

        # Normal Logic
        neighbors = list(G.neighbors(curr))
        if len(path) > 1 and path[-2] in neighbors: 
            prev_node = path[-2].split(' (')[0]
            if prev_node in neighbors:
                neighbors.remove(prev_node)
        
        if not neighbors:
            # Stuck? Force a detour
            teleport_target = random.choice(all_nodes)
            while teleport_target in [start_entity, end_entity, curr]:
                 teleport_target = random.choice(all_nodes)
            path.append(f"{teleport_target} (Detour!)")
            curr = teleport_target
            continue
            
        scored = []
        for n in neighbors:
            w = G[curr][n].get("weight", 1)
            d = dists.get(n, 99)
            score = w * (1.0 / (1.0 + d))
            scored.append((n, score))
        
        weights = [s for n,s in scored]
        nodes = [n for n,s in scored]
        next_node = random.choices(nodes, weights=weights, k=1)[0]
        path.append(next_node)
        curr = next_node
        
    return path

# --- SCREENSHOT FUNCTION ---

def save_html_as_png(playwright_context, html_content, output_path):
    """
    Uses Playwright to load HTML content and save a screenshot.
    """
    page = None
    try:
        page = playwright_context.new_page()
        # Set content from the HTML string
        page.set_content(html_content)
        # Wait for the network physics to hopefully settle
        page.wait_for_timeout(1000) 
        # Take screenshot
        page.screenshot(path=output_path, full_page=True, type='png')
    except Exception as e:
        print(f"  ...Error screenshotting {output_path}: {e}")
    finally:
        if page:
            page.close()

def sanitize_filename(name):
    """Removes invalid characters for filenames"""
    return name.replace(' ', '_').replace("'", "").replace("&", "and")

# --- MAIN EXECUTION ---

def run_batch_visualization():
    # 1. Load Graph
    try:
        G = nx.read_graphml("paragraph_network.graphml")
        print(f"Graph loaded: {G.number_of_nodes()} nodes.")
    except FileNotFoundError:
        print("Error: 'paragraph_network.graphml' not found.")
        return

    # 2. Setup
    viz = RecommendationVisualizer()
    all_nodes = list(G.nodes())
    all_pairs = list(itertools.combinations(all_nodes, 2))

    # 3. Create Output Directories
    output_dir = "walk_visualizations_paragraph"
    dir_exploratory = os.path.join(output_dir, "exploratory_walks")
    dir_guided = os.path.join(output_dir, "guided_walks")
    os.makedirs(dir_exploratory, exist_ok=True)
    os.makedirs(dir_guided, exist_ok=True)

    # 4. Handle Sampling
    nodes_to_process = all_nodes if not SAMPLE_MODE else random.sample(all_nodes, N_EXPLORATORY_SAMPLES)
    pairs_to_process = all_pairs if not SAMPLE_MODE else random.sample(all_pairs, N_GUIDED_SAMPLES)

    print("\n" + "="*50)
    print(f"  RUNNING IN {'SAMPLE' if SAMPLE_MODE else 'FULL'} MODE")
    print(f"  Exploratory Walks: {len(nodes_to_process)} nodes x {N_EXPLORATORY_RUNS} runs = {len(nodes_to_process) * N_EXPLORATORY_RUNS} images")
    print(f"  Guided Walks: {len(pairs_to_process)} pairs x {N_GUIDED_RUNS} runs = {len(pairs_to_process) * N_GUIDED_RUNS} images")
    print("="*50 + "\n")
    
    # 5. Launch Browser Context
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        
        # --- Part 1: Exploratory Walks ---
        print("Processing Exploratory Walks...")
        with tqdm(total=len(nodes_to_process) * N_EXPLORATORY_RUNS) as pbar:
            for start_node in nodes_to_process:
                for run in range(N_EXPLORATORY_RUNS):
                    pbar.set_description(f"Node: {start_node} (Run {run+1})")
                    
                    path = recommend_exploratory_walk(G, start_node, length=8, teleport_prob=0.15)
                    recs = {start_node: path}
                    html_content = viz.generate_viz(G, recs, "walk")
                    
                    filename = f"{sanitize_filename(start_node)}_run_{run+1}.png"
                    output_path = os.path.join(dir_exploratory, filename)
                    
                    save_html_as_png(context, html_content, output_path)
                    pbar.update(1)

        # --- Part 2: Guided Exploratory Walks ---
        print("\nProcessing Guided Exploratory Walks...")
        with tqdm(total=len(pairs_to_process) * N_GUIDED_RUNS) as pbar:
            for (start_node, end_node) in pairs_to_process:
                for run in range(N_GUIDED_RUNS):
                    pbar.set_description(f"Path: {start_node} -> {end_node} (Run {run+1})")
                    
                    path = recommend_guided_exploratory_walk(G, start_node, end_node, max_steps=20, teleport_prob=0.15)
                    recs = {f"{start_node} -> {end_node}": path}
                    html_content = viz.generate_viz(G, recs, "walk")
                    
                    filename = f"{sanitize_filename(start_node)}_to_{sanitize_filename(end_node)}_run_{run+1}.png"
                    output_path = os.path.join(dir_guided, filename)
                    
                    save_html_as_png(context, html_content, output_path)
                    pbar.update(1)
        
        # 6. Shutdown Browser
        browser.close()

    print("\n" + "="*50)
    print("BATCH VISUALIZATION COMPLETE!")
    print(f"Images saved to '{output_dir}' directory.")
    print("="*50)

if __name__ == "__main__":
    run_batch_visualization()