from kubernetes import client, config
import requests
import pandas as pd
import time
import traceback

def k8s_client():
    # Configuration for accessing the K8s Cluster
    config.load_kube_config("~/.kube/config",persist_config=True,context="<CONTEXT>")
    return client.CoreV1Api()

k = k8s_client()

def run(**kwargs):
    namespace = kwargs.get('namespace')
    # list all the pods in the namespace
    podlist = k.list_namespaced_pod(namespace= namespace)
    data = []
    try:   
        for item in podlist.items:
            pod = k.read_namespaced_pod_status(namespace= namespace, name=item.metadata.name)
            if(pod.status.container_statuses[0].state.waiting):
                # Check if the pod statuses is in Crashloop
                if (pod.status.container_statuses[0].state.waiting.reason == "CrashLoopBackOff"):
                    data.append([pod.metadata.name,pod.status.container_statuses[0].state.waiting.reason,pod.status.container_statuses[0].last_state.terminated.message])
        df = pd.DataFrame(data=data, columns=["Pod_Name", "Pod_Status", "Reason, if any"])
        # Format to string to send slack notification
        markdown_table = df.to_markdown()
        if not data:
            print('None of the pods are in CrashLoopBackOff')
        else:
            json_data = {
                'text': "```\n" + markdown_table + "\n```",
            }
            # Send alert to #monitoring-alerts channel
            response = requests.post('<SLACK-WEBHOOK>', json=json_data)
            if response.status_code != 200:
                raise Exception(response.status_code, response.text)
            # sleep for 5 minutes after sending the notification
            time.sleep(300)
    except Exception:
        traceback.print_exc()
        print("error occured, retrying")
        run(namespace="<NAMESPACE>")

run(namespace="<NAMESPACE>")
