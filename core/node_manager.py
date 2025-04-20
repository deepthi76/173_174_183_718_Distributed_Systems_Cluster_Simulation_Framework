import json
import os
from datetime import datetime, timedelta
import threading
from docker_utils import DockerManager
import time

class NodeManager:
    def __init__(self):
        self.state_file = "cluster_state.json"
        self.nodes = {}
        self.pods = {}
        self.docker = DockerManager()
        self._recover_cluster_state()
        self._start_health_monitor()

    def _recover_cluster_state(self):
        """Full state recovery from Docker and JSON"""
        # 1. Rebuild nodes from Docker containers
        for name, container in self.docker.existing_nodes.items():
            self.nodes[name] = self.docker.get_container_info(container)

        # 2. Load pod assignments from JSON
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                state = json.load(f)
                
                # Restore pods and calculate resource usage
                for pod_id, pod in state.get('pods', {}).items():
                    node_id = pod['node_id']
                    
                    if node_id in self.nodes:  # Only if node exists
                        self.pods[pod_id] = pod
                        self.nodes[node_id]['pods'].append(pod_id)
                        self.nodes[node_id]['available_cpu'] -= pod['cpu_requirements']

        # 3. Cleanup and validate
        self._cleanup_orphaned_pods()
        self._validate_resources()
        self._save_state()

    def _cleanup_orphaned_pods(self):
        """Remove pods assigned to non-existent nodes"""
        orphaned_pods = [
            pod_id for pod_id, pod in self.pods.items()
            if pod['node_id'] not in self.nodes
        ]
        for pod_id in orphaned_pods:
            del self.pods[pod_id]

    def _validate_resources(self):
        """Ensure CPU allocations are valid"""
        for node in self.nodes.values():
            used_cpu = sum(
                self.pods[pod_id]['cpu_requirements']
                for pod_id in node['pods']
                if pod_id in self.pods
            )
            node['available_cpu'] = max(0, node['cpu_cores'] - used_cpu)

    def _save_state(self):
        """Persist pod assignments to JSON"""
        with open(self.state_file, 'w') as f:
            json.dump({
                'pods': self.pods,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

    def add_node(self, cpu_cores):
        """Add node with state persistence"""
        node_id = f"node_{len(self.nodes) + 1}"
        container = self.docker.create_node(node_id, cpu_cores)
        
        self.nodes[node_id] = {
            'id': node_id,
            'container_id': container.id,
            'cpu_cores': cpu_cores,
            'available_cpu': cpu_cores,
            'pods': [],
            'status': 'healthy',
            'last_heartbeat': datetime.now()
        }
        self._save_state()
        return node_id

    def add_pod(self, cpu_requirements):
        """Add pod with persistence"""
        pod_id = f"pod_{len(self.pods) + 1}"
        
        for node_id, node in self.nodes.items():
            if node['status'] == 'healthy' and node['available_cpu'] >= cpu_requirements:
                node['pods'].append(pod_id)
                node['available_cpu'] -= cpu_requirements
                self.pods[pod_id] = {
                    'id': pod_id,
                    'cpu_requirements': cpu_requirements,
                    'node_id': node_id,
                    'status': 'running'
                }
                self._save_state()
                return True
        return False

    def _start_health_monitor(self):
        """Monitor node health with state persistence"""
        def monitor():
            while True:
                for node_id, node in list(self.nodes.items()):
                    container = self.docker.existing_nodes.get(node_id)
                    
                    # Update status based on container state
                    if container:
                        node['status'] = 'healthy' if container.status == 'running' else 'unhealthy'
                    
                    # Handle failures
                    if node['status'] == 'unhealthy':
                        self._handle_node_failure(node_id)
                
                time.sleep(5)

        threading.Thread(target=monitor, daemon=True).start()

    def _handle_node_failure(self, node_id):
        """Handle node failure with state persistence"""
        failed_node = self.nodes[node_id]
        for pod_id in failed_node['pods'][:]:
            if self.add_pod(self.pods[pod_id]['cpu_requirements']):
                failed_node['pods'].remove(pod_id)
                failed_node['available_cpu'] += self.pods[pod_id]['cpu_requirements']
                self._save_state()

    def reset_state(self):
        """Full cluster reset"""
        # 1. Remove all containers
        for container in self.docker.existing_nodes.values():
            container.remove(force=True)
        
        # 2. Clear state
        self.docker.existing_nodes = {}
        self.nodes = {}
        self.pods = {}
        
        # 3. Remove state file
        if os.path.exists(self.state_file):
            os.remove(self.state_file)