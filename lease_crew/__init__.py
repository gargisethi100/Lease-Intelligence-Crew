"""Lease Intelligence Crew — a multi-agent LangGraph system for commercial leases."""

# Route Python's SSL through the OS certificate store, so HTTPS works behind
# TLS-inspecting corporate proxies (which present a self-signed root cert).
try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

