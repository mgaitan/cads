# AGENTS.md

## Objetivo
Este repositorio se usa para desarrollar muebles de cocina parametrizados y obtener:
- modelo 3D,
- despiece 2D/CSV,
- instrucciones de armado.

## Convenciones
- Prefijo por mueble: ejemplo `H` para columna horno/micro, `AA` para alacena A.
- Piezas etiquetadas como `H1`, `H2`, ... o `AA1`, `AA2`, ...
- Unidades en milímetros.
- Espesor por defecto: melamina `18 mm`.

## Axiomas de Diseño Vigentes
- Altura final de mesada: `900 mm`.
- Cota base de alacena derecha (AB/AC): `1500 mm`.
- Coronación superior de todos los módulos altos en `2300 mm`.
- El nivel del piso de horno debe coincidir con el borde inferior de la fila de cajones chicos.
- El tope del hueco microondas debe coincidir con el nivel superior de `AC`.
- `AA` con frentes verticales y listón fijo inferior de `90 mm`.
- `BA` con solo 2 frentes grandes inferiores de ancho completo (más fila superior chica, con 1 frente falso bajo anafe).

## Archivos clave
- `columna_horno_micro_freecad.py`: script paramétrico FreeCAD.
- `columna_horno_micro_bom.csv`: lista de piezas actual.
- `columna_horno_micro_instrucciones.md`: montaje y notas.
- `alacena_AA_freecad.py`: script paramétrico alacena A.
- `alacena_AA_bom.csv`: lista de piezas actual alacena A.
- `alacena_AA_instrucciones.md`: montaje y notas alacena A.

## Flujo recomendado
1. Actualizar parámetros en el script.
2. Regenerar `FCStd`, `STEP` y `BOM` por CLI.
3. Validar cotas y códigos de piezas.
4. Confirmar herrajes y holguras con el usuario.

## Notas
- Evitar commitear cachés temporales (`__pycache__`).
- Mantener un commit por cambio funcional (modelo, despiece o documentación).
