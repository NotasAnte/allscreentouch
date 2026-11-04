# AllScreenTouch

Convertir **cualquier pantalla** (monitor, portátil, TV, proyección) en **táctil**, con hardware y software **100 % abiertos** que cualquiera pueda fabricar.

## Estado
🔬 Investigación terminada y primer prototipo funcionando (2026-11-04): **apuntar y hacer clic con la mano usando una webcam** (`software/gestos/`).

## Documentación
- [Investigación · 01 Tecnologías](docs/investigacion/01-tecnologias.md) — comparativa de las 8 formas de hacer una pantalla táctil
- [Investigación · 02 Mercado](docs/investigacion/02-mercado.md) — productos comerciales, precios y huecos
- [Investigación · 03 Open source existente](docs/investigacion/03-open-source-existente.md) — proyectos DIY previos y piezas reutilizables
- [Investigación · 04 Propuesta](docs/investigacion/04-propuesta.md) — qué construir y por qué
- [Investigación · 05 Táctil con webcam](docs/investigacion/05-webcam.md) — reflejo, sombra, cámara rasante y MediaPipe
- [Investigación · 06 Gestos a distancia (estilo Meta Quest)](docs/investigacion/06-gestos.md) — apuntar con la mano y pellizcar
- [Investigación · Fuentes](docs/investigacion/fuentes.md)
- [Roadmap](docs/ROADMAP.md)
- [Próximos pasos propuestos](docs/PROXIMOS-PASOS.md)
- [Prototipo: control por gestos](software/gestos/README.md)

## Idea en una línea
Un **marco IR modular** de segmentos encadenables + controlador RP2040 que se presenta como **pantalla táctil USB HID estándar** (sin drivers), con configurador web abierto.

## Licencia
[MIT](LICENSE). Úsalo, modifícalo y compártelo libremente.
