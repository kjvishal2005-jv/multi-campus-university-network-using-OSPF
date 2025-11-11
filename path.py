from ospf_simulator import NETWORK_TOPOLOGY
from dijkstra import DijkstraAlgorithm


PC_TO_ROUTER = {
    "PC0": "R0", "PC1": "R0", "PC2": "R0",
    "PC3": "R1", "PC4": "R1", "PC5": "R1",
    "PC6": "R2", "PC7": "R2", "PC8": "R2",
    "PC9": "R3", "PC10": "R3", "PC11": "R3",
    "PC12": "R4", "PC13": "R4", "PC14": "R4",
    "PC15": "R5", "PC16": "R5", "PC17": "R5"
}


DISTANCE_KM_PER_HOP = 50     
BANDWIDTH_MBPS = 1.544       
SPEED_OF_LIGHT_FIBER = 2e8   
PACKET_SIZE_BYTES = 1500


def calculate_propagation_delay(distance_km):
    """Propagation delay (ms)"""
    distance_m = distance_km * 1000
    delay_s = distance_m / SPEED_OF_LIGHT_FIBER
    return delay_s * 1000  

def calculate_transmission_delay(packet_size_bytes, bandwidth_mbps):
    """Transmission delay (ms)"""
    packet_bits = packet_size_bytes * 8
    bandwidth_bps = bandwidth_mbps * 1e6
    delay_s = packet_bits / bandwidth_bps
    return delay_s * 1000 

def calculate_total_delay(hops):
    """Estimate total delay for a given hop count"""
    prop_delay = calculate_propagation_delay(DISTANCE_KM_PER_HOP * hops)
    trans_delay = calculate_transmission_delay(PACKET_SIZE_BYTES, BANDWIDTH_MBPS) * hops
    proc_delay = hops * 1.0     
    queue_delay = hops * 2.0    
    total = prop_delay + trans_delay + proc_delay + queue_delay
    return round(total, 3)


def find_pc_to_pc_path(src_pc, dst_pc):
    """Find path, cost, and delay from one PC to another"""
    if src_pc not in PC_TO_ROUTER or dst_pc not in PC_TO_ROUTER:
        return f" Invalid PC name(s). Valid PCs: {', '.join(PC_TO_ROUTER.keys())}"

    src_router = PC_TO_ROUTER[src_pc]
    dst_router = PC_TO_ROUTER[dst_pc]

    if src_router == dst_router:
        return f"{src_pc} and {dst_pc} are in the same network ({src_router}). No routing needed."

    ospf = DijkstraAlgorithm(NETWORK_TOPOLOGY)
    all_routes = ospf.calculate_all_paths()

    path = all_routes[src_router]["paths"].get(dst_router, [])
    cost = all_routes[src_router]["distances"].get(dst_router, float('inf'))

    if not path:
        return f" No route found between {src_router} and {dst_router}"

    hops = len(path) - 1
    delay = calculate_total_delay(hops)

    
    print("\n================= ROUTE INFORMATION =================")
    print(f"Source PC:        {src_pc}")
    print(f"Destination PC:   {dst_pc}")
    print(f"Connected Routers: {src_router} → {dst_router}")
    print(f"Path:             {' → '.join(path)}")
    print(f"Hop Count:        {hops}")
    print(f"Total OSPF Cost:  {cost}")
    print(f"Estimated Delay:  {delay} ms")
    print("=====================================================\n")


if __name__ == "__main__":
    print("=== PC-to-PC OSPF Route Finder ===")
    print("Example: PC0 → PC10")
    print("Type 'exit' anytime to quit.\n")

    while True:
        src = input("Enter Source PC: ").strip()
        if src.lower() == "exit":
            break
        dst = input("Enter Destination PC: ").strip()
        if dst.lower() == "exit":
            break
        find_pc_to_pc_path(src, dst)