DD_PROJECT    := ocaml-docset-redirector
DD_ENTRYPOINT := main.ts
DD_KIND_FLAG  := --prod

dev:
	deno serve $(DD_ENTRYPOINT)

deploy:
	# REF: https://docs.deno.com/deploy/manual/deployctl#project-and-entrypoint
	# REF: https://docs.deno.com/deploy/manual/deployctl#include-and-exclude-files
	deployctl deploy $(DD_KIND_FLAG) \
		--project $(DD_PROJECT) \
		--include '*.ts' \
		--entrypoint $(DD_ENTRYPOINT) \
		--save-config

# REF: https://docs.deno.com/deploy/manual/deployments#production-vs-preview-deployments
deploy-preview: DD_KIND_FLAG =
deploy-preview: deploy

dashboard:
	open "https://dash.deno.com/projects/$(DD_PROJECT)"

# ------------------------------------------------------------

.PHONY: dev deploy deploy-preview dashboard
