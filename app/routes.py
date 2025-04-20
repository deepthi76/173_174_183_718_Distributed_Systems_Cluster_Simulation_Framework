from flask import Blueprint, render_template, request, redirect, url_for
from core.node_manager import NodeManager
from core.scheduler import PodScheduler

bp = Blueprint('main', __name__)
node_manager = NodeManager()
scheduler = PodScheduler(node_manager)

@bp.route('/')
def dashboard():
    return render_template('dashboard.html', 
                         nodes=node_manager.nodes,
                         pods=node_manager.pods)

@bp.route('/add_node', methods=['POST'])
def add_node():
    cpu_cores = int(request.form.get('cpu_cores', 1))
    node_manager.add_node(cpu_cores)
    return redirect(url_for('main.dashboard'))

@bp.route('/launch_pod', methods=['POST'])
def launch_pod():
    cpu_requirements = int(request.form.get('cpu_requirements', 1))
    if scheduler.schedule_pod(cpu_requirements):
        return redirect(url_for('main.dashboard'))
    return "Failed to schedule pod - no available nodes", 400

@bp.route('/reset', methods=['POST'])
def reset_cluster():
    """Reset the entire cluster"""
    node_manager.reset_state()
    return redirect(url_for('main.dashboard'))