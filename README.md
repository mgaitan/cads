# Diseños CAD - Cocina

Modelado paramétrico de muebles de cocina en FreeCAD (CLI + GUI), con:
- modelos 3D (`FCStd`, `STEP`),
- BOM de cortes,
- manuales constructivos.

## Estructura del repositorio
- `scripts/models/`: generadores FreeCAD por módulo.
- `scripts/macros/`: macros para FreeCAD GUI (screenshots).
- `models/fcstd/`: modelos nativos FreeCAD generados.
- `models/step/`: exportaciones STEP generadas.
- `bom/`: BOM CSV por módulo.
- `docs/instrucciones/`: instrucciones de armado por módulo.
- `manuals/`: configuración y salida de manuales PDF/HTML/MD.
- `screenshots/`: capturas usadas en manuales.

## BOM (nuevo)
Cada BOM incluye:
- `ml_gola`: metros lineales por ítem de gola.
- `bisagras_cazoleta`: cantidad por ítem de puerta.
- fila final `TOTAL` con acumulados del módulo.

Regla de bisagras:
- 2 cazoletas por puerta.
- 3 cazoletas si la puerta tiene lado mayor `>= 900 mm`.

## Uso rápido
```bash
make model
make model-ensamble
make manual-all
```

Targets útiles:
- `make model-h`
- `make model-aa`
- `make model-ab`
- `make model-l`
- `make model-ba`
- `make model-bb`
- `make model-m`
- `make screenshots-gui`

## Capturas GUI
Ejecutar macro:
- `scripts/macros/export_screenshots_gui_macro.py`

La macro exporta `iso`, `front`, `rear`, `left`, `right`, `top`, `bottom` en `screenshots/`.
