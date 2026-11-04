from ast_gestos.filters import OneEuroFilter, PinchDetector
from ast_gestos.mapping import InteractionBox, PositionHistory


def test_one_euro_reduces_jitter():
    f = OneEuroFilter(min_cutoff=1.0, beta=0.0)
    out = [f(100 + (5 if i % 2 else -5), i / 30) for i in range(60)]
    assert max(out[30:]) - min(out[30:]) < 5  # entrada salta 10 px, salida mucho menos


def test_one_euro_follows_fast_motion():
    f = OneEuroFilter(min_cutoff=1.0, beta=0.01)
    x = 0.0
    for i in range(30):
        x = f(i * 50.0, i / 30)
    assert x > 29 * 50 * 0.8


def test_pinch_hysteresis():
    p = PinchDetector(0.3, 0.45, confirm_frames=1)
    assert p.update(0.6) is False
    assert p.update(0.25) is True
    assert p.update(0.40) is True   # entre umbrales: sigue pellizcando
    assert p.update(0.50) is False
    assert p.update(0.40) is False  # entre umbrales: sigue suelto


def test_box_maps_corners_and_clamps():
    box = InteractionBox(cx=0.5, cy=0.5, w=0.5, h=0.5)
    assert box.to_screen(0.25, 0.25, 1000, 500) == (0, 0)
    assert box.to_screen(0.75, 0.75, 1000, 500) == (999, 499)
    assert box.to_screen(0.0, 1.0, 1000, 500) == (0, 499)


def test_box_keeps_screen_aspect():
    box = InteractionBox.for_screen(0.45, 1280, 720, 3440, 1440)
    # en píxeles de cámara la caja debe tener la proporción de la pantalla
    assert abs((box.w * 1280) / (box.h * 720) - 3440 / 1440) < 1e-6


def test_history_lookback():
    h = PositionHistory()
    h.add(0.0, 1, 1)
    h.add(0.1, 2, 2)
    h.add(0.2, 3, 3)
    assert h.at(0.15) == (2, 2)
    assert h.at(-1) is None


def test_pinch_needs_two_frames():
    p = PinchDetector(0.4, 0.55, confirm_frames=2)
    assert p.update(0.1) is False   # 1 fotograma: aún no
    assert p.update(0.1) is True    # 2 seguidos: clic
    assert p.update(0.9) is True    # 1 fotograma abierto: aún pulsado
    assert p.update(0.2) is True    # vuelve a cerrar: se anula la racha
    assert p.update(0.9) is True
    assert p.update(0.9) is False


def test_drag_gate_click_vs_drag():
    from ast_gestos.mapping import DragGate
    g = DragGate(slop_px=100)
    g.press((500, 500))
    assert g.position(540, 530) == (500, 500)   # temblor pequeño: sigue siendo clic
    assert g.position(650, 500) == (650, 500)   # se aleja: empieza el arrastre
    assert g.position(560, 500) == (560, 500)   # ya arrastrando: sigue a la mano
    g.release()
    assert g.position(10, 10) == (10, 10)


def test_point_segment_dist():
    from ast_gestos.hand import point_segment_dist
    assert point_segment_dist((0, 1), (-1, 0), (1, 0)) == 1
    assert point_segment_dist((3, 0), (-1, 0), (1, 0)) == 2


def test_side_hand_needs_3d_confirmation():
    from ast_gestos.hand import combine_pinch, facing_weight, palm_alignment
    assert facing_weight(0.9) == 1.0 and facing_weight(0.2) == 0.0
    # palma en el plano XY (de frente) → normal en z → 1; palma en el plano YZ (de canto) → 0
    assert palm_alignment((0, 0, 0), (1, -1, 0), (-1, -1, 0)) == 1.0
    assert palm_alignment((0, 0, 0), (0, -1, 1), (0, -1, -1)) == 0.0
    # de frente: manda el 2D aunque el 3D diga abierto
    assert combine_pinch(0.1, 0.8, facing=1.0) == 0.1
    # de canto: el 2D dice cerrado pero el 3D abierto → no es pellizco
    assert combine_pinch(0.1, 0.8, facing=0.0) == 0.8
    # de canto y ambos cerrados → pellizco
    assert combine_pinch(0.1, 0.2, facing=0.0) == 0.2


def test_sticky_cursor():
    from ast_gestos.mapping import StickyCursor
    c = StickyCursor(radius_px=20)
    assert c.update(100, 100) == (100, 100)
    assert c.update(110, 105) == (100, 100)      # temblor dentro del radio: quieto
    x, y = c.update(150, 100)                     # sale: le sigue a 20 px por detrás
    assert abs(x - 130) < 1e-9 and y == 100


def test_hysteresis_gate():
    from ast_gestos.filters import HysteresisGate
    g = HysteresisGate(0.4, 0.6)
    assert g.update(0.5) is True    # empieza abierta
    assert g.update(0.3) is False   # baja de 0.4: se cierra
    assert g.update(0.5) is False   # entre umbrales: sigue cerrada
    assert g.update(0.7) is True    # supera 0.6: se abre


def test_palm_vs_back():
    from ast_gestos.hand import palm_toward_camera
    # imagen espejada, y hacia abajo, dedos hacia arriba
    wrist, idx_left, pinky_right = (0, 0), (-1, -2), (1, -2)
    assert palm_toward_camera("Right", wrist, idx_left, pinky_right) is True    # derecha, palma
    assert palm_toward_camera("Right", wrist, pinky_right, idx_left) is False   # derecha, dorso
    assert palm_toward_camera("Left", wrist, pinky_right, idx_left) is True     # izquierda, palma
    assert palm_toward_camera("Left", wrist, idx_left, pinky_right) is False    # izquierda, dorso
