"""
dijkstra.py
Manual implementation of Dijkstra's Shortest Path Algorithm
NO external routing libraries used
"""

import heapq

class DijkstraAlgorithm:
    """
    Dijkstra's Algorithm - Coded from Scratch
    Used by OSPF for shortest path calculation
    """
    
    def __init__(self, graph):
        """
        Initialize with network topology
        
        Args:
            graph: Dictionary representing network
                   {router: {neighbor: cost}}
        """
        self.graph = graph
        self.routers = list(graph.keys())
    
    def find_shortest_path(self, start, end=None, verbose=True):
        """
        Find shortest path using Dijkstra's algorithm
        
        Args:
            start: Starting router
            end: Destination router (optional)
            verbose: Print step-by-step execution
            
        Returns:
            distances: Dict of shortest distances
            previous: Dict for path reconstruction
        """
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"DIJKSTRA'S ALGORITHM - Starting from {start}")
            print(f"{'='*70}\n")
        
        # Step 1: Initialize distances and previous nodes
        distances = {router: float('infinity') for router in self.routers}
        distances[start] = 0
        previous = {router: None for router in self.routers}
        
        # Step 2: Priority queue (distance, router)
        priority_queue = [(0, start)]
        visited = set()
        
        iteration = 1
        
        # Step 3: Main loop
        while priority_queue:
            current_distance, current_router = heapq.heappop(priority_queue)
            
            # Skip if already visited
            if current_router in visited:
                continue
            
            visited.add(current_router)
            
            if verbose:
                print(f"📍 Iteration {iteration}: Examining {current_router}")
                print(f"   Current shortest distance: {current_distance}")
            
            # Check all neighbors
            if current_router in self.graph:
                for neighbor, cost in self.graph[current_router].items():
                    
                    if neighbor not in visited:
                        # Calculate new distance
                        new_distance = current_distance + cost
                        
                        if verbose:
                            print(f"   → Neighbor: {neighbor}")
                            print(f"      Current distance to {neighbor}: {distances[neighbor]}")
                            print(f"      New distance via {current_router}: {new_distance}")
                        
                        # Update if shorter path found
                        if new_distance < distances[neighbor]:
                            distances[neighbor] = new_distance
                            previous[neighbor] = current_router
                            heapq.heappush(priority_queue, (new_distance, neighbor))
                            
                            if verbose:
                                print(f"      ✅ UPDATED! New shortest path found")
                        else:
                            if verbose:
                                print(f"      ❌ No update (current path is shorter)")
            
            if verbose:
                print()
            
            iteration += 1
        
        return distances, previous
    
    def reconstruct_path(self, previous, start, end):
        """
        Reconstruct the shortest path from start to end
        
        Args:
            previous: Dictionary from find_shortest_path
            start: Starting router
            end: Destination router
            
        Returns:
            List representing the path
        """
        path = []
        current = end
        
        while current is not None:
            path.insert(0, current)
            current = previous[current]
        
        if path[0] != start:
            return None  # No path exists
        
        return path
    
    def calculate_all_paths(self, verbose=False):
        """
        Calculate shortest paths from all routers to all others
        
        Returns:
            Dictionary with all routing information
        """
        all_results = {}
        
        for router in self.routers:
            distances, previous = self.find_shortest_path(router, verbose=False)
            
            all_results[router] = {
                'distances': distances,
                'previous': previous,
                'paths': {}
            }
            
            # Reconstruct all paths
            for dest in self.routers:
                if dest != router:
                    path = self.reconstruct_path(previous, router, dest)
                    all_results[router]['paths'][dest] = path
        
        return all_results


def test_dijkstra():
    """Test function to demonstrate the algorithm"""
    
    # Simple test topology
    test_graph = {
        'A': {'B': 4, 'C': 2},
        'B': {'A': 4, 'C': 1, 'D': 5},
        'C': {'A': 2, 'B': 1, 'D': 8},
        'D': {'B': 5, 'C': 8}
    }
    
    dijkstra = DijkstraAlgorithm(test_graph)
    distances, previous = dijkstra.find_shortest_path('A', verbose=True)
    
    print("\n" + "="*70)
    print("FINAL RESULTS:")
    print("="*70)
    
    for node in test_graph:
        if node != 'A':
            path = dijkstra.reconstruct_path(previous, 'A', node)
            print(f"A → {node}: Distance = {distances[node]}, Path = {' → '.join(path)}")


if __name__ == "__main__":
    test_dijkstra()