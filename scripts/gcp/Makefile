GLOBAL_PYTHON_INVOCATION = python3

PYTHON_VENV_PATH     = .venv
PYTHON_VENV_ACTIVATE = source $(PYTHON_VENV_PATH)/bin/activate
#PYTHON_INVOCATION   = python
PYTHON_REQUIREMENTS  = requirements.txt

$(PYTHON_VENV_PATH):
	$(GLOBAL_PYTHON_INVOCATION) -m venv $@
	$(PYTHON_VENV_ACTIVATE) && pip install -r $(PYTHON_REQUIREMENTS)

clean:
	rm -rf $(PYTHON_VENV_PATH)

# ------------------------------------------------------------

ENTRY_POINT := transforming_redirect # The name of a function (implicitly in main.py)

dev: $(PYTHON_VENV_PATH)
	@# REF: https://cloud.google.com/run/docs/local-dev-functions
	@# We're using the PORT environment variable (see .envrc) rather than --port
	$(PYTHON_VENV_ACTIVATE) && functions-framework \
		--debug \
		--host localhost \
		--target $(ENTRY_POINT)

GCP_PROJECT            = $(shell $(GLOBAL_PYTHON_INVOCATION) -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["name"])')
GCP_DEPLOYMENT_REGION := europe-west4 # This region supports "Cloud Run Domain Mapping".
GCP_CLOUD_FN_GEN      := gen2
GCP_CLOUD_FN          := redirect # The name of the Cloud Function in the abstract. It's not an identifier in the source code.
GCP_CLOUD_FN_RUNTIME   = python$(shell $(GLOBAL_PYTHON_INVOCATION) -c 'import tomllib, re; print(re.sub(r"\D", "", tomllib.load(open("pyproject.toml", "rb"))["project"]["requires-python"]))')
GCP_CLOUD_FN_MAX_INST := 1 # Need to cap this or it would conceivably be possible for a $$$ bill to be run up.
GCP_CLOUD_FN_CPU      := 0.083
GCP_CLOUD_FN_MEMORY   := 128MiB

deploy: $(PYTHON_REQUIREMENTS)
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
	@# NOTE: The variables used in the URL need to have whitespace trimmed, because when they are defined, if they have a comment after them then their value will include the trailing space.
	open "https://console.cloud.google.com/run/detail/$(strip $(GCP_DEPLOYMENT_REGION))/$(strip $(GCP_CLOUD_FN))/observability/metrics?project=$(strip $(GCP_PROJECT))"

# ------------------------------------------------------------

.PHONY: clean \
        dev deploy console
