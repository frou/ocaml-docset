TARGET = target
DOCSET_NAME = ocaml-unofficial
ORIGINAL_DOC_URL = https://caml.inria.fr/distrib/ocaml-4.10/ocaml-4.10-refman-html.tar.gz

ORIGINAL_DOC = files/ocaml-4.10-refman-html.tar.gz
TAR_NAME = $(TARGET)/ocaml-unofficial.tgz
ROOT = $(TARGET)/$(DOCSET_NAME).docset
RESOURCES = $(ROOT)/Contents/Resources
CONTENTS = $(RESOURCES)/Documents

VENV_PATH = .venv
VENV_ACTIVATE = source $(VENV_PATH)/bin/activate

all: docset $(TAR_NAME)
docset: mkindex extra-files

$(CONTENTS):
	mkdir -p $@

download: $(ORIGINAL_DOC)

$(ORIGINAL_DOC):
	mkdir -p files
	curl -L -o "$@" "$(ORIGINAL_DOC_URL)"

extract: $(ORIGINAL_DOC)
	mkdir -p $(TARGET)/source
	tar xf $(ORIGINAL_DOC) -C $(TARGET)/source

copy: extract $(CONTENTS)
	mkdir -p $(CONTENTS)
	cp -a $(TARGET)/source/htmlman $(CONTENTS)

$(VENV_PATH):
	python3 -m venv "$@"
	$(VENV_ACTIVATE) && pip install -r requirements.txt

mkindex: copy $(VENV_PATH)
	$(VENV_ACTIVATE) && ./mkindex.py $(TARGET)/source $(RESOURCES)

$(TAR_NAME): docset
	tar --exclude=.DS_Store -czf $@ -C $(TARGET) $(DOCSET_NAME).docset

extra-files:
	cp Info.plist $(ROOT)/Contents/

clean-target:
	rm -rf $(TARGET)

clean: clean-target
	@echo "Removing only generated files"
	@echo "Run 'make clean-all' to remove downloaded files and python virtual environment as well."

clean-all: clean-target
	rm -rf files
	rm -rf $(VENV_PATH)

.PHONY: all clean clean-all clean-target copy docset download extra-files extract mkindex
