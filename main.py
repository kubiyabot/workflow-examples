if __name__ == '__main__':
    from kubiya_workflow_sdk import KubiyaClient
    from workflows import incident_response

    wf = incident_response.generate_incident_response_workflow()
    client = KubiyaClient(
        api_key="your-api-key",
        runner="your-runner",
    )
    for event in client.execute_workflow(wf.to_dict(), stream=True):
        print(event)