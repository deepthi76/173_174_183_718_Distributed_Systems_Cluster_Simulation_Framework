from flask import Blueprint, request, jsonify
from .cluster import Cluster
from .docker_utils import launch_node
import time


api = Blueprint('api', __name__)
cluster = Cluster()

@api.route('/register', methods=['POST'])
def register_node():
    data = request.json
    cluster.register_node(data['node_id'], data['cpu'])
    return "Node registered"

@api.route('/heartbeat', methods=['POST'])
def receive_heartbeat():
    data = request.json
    cluster.heartbeat(data['node_id'], data['pods'])
    return "Heartbeat received"

@api.route('/add_node', methods=['POST'])
def add_node():
    data = request.json
    launch_node(data['cpu'])
    return "Node launch initiated"

@api.route('/add_pod', methods=['POST'])
def add_pod():
    data = request.json
    pod_id = f"pod_{int(time.time())}"
    node_id = cluster.schedule_pod(pod_id, data['cpu'])
    return jsonify({"pod_id": pod_id, "node_id": node_id})

@api.route('/status', methods=['GET'])
def get_status():
    return jsonify(cluster.get_cluster_info())

@api.route('/heartbeats', methods=['GET'])
def get_heartbeats():
    return jsonify(cluster.heartbeat_log)
