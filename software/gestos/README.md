# ast-gestos · apuntar y hacer clic con la mano

Prototipo de AllScreenTouch: una webcam te ve, **mueves la mano para mover el cursor** y **juntas índice y pulgar para hacer clic** (si mantienes el pellizco, arrastras).

Funciona en Linux con **Wayland y X11**: crea un ratón virtual por `uinput`, así que el sistema lo ve como un dispositivo real.

## Requisitos
- Linux con acceso de escritura a `/dev/uinput`. En Ubuntu de escritorio suele venir dado al usuario de la sesión; compruébalo con `getfacl /dev/uinput`.
- Una webcam.
- [uv](https://docs.astral.sh/uv/) (instala Python 3.12 automáticamente).

## Uso
```bash
cd software/gestos
uv run ast-gestos --dry-run     # primero: solo vista previa, sin mover el ratón
uv run ast-gestos               # control real
```
La primera vez descarga el modelo de mano de MediaPipe (~7,5 MB) en `~/.cache/allscreentouch/`.

En la ventana de vista previa:
- **Rectángulo verde** = la zona de la imagen que equivale a toda tu pantalla. Mueve la mano dentro de él.
- Punto **azul** = puntero (centro de los nudillos); **rojo** = clic pulsado.
- `p` pausa o reanuda el control · `q` / `Esc` salen.

## Ajustes útiles
| Opción | Para qué |
|---|---|
| `--box-width 0.35` | Caja más pequeña: menos movimiento de brazo, cursor más rápido |
| `--min-cutoff 0.2` | Menos temblor con la mano quieta, algo más de retardo (por defecto 0.4) |
| `--beta 0.02` | Menos retardo en movimientos rápidos (por defecto 0.01) |
| `--pinch-on 0.32 --pinch-off 0.50` | Pellizco más exigente si hace clics sin querer |
| `--deadzone 0.01` | Zona muerta mayor contra el temblor (por defecto 0.006 ≈ 20 px en 3440) |
| `--facing-min 0.3` | Permite hacer clic con la mano más girada (más riesgo de clics fantasma; por defecto 0.5) |
| `--drag-slop 0.05` | Hay que mover más la mano pellizcando para arrastrar (por defecto 0.03 = 3 % del ancho) |
| `--camera 1` | Otra webcam |
| `--screen 3440x1440` | Si no detecta bien el tamaño del escritorio |

## Cómo funciona
1. MediaPipe Hand Landmarker detecta los 21 puntos de la mano.
2. La **media de los 4 nudillos** se lleva de la caja de interacción a la pantalla (casi no se mueven al pellizcar y el promedio reduce el temblor).
3. **Filtro 1€** + **zona muerta "con cuerda"**: con la mano quieta el cursor no se mueve; al moverla, la sigue sin saltos.
4. **Pellizco** = distancia del pulgar al último tramo del índice (medida en la imagen) / tamaño de la palma, con histéresis y 2 fotogramas de confirmación.
5. **Solo clic con la palma hacia la cámara**: de canto o con el dorso hacia la cámara, el pulgar y la punta del índice quedan tapados y una sola cámara no distingue un pellizco real de uno fantasma, así que ahí el cursor se mueve pero no hace clic (la ventana lo avisa en naranja). Palma o dorso se distinguen con la mano detectada (izquierda/derecha) y el sentido de los nudillos respecto a la muñeca.
6. Al empezar el clic se usa la posición de hace 100 ms y el cursor queda **clavado** mientras pellizcas; solo si mueves la mano más de `--drag-slop` empieza a arrastrar (como en los móviles).

## Tests
```bash
uv run --group dev pytest
```
