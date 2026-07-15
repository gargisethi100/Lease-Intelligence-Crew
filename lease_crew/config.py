"""Provider-agnostic model factory.

The rest of the app never imports a vendor class directly. It calls
get_chat_model() / get_embeddings() and receives a ready LangChain object.
Which vendor comes back is decided by two .env switches (PROVIDER and
EMBEDDINGS), so swapping providers is a config change, not a code change.
"""

import os

from dotenv import load_dotenv

# Load .env into the process environment. Also switches on LangSmith
# tracing, since the LANGSMITH_* vars live there. No-op if .env is absent.
load_dotenv()


def get_chat_model(temperature: float = 0.0):
    """Build the chat model named by the PROVIDER env var."""
    provider = os.getenv("PROVIDER", "azure").lower()

    if provider == "azure":
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            # A deployment is our own named instance of a model inside the
            # Azure resource; it has no env-var default, so we must pass it.
            azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            api_version=os.getenv("OPENAI_API_VERSION", "2024-10-21"),
            temperature=temperature,
            # azure_endpoint + api_key are read from AZURE_OPENAI_ENDPOINT
            # and AZURE_OPENAI_API_KEY automatically.
        )

    if provider == "bedrock":
        from langchain_aws import ChatBedrockConverse

        return ChatBedrockConverse(
            # On-demand calls use a region-prefixed inference profile ID.
            model=os.getenv(
                "BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"
            ),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            temperature=temperature,
            # Auth: AWS_BEARER_TOKEN_BEDROCK (your Bedrock API key) read from env.
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_CHAT_MODEL", "gemini-flash-latest"),
            temperature=temperature,
            # api_key is read from GOOGLE_API_KEY automatically.
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
            temperature=temperature,
            # api_key is read from ANTHROPIC_API_KEY automatically.
        )

    raise ValueError(
        f"Unknown PROVIDER={provider!r}; "
        "expected 'azure', 'bedrock', 'gemini', or 'anthropic'."
    )


def get_embeddings():
    """Build the embeddings model named by the EMBEDDINGS env var."""
    provider = os.getenv("EMBEDDINGS", "azure").lower()

    if provider == "azure":
        from langchain_openai import AzureOpenAIEmbeddings

        return AzureOpenAIEmbeddings(
            azure_deployment=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
            api_version=os.getenv("OPENAI_API_VERSION", "2024-10-21"),
        )

    if provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001"),
            # api_key is read from GOOGLE_API_KEY automatically.
        )

    if provider == "huggingface":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=os.getenv(
                "HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
            ),
        )

    raise ValueError(
        f"Unknown EMBEDDINGS={provider!r}; expected 'azure', 'gemini', or 'huggingface'."
    )
