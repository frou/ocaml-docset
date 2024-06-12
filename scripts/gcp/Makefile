# REF: https://github.com/astral-sh/uv?tab=readme-ov-file#getting-started
# REF: https://github.com/astral-sh/uv?tab=readme-ov-file#advanced-usage

.venv:
	uv venv $@

install: requirements.txt .venv
	uv pip sync $<

# We define dependencies in the modern way, but can derive this file from that.
requirements.txt: pyproject.toml
	uv pip compile $< -o $@

#lock: .venv
#	uv pip freeze | uv pip compile - -o requirements.txt

# ------------------------------------------------------------

ENTRY_POINT := transforming_redirect # The name of a function (implicitly in main.py)

dev:
	@# REF: https://cloud.google.com/functions/docs/running/function-frameworks
	@# We're using the PORT environment variable (see .envrc) rather than --port
	functions-framework \
		--debug \
		--host localhost \
		--target $(ENTRY_POINT)

GCP_PROJECT           := $(shell python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["name"])')
GCP_DEPLOYMENT_REGION := europe-west4# This region supports "Cloud Run Domain Mapping".
GCP_CLOUD_FN_GEN      := gen2
GCP_CLOUD_FN          := redirect# The name of the Cloud Function in the abstract. It's not an identifier in the source code.
GCP_CLOUD_FN_RUNTIME  := python$(shell python -c 'import tomllib, re; print(re.sub(r"\D", "", tomllib.load(open("pyproject.toml", "rb"))["project"]["requires-python"]))')
GCP_CLOUD_FN_MAX_INST := 1# Need to cap this or it would conceivably be possible for a $$$ bill to be run up.
GCP_CLOUD_FN_CPU      := 0.083
GCP_CLOUD_FN_MEMORY   := 128MiB
# NOTE: The reason the variable definitions above have comments squished up against values, is that otherwise the values will include the trailing space.

deploy: requirements.txt
	gcloud functions deploy $(GCP_CLOUD_FN) \
		--project $(GCP_PROJECT) \
		--region=$(GCP_DEPLOYMENT_REGION) \
		--$(GCP_CLOUD_FN_GEN) \
		--cpu=$(GCP_CLOUD_FN_CPU) \
		--memory=$(GCP_CLOUD_FN_MEMORY) \
		--max-instances=$(GCP_CLOUD_FN_MAX_INST) \
		--runtime=$(GCP_CLOUD_FN_RUNTIME) \
		--source=. --entry-point=$(ENTRY_POINT) \
		--trigger-http --allow-unauthenticated

console:
	open "https://console.cloud.google.com/functions/details/$(GCP_DEPLOYMENT_REGION)/$(GCP_CLOUD_FN)?env=$(GCP_CLOUD_FN_GEN)&project=$(GCP_PROJECT)"

# ------------------------------------------------------------

.PHONY: install lock \
        dev deploy console
