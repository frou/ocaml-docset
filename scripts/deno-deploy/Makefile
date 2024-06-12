DD_PROJECT    := ocaml-docset-redirector
DD_ENTRYPOINT := main.ts
DD_KIND_FLAG  := --prod

dev:
	deno serve $(DD_ENTRYPOINT)

deploy:
	@# REF: https://docs.deno.com/deploy/manual/deployctl#project-and-entrypoint
	@# REF: https://docs.deno.com/deploy/manual/deployctl#include-and-exclude-files
	deployctl deploy $(DD_KIND_FLAG) \
		--project $(DD_PROJECT) \
		--include '*.ts' \
		--entrypoint $(DD_ENTRYPOINT)
	@# The config file that deployctl makes sure is created is of no use to us,
	@# because the command itself (as stored above) is our source of truth for
	@# the configuration.
	@rm -f deno.json

# REF: https://docs.deno.com/deploy/manual/deployments#production-vs-preview-deployments
deploy-preview: DD_KIND_FLAG =
deploy-preview: deploy

dashboard:
	open "https://dash.deno.com/projects/$(DD_PROJECT)"

# ------------------------------------------------------------

.PHONY: dev deploy deploy-preview dashboard
