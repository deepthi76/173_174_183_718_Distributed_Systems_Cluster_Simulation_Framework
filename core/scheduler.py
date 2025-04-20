class PodScheduler:
    def __init__(self, node_manager):
        self.node_manager = node_manager

    def schedule_pod(self, cpu_requirements, algorithm='first_fit'):
        """Schedule pod using selected algorithm"""
        if algorithm == 'first_fit':
            return self._first_fit(cpu_requirements)
        return False

    def _first_fit(self, cpu_requirements):
        """First-fit scheduling algorithm"""
        return self.node_manager.add_pod(cpu_requirements)