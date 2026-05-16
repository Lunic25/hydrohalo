def test_gui_module_imports():
    import app.gui.app as app_mod
    assert app_mod is not None
