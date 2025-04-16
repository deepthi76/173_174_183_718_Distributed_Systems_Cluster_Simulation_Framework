import docker

client = docker.from_env()

def launch_node(cpu):
    container = client.containers.run(
        image="cluster_node",  # Name after building
        environment={"CPU": str(cpu)},
        detach=True,
        network="host"
    )
    return container.id
