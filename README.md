# Diseños CAD - Cocina

Repositorio de mis diseños de muebles en FreeCAD.

## Flujo actual
- Se edita el modelo directo en FreeCAD, idealmente via MCP.
- La fuente de verdad es el `FCStd`.
- Cada pieza guarda metadata embebida (`bom_*`).
- El despiece para proveedor sale en `TSV`, una fila por objeto real.
- La optimización de corte lee esos `TSV`, no BOM resumidos.

## FreeCAD MCP
Se usa [`freecad-mcp`](https://github.com/neka-nat/freecad-mcp) para editar los modelos desde una sesion de FreeCAD abierta.

La mejor manera de saber donde hay que copiar el addon es preguntarselo a FreeCAD desde su consola Python:

```python
import FreeCAD as App
print(App.getUserAppDataDir())
```

En este caso, usando AppImage `rc3`, el directorio fue:

```text
~/.local/share/FreeCAD/v1-1/
```

Configuracion MCP usada:

```json
{
  "freecad-mcp": {
    "command": "uvx",
    "args": ["-p", "3.12", "freecad-mcp", "--only-text-feedback"],
    "env": {}
  }
}
```

## Estructura útil
- `models/`: modelos fuente
- `models/*.md`: notas constructivas por mueble
- `src/cads/`: herramientas vigentes
- `outputs/supplier/`: TSV para proveedor, un archivo por material y espesor
- `outputs/cutting/`: placements, summary y SVG de corte
- `outputs/screenshots/`: capturas desde FreeCAD GUI
- `outputs/manuals/COCINA.pdf`: manual final

## Modulos
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
- `vanitory_flotante_800`: vanitory flotante anterior de 800 mm
- `vanitory_reforma_770`: vanitory reforma de 770 mm
- `vanitory_reforma_830`: vanitory reforma de 830 mm

## Herramientas vigentes
- `src/cads/freecad/macros/export_supplier_cut_list_macro.py`
  - macro FreeCAD GUI
  - exporta una fila por pieza real
- `src/cads/freecad/macros/export_screenshots_gui_macro.py`
  - macro FreeCAD GUI para vistas
- `src/cads/freecad/macros/create_essential_dimensions_macro.py`
  - agrega ancho, profundidad y altura total al grupo `Cotas esenciales`
- `src/cads/cli/optimize_cuts.py`
  - optimiza cortes desde un solo `TSV` por corrida
- `src/cads/cli/refresh_site.py`
  - sincroniza `manual`, `screenshots`, `STL` y `cutting` dentro de `outputs/site/`
- `src/cads/freecad/freecad_gola.py`
  - helpers geométricos de gola
- `tools/build_vanitory_reforma_770.py` y `tools/build_vanitory_reforma_830.py`
  - scripts auxiliares de los vanitories; los `FCStd` siguen siendo la fuente de verdad

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

Cada TSV se importa sin encabezado y tiene este orden fijo:

```text
pieza  cantidad  largo_mm  ancho_mm  girar  canto_izq  canto_der  canto_sup  canto_inf
```

La pieza se forma como `bom_codigo` + `_` + el slug de `bom_pieza`; por ejemplo,
`A1_PISO` o `A2_LAT_DERECHO`.

## Uso
Supplier desde FreeCAD GUI:
- abrir los módulos
- ejecutar `src/cads/freecad/macros/export_supplier_cut_list_macro.py`

Cotas maestras en FreeCAD GUI:
1. abrir el `FCStd` y seleccionar el documento en el arbol
2. abrir `Macro > Macros... > Ejecutar macro desde archivo`
3. elegir `src/cads/freecad/macros/create_essential_dimensions_macro.py`
4. en el arbol, seleccionar `Cotas esenciales` y presionar `Espacio` para mostrarlas u ocultarlas

La macro crea solo ancho, profundidad y altura total. Se ven tambien en vista
perspectiva y se reemplazan al volver a ejecutar la macro despues de modificar
el mueble.

Optimización de corte:
```bash
uv run optimize-cuts \
  outputs/supplier/AA_AB_BA_BB_H_R_blanco_18mm.tsv \
  --board 2750x1830 --svg
```

Cada espesor o material se corre por separado, con el tamaño de placa que corresponda:

```bash
uv run optimize-cuts outputs/supplier/AA_AB_BA_BB_H_R_blanco_18mm.tsv --board 2750x1830 --svg
uv run optimize-cuts outputs/supplier/AA_AB_BA_BB_H_R_fondo_3mm.tsv --board 2440x1830 --svg
uv run optimize-cuts outputs/supplier/AA_AB_BA_BB_H_R_fondo_6mm.tsv --board 2440x1830 --svg
```

Actualización del sitio:
```bash
uv run refresh-site
```

Ese comando:
- copia el manual desde `outputs/manuals/`
- copia los STL desde `outputs/web_models/`
- copia los cortes desde `outputs/cutting/`
- aplana las capturas desde `outputs/screenshots/<MODULO>/` a `outputs/site/assets/screenshots/`

GitHub Pages publica `outputs/site/` al hacer `push` a `master`.

## Estado actual
- `I.FCStd` es la versión vigente de la isla.
- Los flujos viejos basados en `scripts/models`, `bom/*.csv` y `STEP` quedaron retirados.
