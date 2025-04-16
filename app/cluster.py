import threading, time

class Node:
    def __init__(self, node_id, cpu):
        self.id = node_id
        self.total_cpu = cpu
        self.available_cpu = cpu
        self.pods = []
        self.last_heartbeat = time.time()
        self.active = True

class Cluster:
    def __init__(self):
        self.nodes = {}
        self.heartbeat_log = []
        threading.Thread(target=self.monitor_heartbeats, daemon=True).start()

    def register_node(self, node_id, cpu):
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, cpu)

    def heartbeat(self, node_id, pods):
        node = self.nodes.get(node_id)
        if node:
            node.last_heartbeat = time.time()
            #node.pods = pods
            self.heartbeat_log.append((node_id, time.strftime("%X")))

    def schedule_pod(self, pod_id, cpu_needed):
        pod = {"id": pod_id, "cpu": cpu_needed}
        for node in self.nodes.values():
            if node.active and node.available_cpu >= cpu_needed:
                node.pods.append(pod)  # <-- store pod dict instead of just ID
                node.available_cpu -= cpu_needed
                return node.id
        return None


    def monitor_heartbeats(self):
        while True:
            now = time.time()
            for node in list(self.nodes.values()):
                if now - node.last_heartbeat > 10:
                    if node.active:
                        print(f"Node {node.id} failed.")
                        node.active = False
                        self.reschedule_pods(node)
            time.sleep(5)

    def reschedule_pods(self, failed_node):
        for pod in failed_node.pods:
            for node in self.nodes.values():
                if node.active and node.available_cpu >= pod["cpu"]:
                    node.pods.append(pod)
                    node.available_cpu -= pod["cpu"]
                    break


    def get_cluster_info(self):
        return [{
            "id": n.id,
            "total_cpu": n.total_cpu,
            "available_cpu": n.available_cpu,
            "pods": n.pods,
            "active": n.active
        } for n in self.nodes.values()]
