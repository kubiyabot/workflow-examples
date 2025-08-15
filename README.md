# workflow-examples

This repository demonstrates workflow automation using Kubiya SDK. It includes components for building incident response workflows using Pydantic message blocks, messages, and models.

## Getting Started

Install dependencies via pip:
```bash
pip install kubiya-workflow-sdk[all] pydantic
```

## Example Usage

### Running an Incident Response Workflow
```python
from kubiya_workflow_sdk import KubiyaClient
from workflows import incident_response

wf = incident_response.generate_incident_response_workflow()
client = KubiyaClient(api_key="<your_api_key>", runner="<runner>")
for event in client.execute_workflow(wf.to_dict(), stream=True):
    print(event)
```

## Documentation

- [Message Blocks](docs/message-blocks.mdx)
- [Messages](docs/messages.mdx)
- [Models](docs/models.mdx)
- [Full Documentation](docs/index.mdx)

Explore the docs for details and code examples on each component.
