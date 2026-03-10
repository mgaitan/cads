SHELL := /bin/bash

.PHONY: all model model-h model-aa model-ab screenshots-gui manual-h manuales clean-screens clean-manuales help

all: model

model: model-h model-aa model-ab

model-h:
	@set +e; \
	printf "exec(open('columna_horno_micro_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s columna_horno_micro.FCStd && -s columna_horno_micro.step && -s columna_horno_micro_bom.csv ]]; then \
		echo "model: OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
		exit 0; \
	fi; \
	exit $$status

model-aa:
	@set +e; \
	printf "exec(open('alacena_AA_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s alacena_AA.FCStd && -s alacena_AA.step && -s alacena_AA_bom.csv ]]; then \
		echo "model-aa: OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
		exit 0; \
	fi; \
	exit $$status

model-ab:
	@set +e; \
	printf "exec(open('alacena_AB_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s alacena_AB.FCStd && -s alacena_AB.step && -s alacena_AB_bom.csv ]]; then \
		echo "model-ab: OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
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
	@echo "  make model            Regenera modelos H + AA + AB (FCStd/STEP/BOM)"
	@echo "  make model-h          Regenera solo mueble H"
	@echo "  make model-aa         Regenera solo alacena AA"
	@echo "  make model-ab         Regenera solo alacena AB (A2+A3)"
	@echo "  make screenshots-gui  Indica uso de macro GUI (iso + 6 vistas estandar)"
	@echo "  make manual-h         Genera manual H (MD + HTML + PDF si hay engine/fallback)"
	@echo "  make manuales         Genera todos los manuales (por ahora H)"
	@echo "  make clean-screens    Elimina PNG generados"
	@echo "  make clean-manuales   Elimina manuales generados (MD/HTML/PDF)"
