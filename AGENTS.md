# AGENTS.md

## Objetivo
Este repositorio se usa para desarrollar muebles de cocina parametrizados y obtener:
- modelo 3D,
- despiece 2D/CSV,
- instrucciones de armado.

## Convenciones
- Prefijo por mueble: ejemplo `H` para columna horno/micro.
- Piezas etiquetadas como `H1`, `H2`, ...
- Unidades en milímetros.
- Espesor por defecto: melamina `18 mm`.

## Archivos clave
- `columna_horno_micro_freecad.py`: script paramétrico FreeCAD.
- `columna_horno_micro_bom.csv`: lista de piezas actual.
- `columna_horno_micro_instrucciones.md`: montaje y notas.

## Flujo recomendado
1. Actualizar parámetros en el script.
2. Regenerar `FCStd`, `STEP` y `BOM` por CLI.
3. Validar cotas y códigos de piezas.
4. Confirmar herrajes y holguras con el usuario.

## Notas
- Evitar commitear cachés temporales (`__pycache__`).
- Mantener un commit por cambio funcional (modelo, despiece o documentación).
