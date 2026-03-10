SHELL := /bin/bash

.PHONY: all model screenshots clean-screens help

all: model screenshots

model:
	@set +e; \
	printf "exec(open('columna_horno_micro_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s columna_horno_micro.FCStd && -s columna_horno_micro.step && -s columna_horno_micro_bom.csv ]]; then \
		echo "model: OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
		exit 0; \
	fi; \
	exit $$status

screenshots:
	@mkdir -p screenshots
	@set +e; \
	printf "exec(open('export_screenshots_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s screenshots/horno_iso.png && -s screenshots/horno_front.png && -s screenshots/horno_left.png && -s screenshots/horno_top.png ]]; then \
		echo "screenshots: OK (FreeCAD puede crashear al salir, pero los PNG se generaron)"; \
		exit 0; \
	fi; \
	exit $$status

clean-screens:
	rm -f screenshots/*.png

help:
	@echo "Targets:"
	@echo "  make model         Regenera FCStd/STEP/BOM"
	@echo "  make screenshots   Exporta 4 vistas PNG (iso/front/left/top)"
	@echo "  make clean-screens Elimina PNG generados"
