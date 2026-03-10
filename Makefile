SHELL := /bin/bash

.PHONY: all model model-h model-aa model-ab model-ba model-bb model-mesada model-ensamble screenshots-gui manual-h manual-aa manual-ab manuales clean-screens clean-manuales help

all: model

model: model-h model-aa model-ab model-ba model-bb model-mesada model-ensamble

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

model-ba:
	@set +e; \
	printf "exec(open('bajo_BA_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s bajo_BA.FCStd && -s bajo_BA.step && -s bajo_BA_bom.csv ]]; then \
		echo "model-ba: OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
		exit 0; \
	fi; \
	exit $$status

model-bb:
	@set +e; \
	printf "exec(open('bajo_BB_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s bajo_BB.FCStd && -s bajo_BB.step && -s bajo_BB_bom.csv ]]; then \
		echo "model-bb: OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
		exit 0; \
	fi; \
	exit $$status

model-mesada:
	@set +e; \
	printf "exec(open('mesada_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s mesada.FCStd && -s mesada.step && -s mesada_bom.csv ]]; then \
		echo "model-mesada: OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
		exit 0; \
	fi; \
	exit $$status

model-ensamble:
	@set +e; \
	printf "exec(open('cocina_ensamble_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s cocina_ensamble.FCStd && -s cocina_ensamble.step ]]; then \
		echo "model-ensamble: OK"; \
		exit 0; \
	fi; \
	exit $$status

screenshots-gui:
	@echo "Abrir FreeCAD GUI con columna_horno_micro.FCStd y ejecutar macro:"
	@echo "  /home/tin/lab/diseños_CAD/export_screenshots_gui_macro.py"
	@echo "La macro exporta: iso (vista actual), front, rear, left, right, top, bottom."

manual-h:
	python3 manuals/generate_manual.py manuals/muebles/H.toml

manual-aa:
	python3 manuals/generate_manual.py manuals/muebles/AA.toml

manual-ab:
	python3 manuals/generate_manual.py manuals/muebles/AB.toml

manuales: manual-h manual-aa manual-ab

clean-screens:
	rm -f screenshots/*.png

clean-manuales:
	rm -f manuals/out/*.md manuals/out/*.html manuals/out/*.pdf

help:
	@echo "Targets:"
	@echo "  make model            Regenera modelos H + AA + AB + BA + BB + mesada"
	@echo "  make model-h          Regenera solo mueble H"
	@echo "  make model-aa         Regenera solo alacena AA"
	@echo "  make model-ab         Regenera solo alacena AB (A2+A3)"
	@echo "  make model-ba         Regenera solo bajo mesada BA"
	@echo "  make model-bb         Regenera solo bajo mesada BB"
	@echo "  make model-mesada     Regenera piedra de mesada con calado"
	@echo "  make model-ensamble   Regenera escena conjunta de toda la cocina"
	@echo "  make screenshots-gui  Indica uso de macro GUI (iso + 6 vistas estandar)"
	@echo "  make manual-h         Genera manual H (MD + HTML + PDF si hay engine/fallback)"
	@echo "  make manual-aa        Genera manual AA (alacena izquierda)"
	@echo "  make manual-ab        Genera manual AB+AC (conjunto derecho)"
	@echo "  make manuales         Genera todos los manuales (H + AA + AB)"
	@echo "  make clean-screens    Elimina PNG generados"
	@echo "  make clean-manuales   Elimina manuales generados (MD/HTML/PDF)"
