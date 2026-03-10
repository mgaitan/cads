SHELL := /bin/bash

.PHONY: all model screenshots-gui manual-h manuales clean-screens clean-manuales help

all: model

model:
	@set +e; \
	printf "exec(open('columna_horno_micro_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s columna_horno_micro.FCStd && -s columna_horno_micro.step && -s columna_horno_micro_bom.csv ]]; then \
		echo "model: OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
		exit 0; \
	fi; \
	exit $$status

screenshots-gui:
	@echo "Abrir FreeCAD GUI con columna_horno_micro.FCStd y ejecutar macro:"
	@echo "  /home/tin/lab/diseños_CAD/export_screenshots_gui_macro.py"
	@echo "La macro exporta: iso (vista actual), front, rear, left, right, top, bottom."

manual-h:
	python3 manuals/generate_manual.py manuals/muebles/H.toml

manuales: manual-h

clean-screens:
	rm -f screenshots/*.png

clean-manuales:
	rm -f manuals/out/*.md manuals/out/*.html manuals/out/*.pdf

help:
	@echo "Targets:"
	@echo "  make model            Regenera FCStd/STEP/BOM"
	@echo "  make screenshots-gui  Indica uso de macro GUI (iso + 6 vistas estandar)"
	@echo "  make manual-h         Genera manual H (MD + HTML + PDF si hay engine/fallback)"
	@echo "  make manuales         Genera todos los manuales (por ahora H)"
	@echo "  make clean-screens    Elimina PNG generados"
	@echo "  make clean-manuales   Elimina manuales generados (MD/HTML/PDF)"
