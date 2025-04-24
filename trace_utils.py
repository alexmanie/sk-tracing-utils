"""
trace_utils module.
This module provides utilities for tracing and logging HTTP requests and responses when interacting with Azure OpenAI services asynchronously.
Classes:
    LoggingTransport:
        A custom HTTP transport class derived from httpx.AsyncBaseTransport that logs request and response details including headers and content.
    LoggingAsyncClient:
        A subclass of httpx.AsyncClient that utilizes LoggingTransport to capture and expose HTTP request and response details for debugging and tracing purposes.
Functions:
    async_clients(endpoint: str, key: str, api_version: str) -> AsyncGenerator[tuple[AsyncAzureOpenAI, LoggingAsyncClient], None]:
        Initializes and returns an asynchronous Azure OpenAI client along with a logging-enabled HTTP client for tracing requests and responses.
Dependencies:
    - httpx
    - openai
Usage:
    Primarily intended for debugging, monitoring, and tracing interactions with Azure OpenAI APIs in asynchronous Python applications.
"""

import httpx
from collections.abc import AsyncGenerator
from openai import AsyncAzureOpenAI

import logging
logger = logging.getLogger(__name__)

class LoggingTransport(httpx.AsyncBaseTransport):
    def __init__(self, inner=None):
        self.inner = inner or httpx.AsyncHTTPTransport()
        self.request_headers = {}
        self.request_content = None
        self.response_headers = {}
        self.response_content = None


    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request_headers = dict(request.headers)
        self.request_content = request.content.decode("utf-8") if request.content else None

        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request Headers: {self.request_headers}")
        logger.info(f"Request Content: {self.request_content}")

        response = await self.inner.handle_async_request(request)

        raw_response_bytes = await response.aread()
        self.response_headers = dict(response.headers)
        self.response_content = raw_response_bytes.decode(response.encoding or "utf-8", errors="replace")

        logger.info(f"Response Headers: {self.response_headers}")
        logger.info(f"Response Content: {self.response_content}")

        headers_without_encoding = {k: v for k, v in response.headers.items() if k.lower() != "content-encoding"}

        return httpx.Response(
            status_code=response.status_code,
            headers=headers_without_encoding,
            content=raw_response_bytes,
            request=request,
            extensions=response.extensions,
        )

class LoggingAsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        transport = kwargs.pop("transport", None)
        self.logging_transport = LoggingTransport(transport or httpx.AsyncHTTPTransport())
        super().__init__(*args, **kwargs, transport=self.logging_transport)

    @property
    def request_headers(self):
        return self.logging_transport.request_headers

    @property
    def request_content(self):
        return self.logging_transport.request_content

    @property
    def response_headers(self):
        return self.logging_transport.response_headers

    @property
    def response_content(self):
        return self.logging_transport.response_content


def async_clients(endpoint:str, key:str, api_version:str) -> AsyncGenerator[tuple[AsyncAzureOpenAI, LoggingAsyncClient], None]:
    """
    Initializes and returns an asynchronous Azure OpenAI client along with a logging-enabled HTTP client for tracing requests and responses.

    Args:
        endpoint (str): The Azure OpenAI service endpoint URL.
        key (str): The API key for authenticating requests to the Azure OpenAI service.
        api_version (str): The version of the Azure OpenAI API to use.
    
    Returns:
        The initialized asynchronous Azure OpenAI client (AsyncAzureOpenAI) and a logging-enabled HTTP client (LoggingAsyncClient).

    """
    logging_async_client = LoggingAsyncClient()
    client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=key,
        api_version=api_version, 
        http_client=logging_async_client
    )
    return client, logging_async_client
