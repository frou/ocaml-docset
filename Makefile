OCAML_VERSION     = 4.12
OCAML_RELEASE_URL = https://ocaml.org/releases/$(OCAML_VERSION)

DOWNLOADS_PATH = downloads
GENERATED_PATH = generated
SCRIPTS_PATH   = scripts

MANUAL_BASENAME           = ocaml-$(OCAML_VERSION)-refman-html.tar.gz
MANUAL_URL                = $(OCAML_RELEASE_URL)/$(MANUAL_BASENAME)
MANUAL_PACKED_PATH        = $(DOWNLOADS_PATH)/$(MANUAL_BASENAME)
MANUAL_UNPACKED_PATH      = $(DOWNLOADS_PATH)/$(OCAML_VERSION)
MANUAL_CONTAINER_BASENAME = htmlman

DOCSET_BASENAME_NO_EXT = ocaml-unofficial
DOCSET_BASENAME        = $(DOCSET_BASENAME_NO_EXT).docset
DOCSET_PATH            = $(GENERATED_PATH)/$(DOCSET_BASENAME)
DOCSET_CONTENTS_PATH   = $(DOCSET_PATH)/Contents
DOCSET_RESOURCES_PATH  = $(DOCSET_CONTENTS_PATH)/Resources
DOCSET_INDEXDB_PATH    = $(DOCSET_RESOURCES_PATH)/docSet.dsidx
DOCSET_DOCUMENTS_PATH  = $(DOCSET_RESOURCES_PATH)/Documents
DOCSET_READABLE_NAME   = OCaml (Unofficial)
DOCSET_SEARCH_KEYWORD  = ocaml
DOCSET_MAIN_PAGE       = $(MANUAL_CONTAINER_BASENAME)/index.html
DOCSET_INFO_PATH       = $(DOCSET_CONTENTS_PATH)/Info.plist
DOCSET_ARCHIVE_PATH    = $(GENERATED_PATH)/$(DOCSET_BASENAME_NO_EXT).tgz

STASHED_INDEXDB_PATH = prev.db

PYTHON_VENV_PATH     = .venv
PYTHON_VENV_ACTIVATE = source $(PYTHON_VENV_PATH)/bin/activate

# ------------------------------------------------------------

# The archive is for (optional) distribution: https://kapeli.com/docsets#dashdocsetfeed
# @todo Use a GitHub Action to generate the docset serverside and provide an XML feed
$(DOCSET_ARCHIVE_PATH): docset
	tar --exclude=.DS_Store --strip-components 1 -czf $@ $(DOCSET_PATH)

docset: $(MANUAL_UNPACKED_PATH) $(PYTHON_VENV_PATH)
	# Copy the HTML manual into the docset
	mkdir -p $(DOCSET_DOCUMENTS_PATH)
	cp -a $(MANUAL_UNPACKED_PATH)/$(MANUAL_CONTAINER_BASENAME) $(DOCSET_DOCUMENTS_PATH)

	# Index the HTML manual, and insert anchor tags to enable page ToCs
	$(PYTHON_VENV_ACTIVATE) && $(SCRIPTS_PATH)/mkindex $(MANUAL_UNPACKED_PATH) $(DOCSET_DOCUMENTS_PATH) $(DOCSET_INDEXDB_PATH)

	# Create the Property List file that describes the docset
	$(PYTHON_VENV_ACTIVATE) && $(SCRIPTS_PATH)/mkinfo $(DOCSET_BASENAME_NO_EXT) "$(DOCSET_READABLE_NAME)" $(DOCSET_SEARCH_KEYWORD) $(DOCSET_MAIN_PAGE) $(OCAML_RELEASE_URL) $(DOCSET_INFO_PATH)

$(MANUAL_UNPACKED_PATH): $(MANUAL_PACKED_PATH)
	mkdir -p $@
	tar xf $< -C $@

$(MANUAL_PACKED_PATH):
	mkdir -p $(DOWNLOADS_PATH)
	curl -L -o $@ $(MANUAL_URL)

$(PYTHON_VENV_PATH):
	python3 -m venv $@
	$(PYTHON_VENV_ACTIVATE) && pip install -r requirements.txt

# ------------------------------------------------------------

stash-db:
	cp $(DOCSET_INDEXDB_PATH) $(STASHED_INDEXDB_PATH)

compare-dbs: $(STASHED_INDEXDB_PATH) $(DOCSET_INDEXDB_PATH)
	$(SCRIPTS_PATH)/compare_dbs $^

# ------------------------------------------------------------

clean: clean-generated
	@echo
	@echo "Only generated files were removed. Run 'make clean-all' if you also want to remove downloaded files and the Python virtual environment."

clean-generated:
	rm -rf $(GENERATED_PATH)

clean-all: clean-generated
	rm -rf $(DOWNLOADS_PATH)
	rm -rf $(PYTHON_VENV_PATH)

# ------------------------------------------------------------

.PHONY: docset stash-db compare-dbs clean clean-generated clean-all
