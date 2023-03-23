import traceback as tb
try:
    from window import Window
    from elements import *

    pygame.init()

    window = Window()
    (window.add_element('bg', bg)
           .add_element('orthogonal_proj_renderer', orthogonal_proj_renderer)
           .add_element('isometric_axonometry_renderer', isometric_axonometry_renderer
               .add_child('sliders', sliders))
           .add_element('scale-slider', scale_slider)
           .add_element('fg', fg)
           .add_element('key_event_handler', key_event_handler))

    try:
        window.run()
    finally:
        window.quit()
except Exception as e:
    with open('crash.txt', 'w') as f:
        f.write(tb.format_exc())
    raise e
