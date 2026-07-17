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

Equivalencias actuales:
- `AA`: alacena izquierda
- `AB`: alacena derecha
- `AC`: complemento inferior de `AB`
- `BA`: bajo mesada izquierdo
- `BB`: bajo mesada derecho
- `F`: heladera + modular
- `H`: columna horno + micro
- `I`: bajo mesada isla
- `L`: armario lavarropas
- `M`: mesada principal
- `R`: rinconera
- `ENS`: ensamble cocina principal
- `ENSI`: ensamble isla
- `FULL`: ensamble completo

## Metadata En Piezas
Cada pieza del `FCStd` debe llevar metadata BOM/proveedor embebida, al menos:
- `bom_include`
- `bom_codigo`: codigo breve y estable, por ejemplo `A1`
- `bom_pieza`: nombre corto para el TSV, por ejemplo `PISO` o `LAT_DERECHO`
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
El TSV de importacion no lleva encabezado y tiene exactamente nueve columnas:

1. pieza: `bom_codigo` + `_` + slug de `bom_pieza`, por ejemplo `A1_PISO`
2. cantidad
3. largo en mm
4. ancho en mm
5. girar (`SI`)
6. canto izquierdo
7. canto derecho
8. canto superior
9. canto inferior

El sistema del proveedor interpreta las 4 columnas de canto así:
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
   - `src/cads/freecad/macros/export_supplier_cut_list_macro.py`
5. Revisar los `TSV` en `outputs/supplier/`. La macro genera un archivo distinto por `bom_material` y espesor.
6. Ejecutar optimización desde un `TSV` por corrida:
   - `uv run optimize-cuts ...`
7. Refrescar sitio estático si hace falta:
   - `uv run refresh-site`
8. Para documentar el modelo, ejecutar el recurso de skill
   `.agents/SKILLS/freecad-furnitures/macros/create_essential_dimensions_macro.py`;
   crea el grupo opcional `Cotas esenciales` para el total, casco o seleccion.

## Estructura Actual
- `models/`: modelos fuente `FCStd`
- `models/*.md`: notas constructivas por mueble
- `src/cads/`: herramientas vigentes
- `outputs/supplier/`: despiece TSV
- `outputs/cutting/`: optimización de corte
- `outputs/screenshots/`: capturas desde FreeCAD GUI
- `outputs/manuals/`: manual final en PDF
- `outputs/site/`: sitio estático publicado en GitHub Pages

## Axiomas De Diseño Vigentes
- Altura final de mesada: `900 mm`
- Cota base de alacena derecha `AB/AC`: `1500 mm`
- Coronación superior de módulos altos: `2300 mm`
- La continuidad visual principal se alinea por líneas de gola
- En `BA`, `BB` e `I`, los soportes superiores de mesada van por dentro del casco y tienen `100 mm` de profundidad

## No Hacer
- No reconstruir muebles desde scripts Python viejos.
- No usar BOM resumidos como fuente para proveedor.
- No agrupar piezas distintas aunque compartan medidas.
