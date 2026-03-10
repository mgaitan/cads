SHELL := /bin/bash

MODELS_SCRIPT_DIR := scripts/models
MACRO_DIR := scripts/macros

.PHONY: all model model-h model-aa model-ab model-ba model-bb model-m model-ensamble screenshots-gui manual-h manual-aa manual-ab manual-all manuales clean-screens clean-manuales clean-models help

all: model

model: model-h model-aa model-ab model-ba model-bb model-m model-ensamble

define run_freecad_model
	@set +e; \
	printf "exec(open('$(MODELS_SCRIPT_DIR)/$(1)').read())\nimport sys\nsys.exit()\n" | freecad -c; \
	status=$$?; \
	if [[ -s models/fcstd/$(2).FCStd && -s models/step/$(2).step $(3) ]]; then \
		echo "$(4): OK (FreeCAD puede crashear al salir, pero los archivos se generaron)"; \
		exit 0; \
	fi; \
	exit $$status
endef

model-h:
	$(call run_freecad_model,H_freecad.py,H,&& -s bom/H_bom.csv,model-h)

model-aa:
	$(call run_freecad_model,AA_freecad.py,AA,&& -s bom/AA_bom.csv,model-aa)

model-ab:
	$(call run_freecad_model,AB_freecad.py,AB,&& -s bom/AB_bom.csv,model-ab)

model-ba:
	$(call run_freecad_model,BA_freecad.py,BA,&& -s bom/BA_bom.csv,model-ba)

model-bb:
	$(call run_freecad_model,BB_freecad.py,BB,&& -s bom/BB_bom.csv,model-bb)

model-m:
	$(call run_freecad_model,M_freecad.py,M,&& -s bom/M_bom.csv,model-m)

model-ensamble:
	$(call run_freecad_model,ENS_freecad.py,ENS,,model-ensamble)

screenshots-gui:
	@echo "Abrir FreeCAD GUI con el modelo deseado y ejecutar macro:"
	@echo "  /home/tin/lab/diseños_CAD/$(MACRO_DIR)/export_screenshots_gui_macro.py"
	@echo "La macro exporta: iso (vista actual), front, rear, left, right, top, bottom."

manual-h:
	python3 manuals/generate_manual.py manuals/muebles/H.toml

manual-aa:
	python3 manuals/generate_manual.py manuals/muebles/AA.toml

manual-ab:
	python3 manuals/generate_manual.py manuals/muebles/AB.toml

manual-all:
	python3 manuals/generate_master_manual.py

manuales: manual-h manual-aa manual-ab

clean-screens:
	rm -f screenshots/*.png

clean-manuales:
	rm -f manuals/out/*.md manuals/out/*.html manuals/out/*.pdf

clean-models:
	rm -f models/fcstd/*.FCStd models/step/*.step bom/*_bom.csv

help:
	@echo "Targets:"
	@echo "  make model            Regenera modelos H + AA + AB + BA + BB + mesada + ensamble"
	@echo "  make model-h          Regenera solo mueble H"
	@echo "  make model-aa         Regenera solo alacena AA"
	@echo "  make model-ab         Regenera solo alacena AB+AC"
	@echo "  make model-ba         Regenera solo bajo mesada BA"
	@echo "  make model-bb         Regenera solo bajo mesada BB"
	@echo "  make model-m          Regenera piedra de mesada con calado"
	@echo "  make model-ensamble   Regenera escena conjunta"
	@echo "  make screenshots-gui  Indica uso de macro GUI (iso + 6 vistas estandar)"
	@echo "  make manual-all       Genera manual integral unico (ensamble + modulos + BOM total)"
	@echo "  make manuales         Genera manuales PDF/HTML/MD de H, AA y AB"
	@echo "  make clean-models     Limpia FCStd/STEP/BOM generados"
