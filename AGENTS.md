# AGENTS.md

## Objetivo
Desarrollar muebles de cocina en FreeCAD y producir:
- modelo 3D en `FCStd`,
- despiece unitario para proveedor en `TSV`,
- optimización de corte a partir de esos `TSV`.

## Source Of Truth
- La fuente de verdad es el modelo `FCStd`.
- Los cambios se hacen en FreeCAD, preferentemente vía MCP.
- No se regeneran muebles desde `scripts/models/*.py`; ese flujo quedó obsoleto.
- Cada pieza relevante vive como objeto individual dentro del documento.

## Convenciones
- Prefijos de módulo: `AA`, `AB`, `AC`, `BA`, `BB`, `F`, `H`, `I`, `L`, `M`, `R`, `ENS`, `ENSI`, `FULL`.
- Piezas etiquetadas como `AA1`, `BA14`, etc.
- Unidades: milímetros.
- Espesor melamina por defecto: `18 mm`.
- Ninguna pieza de placa debe tener `largo` o `ancho` menor a `50 mm`.

## Metadata En Piezas
Cada pieza del `FCStd` debe llevar metadata BOM/proveedor embebida, al menos:
- `bom_include`
- `bom_codigo`
- `bom_pieza`
- `bom_categoria`
- `bom_material`
- `bom_largo_mm`
- `bom_ancho_mm`
- `bom_espesor_mm`
- `bom_canto_izq`
- `bom_canto_der`
- `bom_canto_sup`
- `bom_canto_inf`

Reglas actuales:
- `Mesada`, `Alzada`, `Barra` y tapas laterales de piedra usan `bom_material = piedra gris mara`.
- Herrajes, previews y referencias no salen al supplier.
- El despiece para proveedor sale directo del `FCStd`, una fila por objeto real, sin agrupar.

## Cantos Para Proveedor
El sistema del proveedor interpreta las 4 columnas así:
- primeras dos columnas: lados del `Largo` (`| |`)
- últimas dos columnas: lados del `Ancho` (`— —`)

Orden de columnas en el TSV:
1. `canto_izq`
2. `canto_der`
3. `canto_sup`
4. `canto_inf`

La macro no copia la orientación geométrica “tal cual está en el mueble”; traduce la metadata de canto visible al sistema del proveedor según el `Largo/Ancho` exportado.

## Flujo Vigente
1. Editar el `FCStd` en FreeCAD vía MCP.
2. Guardar el modelo.
3. Mantener/corregir metadata por pieza.
4. Ejecutar macro de supplier:
   - `src/cads/export_supplier_cut_list_macro.py`
5. Revisar los `TSV` en `outputs/supplier/`.
6. Ejecutar optimización desde esos `TSV`:
   - `uv run python -m cads.optimize_cuts ...`

## Estructura Actual
- `models/fcstd/`: modelos fuente
- `src/cads/`: herramientas vigentes
- `outputs/supplier/`: despiece TSV
- `outputs/cutting/`: optimización de corte
- `screenshots/`: capturas desde FreeCAD GUI
- `docs/instrucciones/`: notas constructivas por mueble

## Axiomas De Diseño Vigentes
- Altura final de mesada: `900 mm`
- Cota base de alacena derecha `AB/AC`: `1500 mm`
- Coronación superior de módulos altos: `2300 mm`
- La continuidad visual principal se alinea por líneas de gola
- En `BA`, `BB` e `I`, los soportes superiores de mesada van por dentro del casco y tienen `100 mm` de profundidad
- `I.FCStd` es la variante vigente del mueble isla

## No Hacer
- No reconstruir muebles desde scripts Python viejos.
- No usar BOM resumidos como fuente para proveedor.
- No agrupar piezas distintas aunque compartan medidas.
