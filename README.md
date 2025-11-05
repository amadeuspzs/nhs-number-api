# NHS Number API

> AI generated code for NHS RPySoc2025 demo - **do not use**

```mermaid
flowchart LR
	PY["Python code"] --> FLASK["Flask API"]
	FLASK --> CONTAINER["Container"]
	CONTAINER --> K8S["Kubernetes deployment"]
```

A FastAPI web wrapper around the `nhs_number` Python package, with Container and kubernetes specifications.

## Installation (local)

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage (local)

Run the application using the project entry point. The package provides a CLI entry, but you can also run the app directly with Uvicorn/uv:

```bash
uv run nhs-number-api
# or, if the `uv` CLI isn't available, use uvicorn directly:
uvicorn nhs_number_api.main:app --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000 to view the API and the automatically generated OpenAPI docs.

## Container (build & run)

This repository includes a `Containerfile` that builds a non-root, read-only-friendly image. Example commands to build and run locally:

```bash
# Build the image (from repo root)
docker build -f Containerfile -t nhs-number-api:local .

# Run the container with a read-only root filesystem and writable tmp directories
docker run --rm -p 8000:8000 \
	--read-only \
	--tmpfs /tmp:rw \
	--tmpfs /var/tmp:rw \
	nhs-number-api:local
```

## Kustomize

This repository includes a `k8s/` directory with Kubernetes manifests and a `kustomization.yaml` that applies them in the correct order (namespace first).

To deploy the app with kustomize (recommended for grouped resources):

```bash
# Make sure you've built and pushed your image (replace registry/path accordingly):
docker build -f Containerfile -t your-registry/nhs-number-api:latest .
docker push your-registry/nhs-number-api:latest

# Apply everything using kustomize which reads k8s/kustomization.yaml
kubectl apply -k k8s/
```

Notes:
- `kustomization.yaml` sets namespace: `nhsrpysoc`, so resources will be created in that namespace automatically.
- If you need to change the image tag, either update `k8s/deployment.yaml` or use `kubectl set image`:

```bash
kubectl -n nhsrpysoc set image deployment/nhs-number-api nhs-number-api=your-registry/nhs-number-api:mytag
```

- To delete the resources applied via kustomize:

```bash
kubectl delete -k k8s/
```
