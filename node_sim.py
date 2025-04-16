import requests, time, os, random
import uuid

NODE_ID = str(uuid.uuid4())
API_SERVER = os.getenv("API_SERVER", "http://host.docker.internal:5000")
CPU = os.getenv("CPU", "4")

pod_ids = []

def heartbeat():
    while True:
        try:
            res = requests.post(f"{API_SERVER}/heartbeat", json={
                "node_id": NODE_ID,
                "cpu": int(CPU),
                "pods": pod_ids
            })
            print(res.text)
        except:
            print("API Server unreachable")
        time.sleep(5)

def register():
    try:
        res = requests.post(f"{API_SERVER}/register", json={"node_id": NODE_ID, "cpu": int(CPU)})
        print("Node Registered:", res.text)
    except Exception as e:
        print("Registration failed", e)

if __name__ == "__main__":
    register()
    heartbeat()
