# Fuentes del SGR

Como grupo guardamos las fuentes dentro del proyecto para que ninguna página las pida a un servidor externo: así la IP de cada funcionario no llega a terceros.

| Archivo | Familia | Peso | Origen |
| --- | --- | --- | --- |
| `roboto-latin-400-normal.woff2` | Roboto | 400 | Paquete `@fontsource/roboto` 5.1.0 |
| `roboto-latin-500-normal.woff2` | Roboto | 500 | Paquete `@fontsource/roboto` 5.1.0 |
| `roboto-latin-700-normal.woff2` | Roboto | 700 | Paquete `@fontsource/roboto` 5.1.0 |
| `roboto-slab-latin-600-normal.woff2` | Roboto Slab | 600 | Paquete `@fontsource/roboto-slab` 5.1.0 |
| `roboto-slab-latin-700-normal.woff2` | Roboto Slab | 700 | Paquete `@fontsource/roboto-slab` 5.1.0 |

- Subconjunto latino (incluye tildes, «ñ» y comillas latinas).
- Licencia: Apache 2.0, según declaran ambos paquetes. El texto completo está en `LICENCIA-Roboto-Apache-2.0.txt` y `LICENCIA-RobotoSlab-Apache-2.0.txt`. Es una licencia libre que permite redistribuir los archivos junto con su licencia.
- Se cargan con `@font-face` y `font-display: swap` desde `static/css/sgr.css`.
