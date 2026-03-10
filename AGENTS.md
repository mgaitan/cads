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
- La continuidad principal de alineación frontal se toma por las líneas de gola.
- La altura de `H10` debe acompañar visualmente `BB` (frente medio + frente inferior + gola central).
- El tope del hueco microondas debe coincidir con el nivel superior de `AC`.
- `AA` con frentes verticales y listón fijo inferior de `90 mm`.
- `BA` con solo 2 frentes grandes inferiores de ancho completo (más fila superior chica, con 1 frente falso bajo anafe).
- Reparto de anchos con simetría visual:
  - Total libre sin `H`: `2258 mm`
  - `AA = BA = 903 mm` (2/5)
  - `AB/AC = BB = 1355 mm` (3/5)

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
