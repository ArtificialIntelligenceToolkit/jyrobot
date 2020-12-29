# -*- coding: utf-8 -*-
# *************************************
# jyrobot: Python robot simulator
#
# Copyright (c) 2020 Calysto Developers
#
# https://github.com/Calysto/jyrobot
#
# *************************************

from .utils import gallery, image_to_png


def display(
    *objects,
    wait=True,
    clear=True,
    wheres=[],
    layout=None,
    title="Jyrobot",
    use_box=True,
    **kwargs
):
    """
    Display the objects in a notebook, jupyter lab, or regular python.
    """
    try:
        from PIL import Image
    except ImportError:
        Image = None

    try:
        from ipylab import JupyterFrontEnd, Panel
    except ImportError:
        ipylab = None

    try:
        import ipywidgets
    except ImportError:
        ipywidgets = None

    try:
        from IPython.display import clear_output
        from IPython.display import display as ipy_display
    except ImportError:

        def clear_output(wait=None):
            pass

        ipy_display = print

    layout = layout if layout is not None else {}

    if Image is not None:
        if all([isinstance(obj, Image.Image) for obj in objects]) and len(objects) > 1:
            image = gallery(*objects, **kwargs)
            png = image_to_png(image)
            objects = [ipywidgets.Image(value=png, format="png")]

    if wheres == []:
        wheres = ["inline"]  # default; can be "inline", "left", "right", or "panel"

    # Convert objects to widgets
    widgets = []
    for obj in objects:
        if Image and isinstance(obj, Image.Image):
            png = image_to_png(obj)
            widget = ipywidgets.Image(value=png, format="png")
            widgets.append(widget)
        elif isinstance(obj, str):
            widget = ipywidgets.Text(value=obj)
            widgets.append(widget)
        else:
            widgets.append(obj)

    for where in wheres:
        if where in ["panel", "left", "right"] and ipylab is not None:
            app = JupyterFrontEnd()
            panel = Panel()

            if clear:
                for w in list(app.shell.widgets.values()):
                    if (
                        hasattr(w, "title")
                        and hasattr(w.title, "label")
                        and w.title.label == title
                    ):
                        w.close()

            if where == "panel":
                if use_box:
                    defaults = {"width": "100%", "height": "auto"}
                    defaults.update(layout)
                    box = ipywidgets.Box()
                    for keyword in defaults:
                        setattr(box.layout, keyword, defaults[keyword])
                        box.children = widgets

                    panel.children = [box]
                else:
                    panel.children = widgets
                panel.title.label = title
                app.shell.add(panel, "main", {"mode": "split-right"})
            elif where == "left":
                panel.children = widgets
                panel.title.label = title
                app.shell.add(panel, "left", {"rank": 10000})
                app.shell.expand_left()
            elif where == "right":
                panel.children = widgets
                panel.title.label = title
                app.shell.add(panel, "right", {"rank": 0})
                app.shell.expand_right()
                return panel
        else:  # "inline", or something else
            if ipywidgets is None:
                clear_output(wait=wait)
                ipy_display(*widgets)  # FIXME: use objects?
            else:
                defaults = {"max_width": "600px"}
                defaults.update(layout)
                box = ipywidgets.Box()
                for keyword in defaults:
                    setattr(box.layout, keyword, defaults[keyword])
                box.children = widgets
                clear_output(wait=wait)
                ipy_display(box)
