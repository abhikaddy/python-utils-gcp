from google.cloud import monitoring_v3
from google.protobuf.timestamp_pb2 import Timestamp

def close_incidents_for_alert_policy(project_id, alert_policy_id):
    client = monitoring_v3.IncidentServiceClient()
    
    project_name = f"projects/{project_id}"
    alert_policy_name = f"projects/{project_id}/alertPolicies/{alert_policy_id}"
    
    # List incidents associated with the alert policy
    incidents = client.list_incidents(
        name=project_name,
        filter=f'policy_name="{alert_policy_name}" AND state=OPEN'
    )
    
    for incident in incidents:
        # Mark incidents as resolved
        incident.end_time = Timestamp()
        client.update_incident(incident=incident)
        print(f"Incident {incident.name} has been marked as resolved.")

# Replace with your GCP project ID and alert policy ID
project_id = "your-project-id"
alert_policy_id = "your-alert-policy-id"

close_incidents_for_alert_policy(project_id, alert_policy_id)
