"""
Main Runner Script for Hyderabad Cultural Network Project
Run this to execute the entire pipeline
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    required = [
        'networkx', 'matplotlib', 'pandas', 'numpy', 
        'requests','pyvis'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\n📦 Install with:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

def run_pipeline():
    """Run the complete pipeline"""
    print("="*70)
    print("HYDERABAD CULTURAL NETWORK PROJECT")
    print("Mapping Culture Through Food & Heritage")
    print("="*70)
    
    # Import here to avoid errors if files don't exist yet
    import importlib.util
    
    # Step 1: Entity Collection
    print("\n" + "="*70)
    print("STEP 1: ENTITY COLLECTION")
    print("="*70)
    
    try:
        spec = importlib.util.spec_from_file_location("entity_collection", "hyderabad_entities.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        collector = module.HyderabadEntityCollector()
        entities = collector.save_entities()
        print(f"✓ Collected {entities['total_count']} entities")
    except Exception as e:
        print(f"✗ Error in entity collection: {e}")
        return False
    
    # Step 2: Web Scraping
    print("\n" + "="*70)
    print("STEP 2: WEB SCRAPING")
    print("="*70)
    print("⏱️  This may take 5-10 minutes...")
    
    try:
        spec = importlib.util.spec_from_file_location("web_scraper", "web_scraper.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        scraper = module.HyderabadContentScraper()
        scraped_data = scraper.run_all_scrapers()
        print(f"✓ Scraped {len(scraped_data)} documents")
    except Exception as e:
        print(f"✗ Error in web scraping: {e}")
        import traceback
        traceback.print_exc()
        
        # Check if we have some data to continue
        if not Path('scraped_data.json').exists():
            print("❌ Cannot continue without scraped data.")
            return False
        else:
            print("⚠️  Using existing scraped data...")
    
    # Step 3: Network Building
    print("\n" + "="*70)
    print("STEP 3: NETWORK BUILDING")
    print("="*70)
    
    try:
        spec = importlib.util.spec_from_file_location("cooccurrence_network", "cooccurrence_network.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        builder = module.CooccurrenceNetworkBuilder()
        builder.build_all_networks()
        builder.save_networks()
        
        stats = builder.get_network_stats()
        print("\n✓ Networks built successfully!")
        
        for network_name, network_stats in stats.items():
            print(f"\n{network_name} Network:")
            print(f"  Nodes: {network_stats['nodes']}")
            print(f"  Edges: {network_stats['edges']}")
            print(f"  Density: {network_stats['density']:.4f}")
    except Exception as e:
        print(f"✗ Error in network building: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Network Analysis
    print("\n" + "="*70)
    print("STEP 4: NETWORK ANALYSIS (Static)")
    print("="*70)
    
    try:
        spec = importlib.util.spec_from_file_location("network_analysis", "network_analysis.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        analyzer = module.NetworkAnalyzer()
        analyzer.run_complete_analysis()
        
        print("\n✓ Static analysis complete!")
    except Exception as e:
        print(f"✗ Error in network analysis: {e}")
        import traceback
        traceback.print_exc()
        # Continue anyway - interactive viz is more important
    
    # Step 5: Interactive Visualization
    print("\n" + "="*70)
    print("STEP 5: INTERACTIVE VISUALIZATION")
    print("="*70)
    
    try:
        spec = importlib.util.spec_from_file_location("interactive_viz", "interactive_viz.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        visualizer = module.InteractiveNetworkVisualizer()
        visualizer.create_all_interactive_visualizations()
        visualizer.create_comparison_dashboard()
        
        print("\n✓ Interactive visualizations created!")
    except Exception as e:
        print(f"✗ Error in interactive visualization: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "="*70)
    print("🎉 PROJECT COMPLETE!")
    print("="*70)
    print("\n📂 Generated files:")
    print("\n  Data files:")
    print("    • hyderabad_entities.json")
    print("    • scraped_data.json")
    print("\n  Network files:")
    print("    • sentence_network.pkl / .graphml")
    print("    • paragraph_network.pkl / .graphml")
    print("    • page_network.pkl / .graphml")
    print("\n  Static Analysis (PNG/CSV):")
    print("    • degree_distribution.png")
    print("    • log_degree_distribution.png")
    print("    • network_visualization.png")
    print("    • *_centrality.csv (3 files)")
    print("    • *_centrality_distribution.png (3 files)")
    print("    • network_metrics.csv")
    print("\n  🌟 INTERACTIVE Visualizations (HTML):")
    print("    • dashboard.html ⭐ START HERE!")
    print("    • sentence_interactive.html")
    print("    • paragraph_interactive.html")
    print("    • page_interactive.html")
    
    print("\n" + "="*70)
    print("🎯 NEXT STEP: Open 'dashboard.html' in your web browser!")
    print("   You can zoom, pan, click nodes, and explore the networks!")
    print("="*70)
    
    return True

def run_individual_step(step):
    """Run an individual step of the pipeline"""
    import importlib.util
    
    if step == '1':
        spec = importlib.util.spec_from_file_location("entity_collection", "hyderabad_entities.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        collector = module.HyderabadEntityCollector()
        collector.save_entities()
        
    elif step == '2':
        spec = importlib.util.spec_from_file_location("web_scraper", "web_scraper.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        scraper = module.HyderabadContentScraper()
        scraper.run_all_scrapers()
        
    elif step == '3':
        spec = importlib.util.spec_from_file_location("cooccurrence_network", "cooccurrence_network.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        builder = module.CooccurrenceNetworkBuilder()
        builder.build_all_networks()
        builder.save_networks()
        
    elif step == '4':
        spec = importlib.util.spec_from_file_location("network_analysis", "network_analysis.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        analyzer = module.NetworkAnalyzer()
        analyzer.run_complete_analysis()
        
    elif step == '5':
        spec = importlib.util.spec_from_file_location("interactive_viz", "interactive_viz.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        visualizer = module.InteractiveNetworkVisualizer()
        visualizer.create_all_interactive_visualizations()
        visualizer.create_comparison_dashboard()

def main():
    """Main function"""
    print("\n🕸️ Hyderabad Cultural Network Project")
    print("="*70)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        return
    
    print("✓ All dependencies found\n")
    
    # Ask user what to do
    print("Options:")
    print("  1. Run complete pipeline (RECOMMENDED)")
    print("  2. Run individual step")
    print("  3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        run_pipeline()
    elif choice == '2':
        print("\nSteps:")
        print("  1. Entity Collection")
        print("  2. Web Scraping")
        print("  3. Network Building")
        print("  4. Static Network Analysis")
        print("  5. Interactive Visualization")
        
        step = input("\nEnter step (1-5): ").strip()
        if step in ['1', '2', '3', '4', '5']:
            run_individual_step(step)
        else:
            print("❌ Invalid step")
    else:
        print("👋 Exiting...")

if __name__ == "__main__":
    main()