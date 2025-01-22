DD_PROJECT    := ocaml-docset-redirector
DD_ENTRYPOINT := main.ts
DD_KIND_FLAG  := --prod

# @todo There's no point testing locally?
# @→    It's too prone to false positive. Because often something that works in
# @→    Deno-CLI doesn't work in Deno-Deploy, either because the feature/API
# @→    simply won't be supported in Deploy at all, or because development of
# @→    the Deploy runtime is lagging behind in some regard.
# @→    So just test using Preview Deployments instead.
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

logs:
	@# @todo It seems to only be the latest *production* deployment
	@# @→    If that's the case, then what's the point of the `deployctl logs --prod` flag?
	@echo "# Showing live logs of the latest deployment:"
	@echo
	@# REF: https://docs.deno.com/deploy/manual/deployctl/#logs
	deployctl logs $(DD_PROJECT)

dashboard:
	open "https://dash.deno.com/projects/$(DD_PROJECT)"

# ------------------------------------------------------------

.PHONY: dev deploy deploy-preview logs dashboard
