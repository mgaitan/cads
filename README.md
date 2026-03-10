# Diseños CAD - Cocina

Repositorio de trabajo para modelado y despiece de muebles de cocina en FreeCAD (CLI).

## Estado actual
- Módulo implementado: columna de horno + microondas (`mueble H`).
- Modelo principal: `columna_horno_micro.FCStd`
- Intercambio CAD: `columna_horno_micro.step`
- Despiece: `columna_horno_micro_bom.csv`
- Script generador: `columna_horno_micro_freecad.py`
- Instrucciones: `columna_horno_micro_instrucciones.md`
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

## Regenerar modelo por CLI
```bash
cd /home/tin/lab/diseños_CAD
printf "exec(open('columna_horno_micro_freecad.py').read())\nimport sys\nsys.exit()\n" | freecad -c
```

## Makefile
```bash
cd /home/tin/lab/diseños_CAD
make model
make screenshots
```

`make screenshots` genera:
- `screenshots/horno_iso.png`
- `screenshots/horno_front.png`
- `screenshots/horno_left.png`
- `screenshots/horno_top.png`
