# AGENTS.md

## Objetivo
Desarrollar muebles de cocina parametrizados y producir:
- modelo 3D,
- BOM de corte,
- instrucciones de armado.

## Convenciones
- Prefijo por mueble: `H`, `AA`, `AB`, `AC`, `L`, `BA`, `BB`.
- Piezas etiquetadas como `H1`, `AA1`, etc.
- Unidades: milímetros.
- Espesor melamina por defecto: `18 mm`.
- Regla de corte: ninguna pieza de placa debe tener `largo` o `ancho` menor a `50 mm`.
  El espesor no cuenta para esta restricción.

## Estructura de trabajo
- Scripts de modelado: `scripts/models/`
- Macro de capturas: `scripts/macros/`
- Modelos generados: `models/fcstd/` y `models/step/`
- BOM generados: `bom/`
- Instrucciones: `docs/instrucciones/`
- Manuales: `manuals/`

## Axiomas de diseño vigentes
- Altura final de mesada: `900 mm`.
- Cota base de alacena derecha (AB/AC): `1500 mm`.
- Coronación superior de módulos altos: `2300 mm`.
- La continuidad visual principal se alinea por líneas de gola.
- Altura de `H10` alineada con grilla visual de `BB`.
- Tope del hueco microondas alineado con nivel superior de `AC`.
- `AA` con frentes verticales y listón fijo inferior de `90 mm`.
- `BA` con dos frentes grandes inferiores de ancho completo + frente falso superior bajo anafe.
- En bajo mesadas `BA`, `BB` e `I`, los soportes superiores de mesada van por dentro del casco y con profundidad `100 mm`.
- Reparto de anchos:
  - libre sin `H`: `2258 mm`
  - `AA = BA = 903 mm`
  - `AB/AC = BB = 1355 mm`

## BOM
Cada BOM por módulo incluye:
- `ml_gola` por pieza de gola.
- `bisagras_cazoleta` por puerta.
- fila `TOTAL` con acumulados.

Regla actual de bisagras:
- 2 por puerta.
- 3 por puerta si lado mayor `>= 900 mm`.

## Flujo recomendado
1. Ajustar parámetros en `scripts/models/*.py`.
2. Regenerar con `make model`.
3. Validar cotas y continuidad visual en `models/fcstd/ENS.FCStd` y/o `models/fcstd/ENSI.FCStd`.
4. Revisar `bom/*.csv` y manuales.
