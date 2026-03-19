SHELL := /bin/bash

.PHONY: help supplier cuts clean-cutting

help:
	@echo "Targets vigentes:"
	@echo "  make supplier      Indica la macro GUI para exportar TSV desde FreeCAD"
	@echo "  make cuts          Optimiza AA+AB+BA+BB+H+R desde los TSV vigentes"
	@echo "  make clean-cutting Limpia outputs/cutting"

supplier:
	@echo "Ejecutar en FreeCAD GUI:"
	@echo "  src/cads/export_supplier_cut_list_macro.py"

cuts:
	UV_CACHE_DIR=/tmp/uv-cache uv run --with ortools python -m cads.optimize_cuts \
		outputs/supplier/AA_AB_BA_BB_H_R_blanco_18mm.tsv \
		outputs/supplier/AA_AB_BA_BB_H_R_fondo_3mm.tsv \
		outputs/supplier/AA_AB_BA_BB_H_R_fondo_6mm.tsv \
		--board 2750x1830 --max-extra-boards 20 --svg

clean-cutting:
	rm -f outputs/cutting/*.csv outputs/cutting/*.svg
