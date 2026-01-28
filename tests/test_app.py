import pytest
from dash_app import app


def test_header_present(dash_duo):
    dash_duo.start_server(app)
    header = dash_duo.find_element("h1")
    assert header is not None
    assert "Pink Morsels" in header.text


def test_visualisation_present(dash_duo):
    dash_duo.start_server(app)
    graph = dash_duo.find_element("#sales_line")
    assert graph is not None


def test_region_picker_present(dash_duo):
    dash_duo.start_server(app)
    picker = dash_duo.find_element("#region")
    assert picker is not None
