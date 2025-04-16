function addNode() {
    fetch('/add_node', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cpu: parseInt(document.getElementById('node_cpu').value)})
    }).then(res => res.text()).then(alert);
}

function addPod() {
    fetch('/add_pod', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cpu: parseInt(document.getElementById('pod_cpu').value)})
    }).then(res => res.json()).then(data => {
        if (data.node_id) {
            alert(`Pod ${data.pod_id} scheduled on Node ${data.node_id}`);
        } else {
            alert(`Pod ${data.pod_id} could not be scheduled: insufficient resources on all nodes`);
        }
    });
}


function refresh() {
    fetch('/status').then(res => res.json()).then(statusData => {
        fetch('/heartbeats').then(res => res.json()).then(heartbeatData => {
            const container = document.getElementById('node_cards');
            container.innerHTML = '';

            statusData.forEach(node => {
                const nodeCard = document.createElement('div');
                nodeCard.style.border = '1px solid #ccc';
                nodeCard.style.padding = '10px';
                nodeCard.style.width = '300px';
                nodeCard.style.overflow = 'hidden';
                nodeCard.style.borderRadius = '10px';
                nodeCard.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
                nodeCard.style.backgroundColor = node.active ? '#f8fff8' : '#fff0f0';

                const nodeInfo = `
                    <h3>Node ${node.id}</h3>
                    <p><strong>Total CPU:</strong> ${node.total_cpu}</p>
                    <p><strong>Available CPU:</strong> ${node.available_cpu}</p>
                    <p><strong>Active:</strong> ${node.active}</p>
                    <p><strong>Pods:</strong> ${
                        node.pods.length > 0
                            ? node.pods.map(p => typeof p === 'string' ? p : p.pod_id || JSON.stringify(p)).join(', ')
                            : 'None'
                    }</p>

                `;

                // Filter and reverse heartbeats to show latest on top
                const heartbeats = heartbeatData
                    .filter(hb => hb[0] === node.id)
                    .reverse();

                const heartbeatList = document.createElement('div');
                heartbeatList.style.maxHeight = '80px';
                heartbeatList.style.overflowY = 'auto';
                heartbeatList.style.border = '1px solid #ddd';
                heartbeatList.style.padding = '5px';
                heartbeatList.style.marginTop = '5px';
                heartbeatList.style.background = '#fafafa';

                const lastThree = heartbeats.slice(0, 3);
                heartbeatList.innerHTML = lastThree.map(hb => `🫀 ${hb[1]}`).join('<br>');

                nodeCard.innerHTML = nodeInfo + '<h4>Heartbeats</h4>';
                nodeCard.appendChild(heartbeatList);
                container.appendChild(nodeCard);
            });
        });
    });
}


setInterval(refresh, 5000);
refresh();
