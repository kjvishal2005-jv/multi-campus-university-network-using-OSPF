from datetime import datetime
from dijkstra import DijkstraAlgorithm
import os
import csv

DEFAULT_PACKET_SIZE_BYTES = 1500
SPEED_OF_LIGHT_FIBER = 2e8
DEFAULT_PACKET_LOSS = 0.01
DEFAULT_UTILIZATION = 0.8

def propagation_delay_ms(distance_km):
    distance_m = distance_km * 1000.0
    delay_s = distance_m / SPEED_OF_LIGHT_FIBER
    return delay_s * 1000.0

def transmission_delay_ms(packet_size_bytes, bandwidth_mbps):
    packet_bits = packet_size_bytes * 8
    bw_bps = bandwidth_mbps * 1e6
    delay_s = packet_bits / bw_bps
    return delay_s * 1000.0

def effective_throughput_mbps(path_bandwidths_mbps, packet_loss=DEFAULT_PACKET_LOSS, utilization=DEFAULT_UTILIZATION):
    if not path_bandwidths_mbps:
        return 0.0
    min_bw = min(path_bandwidths_mbps)
    return round(min_bw * (1 - packet_loss) * utilization, 2)

def calculate_network_metrics(topology, packet_size_bytes=DEFAULT_PACKET_SIZE_BYTES):
    weights_graph = {}
    for node, neighs in topology.items():
        weights_graph[node] = {}
        for nbr, attrs in neighs.items():
            cost = attrs.get('cost', 64)
            weights_graph[node][nbr] = cost

    ospf = DijkstraAlgorithm(weights_graph)
    all_routes = ospf.calculate_all_paths()

    metrics = {}

    for src in topology.keys():
        metrics[src] = {}
        for dst in topology.keys():
            if src == dst:
                continue
            path = all_routes[src]['paths'].get(dst)
            if not path:
                continue

            link_costs = []
            prop_ms = 0.0
            trans_ms = 0.0
            path_bandwidths = []

            for i in range(len(path)-1):
                a = path[i]
                b = path[i+1]
                if a not in topology or b not in topology[a]:
                    attrs = topology.get(a, {}).get(b) or topology.get(b, {}).get(a)
                    if not attrs:
                        attrs = {'cost':64, 'distance_km':50, 'bandwidth_mbps':1000}
                else:
                    attrs = topology[a][b]

                link_costs.append(attrs.get('cost', 64))
                d_km = attrs.get('distance_km', 50)
                bw_mbps = attrs.get('bandwidth_mbps', 1000)
                prop_ms += propagation_delay_ms(d_km)
                trans_ms += transmission_delay_ms(packet_size_bytes, bw_mbps)
                path_bandwidths.append(bw_mbps)

            hops = max(len(path) - 1, 0)
            processing_ms = hops * 1.0
            queuing_ms = hops * 2.0

            total_delay_ms = round(prop_ms + trans_ms + processing_ms + queuing_ms, 4)
            python_throughput = effective_throughput_mbps(path_bandwidths)

            metrics[src][dst] = {
                'path_list': path,
                'path_str': ' -> '.join(path),
                'hops': hops,
                'ospf_cost': sum(link_costs),
                'delay': {
                    'propagation_ms': round(prop_ms, 4),
                    'transmission_ms': round(trans_ms, 4),
                    'processing_ms': round(processing_ms, 4),
                    'queuing_ms': round(queuing_ms, 4),
                    'total_delay_ms': total_delay_ms
                },
                'throughput_mbps': python_throughput,
                'path_bandwidths_mbps': path_bandwidths
            }

    return metrics

