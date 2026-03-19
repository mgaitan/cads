# Diseños CAD - Cocina

Repositorio `FCStd-first` para diseño de muebles de cocina en FreeCAD.

## Flujo actual
- Se edita el modelo directo en FreeCAD.
- La fuente de verdad es el `FCStd`.
- Cada pieza guarda metadata embebida (`bom_*`).
- El despiece para proveedor sale en `TSV`, una fila por objeto real.
- La optimización de corte lee esos `TSV`, no BOM resumidos.

## Estructura útil
- `models/fcstd/`: modelos fuente
- `src/cads/`: herramientas vigentes
- `outputs/supplier/`: TSV para proveedor
- `outputs/cutting/`: placements, summary y SVG de corte
- `screenshots/`: capturas desde FreeCAD GUI
- `docs/instrucciones/`: notas constructivas por mueble

## Herramientas vigentes
- `src/cads/export_supplier_cut_list_macro.py`
  - macro FreeCAD GUI
  - exporta una fila por pieza real
- `src/cads/export_screenshots_gui_macro.py`
  - macro FreeCAD GUI para vistas
- `src/cads/optimize_cuts.py`
  - optimiza cortes desde uno o más `TSV`
- `src/cads/freecad_gola.py`
  - helpers geométricos de gola

## Cantos del proveedor
El proveedor interpreta los 4 flags en este orden:
1. lado izquierdo del `Largo`
2. lado derecho del `Largo`
3. lado superior del `Ancho`
4. lado inferior del `Ancho`

Es decir:
- `Largo` -> `| |`
- `Ancho` -> `— —`

La macro traduce los cantos visibles del modelo a ese sistema.

## Uso
Supplier desde FreeCAD GUI:
- abrir los módulos
- ejecutar `src/cads/export_supplier_cut_list_macro.py`

Optimización de corte:
```bash
UV_CACHE_DIR=/tmp/uv-cache uv run --with ortools python -m cads.optimize_cuts \
  outputs/supplier/AA_AB_BA_BB_H_R_blanco_18mm.tsv \
  outputs/supplier/AA_AB_BA_BB_H_R_fondo_3mm.tsv \
  outputs/supplier/AA_AB_BA_BB_H_R_fondo_6mm.tsv \
  --board 2750x1830 --svg
```

## Estado actual
- `I.FCStd` es la versión vigente de la isla.
- Los flujos viejos basados en `scripts/models`, `bom/*.csv` y `STEP` quedaron retirados.
