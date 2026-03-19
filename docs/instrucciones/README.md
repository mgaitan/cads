# Instrucciones vigentes

Las instrucciones por módulo que había en esta carpeta quedaron obsoletas.

## Flujo actual
- Se modela directo en `FCStd`.
- Cada pieza tiene metadata `bom_*`.
- El despiece útil es el `TSV` de proveedor.
- La optimización de corte se hace desde esos `TSV`.

## Cantos
El proveedor usa este orden:
1. lado izquierdo del `Largo`
2. lado derecho del `Largo`
3. lado superior del `Ancho`
4. lado inferior del `Ancho`

La macro:
- lee la metadata del modelo
- orienta la pieza para el sistema del proveedor
- exporta los 4 flags ya traducidos

## Herramientas
- `src/cads/export_supplier_cut_list_macro.py`
- `src/cads/export_screenshots_gui_macro.py`
- `src/cads/optimize_cuts.py`