def save_metrics_to_file(topology, output_dir="output_reports", output_file="metric_results.txt", pt_csv="pt_metrics.csv"):
    metrics = calculate_network_metrics(topology)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)

    pt_data = {}
    if os.path.exists(pt_csv):
        try:
            with open(pt_csv, newline='', encoding='utf-8') as csvf:
                r = csv.DictReader(csvf)
                for row in r:
                    key = (row['Source'].strip(), row['Destination'].strip())
                    pt_data[key] = {
                        'pt_delay_ms': float(row.get('PT_Delay_ms', 0) or 0),
                        'pt_throughput_mbps': float(row.get('PT_Throughput_Mbps', 0) or 0),
                        'pt_ospf_cost': float(row.get('PT_OSPF_Cost', 0) or 0)
                    }
        except Exception:
            pt_data = {}

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("="*70 + "\n")
        f.write("NETWORK PERFORMANCE METRICS\n")
        f.write("="*70 + "\n")
        f.write(f"Generated on: {datetime.now()}\n")
        f.write("-"*70 + "\n")
        f.write(f"{'SRC':6} {'DST':6} {'HOPS':4} {'OSPF_COST':9} {'PY_DELAY(ms)':13} {'PT_DELAY(ms)':13} {'%ERR_DELAY':10} {'PY_TPUT(Mbps)':14} {'PT_TPUT(Mbps)':14} {'%ERR_TPUT':10}\n")
        f.write("-"*140 + "\n")

        for src in sorted(metrics.keys()):
            for dst in sorted(metrics[src].keys()):
                info = metrics[src][dst]
                key = (src, dst)
                py_delay = info['delay']['total_delay_ms']
                py_tput = info['throughput_mbps']
                py_cost = info['ospf_cost']

                pt_delay = pt_through = pt_cost = None
                delay_err = tput_err = cost_err = ""

                if key in pt_data:
                    pt_delay = pt_data[key]['pt_delay_ms']
                    pt_through = pt_data[key]['pt_throughput_mbps']
                    pt_cost = pt_data[key]['pt_ospf_cost']

                    if pt_delay:
                        delay_err = f"{abs(py_delay - pt_delay)/pt_delay*100:.2f}%"
                    else:
                        delay_err = "N/A"
                    if pt_through:
                        tput_err = f"{abs(py_tput - pt_through)/pt_through*100:.2f}%"
                    else:
                        tput_err = "N/A"
                    if pt_cost:
                        cost_err = f"{abs(py_cost - pt_cost)/pt_cost*100:.2f}%"
                    else:
                        cost_err = "N/A"
                else:
                    pt_delay = pt_through = pt_cost = "N/A"
                    delay_err = tput_err = cost_err = "N/A"

                f.write(f"{src:6} {dst:6} {info['hops']:4d} {py_cost:9d} {py_delay:13.4f} {str(pt_delay):13} {delay_err:10} {py_tput:14.2f} {str(pt_through):14} {tput_err:10}\n")

        f.write("\n" + "="*70 + "\n")
        f.write(f"Full details saved. See per-route breakdown below.\n\n")

        for src in sorted(metrics.keys()):
            f.write("\n" + "="*70 + "\n")
            f.write(f"METRICS FROM {src}\n")
            f.write("="*70 + "\n")
            for dst in sorted(metrics[src].keys()):
                info = metrics[src][dst]
                f.write(f"\nRoute: {src} -> {dst}\n")
                f.write(f"  Path: {info['path_str']}\n")
                f.write(f"  Hops: {info['hops']}\n")
                f.write(f"  OSPF Cost (sum of link costs): {info['ospf_cost']}\n")
                d = info['delay']
                f.write(f"  Delay (ms): total={d['total_delay_ms']}, prop={d['propagation_ms']}, tx={d['transmission_ms']}, proc={d['processing_ms']}, queue={d['queuing_ms']}\n")
                f.write(f"  Path link bandwidths (Mbps): {info['path_bandwidths_mbps']}\n")
                f.write(f"  Python Throughput (Mbps): {info['throughput_mbps']}\n")

        f.write("\n" + "="*70 + "\n")
        f.write(f"Metrics saved to: {output_path}\n")
        f.write("="*70 + "\n")

    print(f"\nResults saved to: {output_path}\n")
    if pt_data:
        print("Packet Tracer CSV detected and compared (see file for % error columns).")
    else:
        print("No Packet Tracer CSV provided. To compare, create pt_metrics.csv with headers: Source,Destination,PT_Delay_ms,PT_Throughput_Mbps,PT_OSPF_Cost")

def convert_simple_to_full(simple_topology):
    full = {}
    for a, nbrs in simple_topology.items():
        full[a] = {}
        for b, cost in nbrs.items():
            full[a][b] = {
                "cost": cost,
                "distance_km": 50,
                "bandwidth_mbps": 1.544
            }
    return full

if __name__ == "__main__":
    from ospf_simulator import NETWORK_TOPOLOGY
    NETWORK_TOPOLOGY = convert_simple_to_full(NETWORK_TOPOLOGY)
    save_metrics_to_file(NETWORK_TOPOLOGY)
