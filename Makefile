DOCSET_NAME   = ocaml-unofficial
OCAML_VERSION = 4.11

DOWNLOADS = downloads
GENERATED = generated

MANUAL_BASENAME      = ocaml-$(OCAML_VERSION)-refman-html.tar.gz
MANUAL_URL           = https://caml.inria.fr/distrib/ocaml-$(OCAML_VERSION)/$(MANUAL_BASENAME)
MANUAL_PACKED_PATH   = $(DOWNLOADS)/$(MANUAL_BASENAME)
MANUAL_UNPACKED_PATH = $(DOWNLOADS)/$(OCAML_VERSION)

TAR_NAME     = $(GENERATED)/ocaml-unofficial.tgz
ROOT         = $(GENERATED)/$(DOCSET_NAME).docset
RESOURCES    = $(ROOT)/Contents/Resources
CONTENTS     = $(RESOURCES)/Documents

VENV_PATH     = .venv
VENV_ACTIVATE = source $(VENV_PATH)/bin/activate

all: docset $(TAR_NAME)
docset: mkindex extra-files

$(CONTENTS):
	mkdir -p $@

download: $(MANUAL_PACKED_PATH)

$(MANUAL_PACKED_PATH):
	mkdir -p $(DOWNLOADS)
	curl -L -o "$@" "$(MANUAL_URL)"

extract: $(MANUAL_PACKED_PATH)
	mkdir -p $(MANUAL_UNPACKED_PATH)
	tar xf $(MANUAL_PACKED_PATH) -C $(MANUAL_UNPACKED_PATH)

copy: extract $(CONTENTS)
	mkdir -p $(CONTENTS)
	cp -a $(MANUAL_UNPACKED_PATH)/htmlman $(CONTENTS)

$(VENV_PATH):
	python3 -m venv "$@"
	$(VENV_ACTIVATE) && pip install -r requirements.txt

mkindex: copy $(VENV_PATH)
	$(VENV_ACTIVATE) && ./mkindex.py $(MANUAL_UNPACKED_PATH) $(RESOURCES)

$(TAR_NAME): docset
	tar --exclude=.DS_Store -czf $@ -C $(GENERATED) $(DOCSET_NAME).docset

extra-files:
	cp Info.plist $(ROOT)/Contents/

# ------------------------------------------------------------

clean-generated:
	rm -rf $(GENERATED)

clean: clean-generated
	@echo "Removing only generated files."
	@echo "Run 'make clean-all' to also remove downloaded files and the python virtual environment."

clean-all: clean-generated
	rm -rf $(DOWNLOADS)
	rm -rf $(VENV_PATH)

# ------------------------------------------------------------

.PHONY: all clean clean-all clean-generated copy docset download extra-files extract mkindex
