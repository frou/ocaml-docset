DD_PROJECT    := ocaml-docset-redirector
DD_ENTRYPOINT := main.ts
DD_KIND_FLAG  := --prod

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

logs:
	@# @todo It seems to only be the latest *production* deployment
	@# @→    Reported as https://github.com/denoland/deployctl/issues/362
	@# @→    If that's intended behaviour, then what's the purpose of the `deployctl logs --prod` flag?
	@echo "# Showing live logs of the latest deployment:"
	@echo
	@# REF: https://docs.deno.com/deploy/manual/deployctl/#logs
	deployctl logs $(DD_PROJECT)

dashboard:
	open "https://dash.deno.com/projects/$(DD_PROJECT)"

# ------------------------------------------------------------

.PHONY: deploy deploy-preview logs dashboard
