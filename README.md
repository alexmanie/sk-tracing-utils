# Semantic Kernel tracing utils

This module provides utilities for tracing and logging HTTP requests and responses when interacting with Azure OpenAI services asynchronously.

## Example usage

```python

from trace_utils import async_clients

# initialize the clients
client, logging_async_client = async_clients(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
    key=os.getenv("AZURE_OPENAI_KEY") or DefaultAzureCredential(),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# use the "client" within the 'async_client' property of the AzureChatCompletion service
agent = ChatCompletionAgent(
    service=AzureChatCompletion(
        deployment_name=deployment,
        async_client=client
    ),
    instructions=instructions,
    name=agent_name
)

# use the "logging_async_client" to get detailed information from request and response
response = await agent.get_response(messages=prompt)

# debug traces
request_headers = logging_async_client.request_headers
request_content = logging_async_client.request_content

response_headers = logging_async_client.response_headers
response_content = logging_async_client.response_content
```
