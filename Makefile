SHELL := /bin/bash

MODELS_SCRIPT_DIR := scripts/models
MACRO_DIR := scripts/macros

.PHONY: all model model-h model-aa model-ab model-f model-l model-ba model-bb model-i model-m model-ensamble model-ensamble-isla screenshots-gui manual-h manual-aa manual-ab manual-all manuales optimize-cuts clean-screens clean-manuales clean-models help

all: model

model: model-h model-aa model-ab model-f model-l model-ba model-bb model-i model-m model-ensamble

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

model-f:
	$(call run_freecad_model,F_freecad.py,F,&& -s bom/F_bom.csv,model-f)

model-l:
	$(call run_freecad_model,L_freecad.py,L,&& -s bom/L_bom.csv,model-l)

model-ba:
	$(call run_freecad_model,BA_freecad.py,BA,&& -s bom/BA_bom.csv,model-ba)

model-bb:
	$(call run_freecad_model,BB_freecad.py,BB,&& -s bom/BB_bom.csv,model-bb)

model-i:
	$(call run_freecad_model,I_freecad.py,I,&& -s bom/I_bom.csv,model-i)

model-m:
	$(call run_freecad_model,M_freecad.py,M,&& -s bom/M_bom.csv,model-m)

model-ensamble:
	$(call run_freecad_model,ENS_freecad.py,ENS,,model-ensamble)

model-ensamble-isla:
	$(call run_freecad_model,ENSI_freecad.py,ENSI,,model-ensamble-isla)

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

optimize-cuts:
	uv run scripts/tools/optimize_cuts.py --svg

clean-screens:
	rm -f screenshots/*.png

clean-manuales:
	rm -f manuals/out/*.md manuals/out/*.html manuals/out/*.pdf

clean-models:
	rm -f models/fcstd/*.FCStd models/step/*.step bom/*_bom.csv

help:
	@echo "Targets:"
	@echo "  make model            Regenera modelos H + AA + AB + F + L + BA + BB + mesada + ensamble"
	@echo "  make model-h          Regenera solo mueble H"
	@echo "  make model-aa         Regenera solo alacena AA"
	@echo "  make model-ab         Regenera solo alacena AB+AC"
	@echo "  make model-f          Regenera solo mueble F (fridge + modular)"
	@echo "  make model-l          Regenera solo frente armario L"
	@echo "  make model-ba         Regenera solo bajo mesada BA"
	@echo "  make model-bb         Regenera solo bajo mesada BB"
	@echo "  make model-i          Regenera solo bajo mesada isla I"
	@echo "  make model-m          Regenera piedra de mesada con calado"
	@echo "  make model-ensamble   Regenera escena conjunta"
	@echo "  make model-ensamble-isla Regenera ensamble isla (I + F)"
	@echo "  make screenshots-gui  Indica uso de macro GUI (iso + 6 vistas estandar)"
	@echo "  make manual-all       Genera manual integral unico (ensamble + modulos + BOM total)"
	@echo "  make manuales         Genera manuales PDF/HTML/MD de H, AA y AB"
	@echo "  make optimize-cuts    Optimiza cortes de placas y genera layouts SVG (OR-Tools + uv)"
	@echo "  make clean-models     Limpia FCStd/STEP/BOM generados"
