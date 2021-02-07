OCAML_VERSION = 4.11

DOWNLOADS = downloads
GENERATED = generated

MANUAL_BASENAME      = ocaml-$(OCAML_VERSION)-refman-html.tar.gz
MANUAL_URL           = https://caml.inria.fr/distrib/ocaml-$(OCAML_VERSION)/$(MANUAL_BASENAME)
MANUAL_PACKED_PATH   = $(DOWNLOADS)/$(MANUAL_BASENAME)
MANUAL_UNPACKED_PATH = $(DOWNLOADS)/$(OCAML_VERSION)

DOCSET_BASENAME_NO_EXT = ocaml-unofficial
DOCSET_BASENAME        = $(DOCSET_BASENAME_NO_EXT).docset
DOCSET_PATH            = $(GENERATED)/$(DOCSET_BASENAME)
DOCSET_CONTENTS_PATH   = $(DOCSET_PATH)/Contents
DOCSET_RESOURCES_PATH  = $(DOCSET_CONTENTS_PATH)/Resources
DOCSET_DOCUMENTS_PATH  = $(DOCSET_RESOURCES_PATH)/Documents
# The archive is for (optional) distribution: https://kapeli.com/docsets#dashdocsetfeed
DOCSET_ARCHIVE_PATH    = $(GENERATED)/$(DOCSET_BASENAME_NO_EXT).tgz

PYTHON_VENV_PATH     = .venv
PYTHON_VENV_ACTIVATE = source $(PYTHON_VENV_PATH)/bin/activate

all: $(DOCSET_ARCHIVE_PATH)

$(DOCSET_PATH): mkindex
	cp Info.plist $(DOCSET_CONTENTS_PATH)

$(DOCSET_DOCUMENTS_PATH):
	mkdir -p $@

$(MANUAL_PACKED_PATH):
	mkdir -p $(DOWNLOADS)
	curl -L -o "$@" "$(MANUAL_URL)"

extract: $(MANUAL_PACKED_PATH)
	mkdir -p $(MANUAL_UNPACKED_PATH)
	tar xf $(MANUAL_PACKED_PATH) -C $(MANUAL_UNPACKED_PATH)

copy: extract $(DOCSET_DOCUMENTS_PATH)
	cp -a $(MANUAL_UNPACKED_PATH)/htmlman $(DOCSET_DOCUMENTS_PATH)

$(PYTHON_VENV_PATH):
	python3 -m venv "$@"
	$(PYTHON_VENV_ACTIVATE) && pip install -r requirements.txt

mkindex: copy $(PYTHON_VENV_PATH)
	$(PYTHON_VENV_ACTIVATE) && ./mkindex.py $(MANUAL_UNPACKED_PATH) $(DOCSET_RESOURCES_PATH)

$(DOCSET_ARCHIVE_PATH): $(DOCSET_PATH)
	tar --exclude=.DS_Store --strip-components 1 -czf $@ $<

# ------------------------------------------------------------

clean-generated:
	rm -rf $(GENERATED)

clean: clean-generated
	@echo "Removing only generated files."
	@echo "Run 'make clean-all' to also remove downloaded files and the python virtual environment."

clean-all: clean-generated
	rm -rf $(DOWNLOADS)
	rm -rf $(PYTHON_VENV_PATH)

# ------------------------------------------------------------

.PHONY: all clean clean-all clean-generated copy extract mkindex
