from dijkstra import DijkstraAlgorithm
from datetime import datetime

NETWORK_TOPOLOGY = {
    'R0': {'R6': 64},
    'R1': {'R7': 64},
    'R2': {'R8': 64},
    'R3': {'R9': 64},
    'R4': {'R10': 64},
    'R5': {'R11': 64},
    'R6': {'R0': 64, 'R7': 64},
    'R7': {'R6': 64, 'R8': 64, 'R9': 64, 'R1': 64},  
    'R8': {'R7': 64, 'R9': 64, 'R2': 64},
    'R9': {'R8': 64, 'R10': 64, 'R3': 64, 'R7': 64}, 
    'R10': {'R9': 64, 'R11': 64, 'R4': 64},
    'R11': {'R10': 64, 'R5': 64}

}

def display_network_topology():
    """Display the network connections"""
    print("\n" + "="*70)
    print("NETWORK TOPOLOGY")
    print("="*70)
    print(f"{'Router':<10} {'Connected To':<15} {'Cost'}")
    print("-" * 70)
    for router, neighbors in NETWORK_TOPOLOGY.items():
        for neighbor, cost in neighbors.items():
            print(f"{router:<10} ↔ {neighbor:<15} {cost}")
    print()

def generate_routing_tables():    
    print("\n" + "="*70)
    print("OSPF ROUTING TABLE GENERATION")
    print("="*70)
    ospf = DijkstraAlgorithm(NETWORK_TOPOLOGY)
    all_routes = ospf.calculate_all_paths() 
    for router in NETWORK_TOPOLOGY.keys():
        print(f"\n{'='*70}")
        print(f"ROUTING TABLE FOR {router}")
        print(f"{'='*70}")
        print(f"{'Destination':<15} {'Cost':<10} {'Next Hop':<12} {'Path'}")
        print("-" * 70)     
        distances = all_routes[router]['distances']
        paths = all_routes[router]['paths']     
        for dest in NETWORK_TOPOLOGY.keys():
            if dest != router:
                cost = distances[dest]
                path = paths[dest]    
                if path and len(path) > 1:
                    next_hop = path[1]
                    path_str = " → ".join(path)
                else:
                    next_hop = "N/A"
                    path_str = "No path"       
                if cost != float('infinity'):
                    print(f"{dest:<15} {cost:<10} {next_hop:<12} {path_str}")
                else:
                    print(f"{dest:<15} {'∞':<10} {next_hop:<12} Unreachable")
    return all_routes

def validate_with_packet_tracer():
    print("\n" + "="*70)
    print("VALIDATION: PYTHON vs PACKET TRACER")
    print("="*70)

    packet_tracer_costs = {
        ('R0', 'R6'): 64,
        ('R1', 'R7'): 64,
        ('R2', 'R8'): 64,
        ('R3', 'R9'): 64,
        ('R4', 'R10'): 64,
        ('R5', 'R11'): 64,
        ('R6', 'R7'): 64,
        ('R7', 'R8'): 64,
        ('R7', 'R9'): 64,   
        ('R8', 'R9'): 64,
        ('R9', 'R10'): 64,
        ('R10', 'R11'): 64,
        ('R6', 'R0'): 64,
        ('R7', 'R1'): 64,
        ('R8', 'R2'): 64,
        ('R9', 'R3'): 64,
        ('R10', 'R4'): 64,
        ('R11', 'R5'): 64,
        ('R7', 'R6'): 64,
        ('R8', 'R7'): 64,
        ('R9', 'R7'): 64,   
        ('R9', 'R8'): 64,
        ('R10', 'R9'): 64,
        ('R11', 'R10'): 64,
    }

    ospf = DijkstraAlgorithm(NETWORK_TOPOLOGY)
    all_routes = ospf.calculate_all_paths()
    print(f"{'Route':<20} {'PT Cost':<12} {'Python Cost':<15} {'Status'}")
    print("-" * 70)
    matches = 0
    total = 0
    for (src, dst), pt_cost in packet_tracer_costs.items():
        python_cost = all_routes[src]['distances'][dst] 
        status = "MATCH" if python_cost == pt_cost else "MISMATCH" 
        if python_cost == pt_cost:
            matches += 1
        total += 1    
        print(f"{src}→{dst:<17} {pt_cost:<12} {python_cost:<15} {status}")
    accuracy = (matches / total * 100) if total > 0 else 0
    print("=" * 70)
    print(f"VALIDATION ACCURACY: {accuracy:.1f}% ({matches}/{total} routes matched)")
    print("=" * 70)
    return accuracy

def main():
    """Main execution"""
    print("="*70)
    print("MULTI-CAMPUS OSPF NETWORK SIMULATION")
    print("Manual Implementation - NO Built-in Routing Libraries")
    print(f"Simulation Time: {datetime.now()}")
    print("="*70)
    display_network_topology()
    print("\n🔹 Running OSPF SPF Algorithm...")
    routing_tables = generate_routing_tables()
    print("\n🔹 Validating Results...")
    accuracy = validate_with_packet_tracer()
    print("\n" + "="*70)
    print("SIMULATION COMPLETED SUCCESSFULLY")
    print("="*70)

if __name__ == "__main__":
    main()