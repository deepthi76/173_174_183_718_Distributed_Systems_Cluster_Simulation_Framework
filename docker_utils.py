import docker
from datetime import datetime

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.node_prefix = "node_"
        self.existing_nodes = self._load_existing_containers()

    def _load_existing_containers(self):
        """Load all node containers with full inspection"""
        nodes = {}
        for container in self.client.containers.list(all=True):
            if container.name.startswith(self.node_prefix):
                nodes[container.name] = container
        return nodes

    def get_container_info(self, container):
        """Extract complete node information from container"""
        attrs = container.attrs
        cpuset = attrs['HostConfig']['CpusetCpus']
        cpu_cores = len(cpuset.split(',')) if cpuset else 1
        
        return {
            'id': container.name,
            'container_id': container.id,
            'cpu_cores': cpu_cores,
            'available_cpu': cpu_cores,  # Temporary value
            'pods': [],  # Will be populated from state file
            'status': 'healthy' if container.status == 'running' else 'unhealthy',
            'last_heartbeat': datetime.strptime(
                attrs['State']['StartedAt'][:26], 
                '%Y-%m-%dT%H:%M:%S.%f'
            ) if container.status == 'running' else None
        }

    def create_node(self, name, cpu_cores):
        """Create or restart existing node"""
        if name in self.existing_nodes:
            container = self.existing_nodes[name]
            if container.status != 'running':
                container.start()
            return container
        
        container = self.client.containers.run(
            "alpine:latest",
            command="tail -f /dev/null",
            detach=True,
            name=name,
            cpuset_cpus=f"0-{cpu_cores-1}" if cpu_cores > 1 else "0",
            mem_limit='256m'
        )
        self.existing_nodes[name] = container
        return container