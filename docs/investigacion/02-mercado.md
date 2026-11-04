# 02 · Productos comerciales en el mercado

> Precios observados en marketplaces el 2026-11-04. Son orientativos (distintas monedas, vendedores y fechas). Ver [fuentes.md](fuentes.md).

## Marcos IR genéricos (China: Chengying, SpecialTouch, etc.)

| Tamaño | Puntos | Precio observado | Notas |
|---|---|---|---|
| 15" | 10 | ~149 CAD | Fruugo CA, envío gratis |
| 22" | — | ~52 USD | Marketplace UK |
| 27" | 10 | ~445 € | Desertcart UK (inflado por reventa) |
| 32" | 20 | ~135 USD | Marketplace |
| 42" | — | ~99 USD + envío | Fruugo US |
| 55" | — | 269–279 CAD | Fruugo CA |
| 65" | 16 | ~337 £ | Desertcart UK |

**Lectura del mercado:**
- El hardware es **barato y maduro** (en origen, AliExpress/fábrica, suelen ser bastante más baratos que estos revendedores).
- Son **USB HID plug-and-play** en Windows; en otros SO la compatibilidad varía según el listado (algunos piden driver propietario fuera de Windows).
- **Cerrados**: firmware propietario, sin documentación, sin posibilidad de ajustar sensibilidad, gestos o filtrado; tallas fijas.
- Hay casos reportados de que el toque "se va a otra pantalla" en configuraciones multimonitor → problema de **mapeo pantalla↔digitalizador** en el SO (algo que nuestro software puede resolver).

## Barras para portátil

| Producto | Tecnología | Precio | Estado |
|---|---|---|---|
| **Neonode AirBar** | Barra IR magnética en el bisel inferior (zForce) | ~69 $ (2018) | Descatalogado en varias tiendas. 2 puntos. Win/ChromeOS bien; macOS limitado. Imanes que interfieren con algunos portátiles |
| **Neonode zForce AIR Touch Sensor Module** (kits) | Módulos ópticos 122–346 mm, I2C + USB HID | 145–220 $ por kit; kit de 7 módulos ~530–790 $ | Algunas referencias marcadas obsoletas en DigiKey |
| **CoreDAR Glamos** | Mini LiDAR, "pantalla virtual" | 119–139 $ (Kickstarter 2020) | Más gesto que tacto real; estado de envío incierto |

## Superposiciones (overlays) para monitor

| Producto | Precio | Valoración |
|---|---|---|
| Soladapt TouchGenie 21,5" | ~195 £ | "Sencillo pero caro" (Expert Reviews); nicho (Tech Advisor) |
| Christie TA551 (55", 10 puntos) | Profesional | Para señalética |

## Láminas PCAP (cristales/escaparates)

- **VisualPlanet TouchFoil**, **Pro Display Interactive PCAP Foil**: 15"–85", hasta 32 toques, funcionan a través de cristal, con guantes y en exterior.
- Precio bajo pedido (cientos o miles de €). Orientado a escaparates y gran formato.

## Paredes y proyección

- **Slamtec RPLIDAR + FrameGrabber.NET**: TUIO, emulación de ratón. Herramienta cerrada, solo Windows.
- **Ubi Interactive** (Kinect + proyector): producto comercial, histórico.

## Huecos que detectamos (oportunidad para un proyecto abierto)

1. **No existe un marco táctil open hardware moderno**, documentado y reproducible. Los proyectos DIY son de 2007–2017, abandonados o no reproducibles.
2. **Tallas fijas**: si tu monitor es 34" ultrawide o un portátil de 14", no hay producto. Un diseño **modular** resolvería esto.
3. **Firmware cerrado**: no se puede ajustar filtrado, gestos, palm rejection ni hover.
4. **macOS** no tiene soporte nativo de pantallas táctiles: los digitalizadores HID se comportan como ratón o necesitan drivers de pago (p. ej. UPDD). Oportunidad para un driver abierto.
5. **Multimonitor**: el mapeo táctil↔pantalla es incómodo; una herramienta abierta de calibración/mapeo aporta valor incluso con marcos comerciales.
