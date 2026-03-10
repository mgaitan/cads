# Diseños CAD - Cocina

Repositorio de trabajo para modelado y despiece de muebles de cocina en FreeCAD (CLI).

## Estado actual
- Módulo implementado: columna de horno + microondas (`mueble H`).
- Módulo implementado: alacena superior izquierda (`mueble AA`).
- Modelo principal: `columna_horno_micro.FCStd`
- Intercambio CAD: `columna_horno_micro.step`
- Despiece: `columna_horno_micro_bom.csv`
- Script generador: `columna_horno_micro_freecad.py`
- Instrucciones: `columna_horno_micro_instrucciones.md`
- Modelo alacena: `alacena_AA.FCStd`
- Intercambio CAD: `alacena_AA.step`
- Despiece: `alacena_AA_bom.csv`
- Script generador: `alacena_AA_freecad.py`
- Instrucciones: `alacena_AA_instrucciones.md`
- Referencias visuales: carpeta `renders/`

## Parámetros base del mueble H
- Espesor melamina: `18 mm`
- Alto total: `2300 mm`
- Profundidad: `600 mm`
- Ancho interior útil: `600 mm`
- Ancho exterior: `636 mm`
- Patas: `80 mm` (ocultas con zócalo)
- Sin fondo

## Códigos de piezas
- `H1` lateral izquierdo
- `H2` lateral derecho
- `H3` piso casco
- `H4` tapa casco
- `H5` piso horno
- `H6` piso micro
- `H7` tapa micro
- `H8` estante inferior
- `H9` faja frontal central 50 mm
- `H10` puerta inferior
- `H11` puerta superior
- `H12` faja frontal inferior 50 mm
- `H13` faja frontal superior micro 50 mm
- `H14` fondo 3 mm (oculto en vistas)

### Alacena A (prefijo AA)
- `AA1` lateral izquierdo
- `AA2` lateral derecho
- `AA3` piso casco calado 160
- `AA4` tapa casco calada 160
- `AA5` divisor central
- `AA6` estante derecho
- `AA7` fondo 3 mm
- `AA8` puerta izquierda
- `AA9` puerta derecha

## Regenerar modelo por CLI
```bash
cd /home/tin/lab/diseños_CAD
printf "exec(open('columna_horno_micro_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c
```

## Makefile
```bash
cd /home/tin/lab/diseños_CAD
make model
make model-aa
make screenshots-gui
make manual-h
```

Macro GUI:
- `make screenshots-gui` muestra la ruta de macro a ejecutar.
- `export_screenshots_gui_macro.py` exporta `iso` (vista actual) y estándar:
  `front`, `rear`, `left`, `right`, `top`, `bottom`.

## Manual constructivo por mueble (PDF)
Se usa configuracion por mueble en `manuals/muebles/*.toml`.

Para el mueble H:
```bash
make manual-h
```

Salidas:
- `manuals/out/H_manual.md`
- `manuals/out/H_manual.html`
- `manuals/out/H_manual.pdf`

Contenido del manual:
- Vista isometrica + 6 vistas ortogonales
- Tabla de cortes (desde BOM CSV)
- Instrucciones de ensamblado (desde markdown)
- Terminacion del mueble (por ejemplo: melamina blanca, simil paraiso)
