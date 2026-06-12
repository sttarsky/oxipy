import pytest
import responses
from conftest import load

from oxi import OxiAPI
from oxi.exception import OxiAPIError

BASE = "https://oxi.example.com"

NODE_DATA = {
    "name": "HQ",
    "full_name": "grp/HQ",
    "model": "keenetic",
    "ip": "192.168.1.1",
    "group": "grp",
}


@responses.activate
def test_node_show_returns_view():
    responses.get(f"{BASE}/node/show/HQ.json", json=NODE_DATA)

    api = OxiAPI(url=BASE)
    node = api.node("HQ")

    assert node.ip == "192.168.1.1"
    assert node.model == "keenetic"
    assert node.full_name == "grp/HQ"
    assert node.group == "grp"


@responses.activate
def test_node_config_fetches_and_parses():
    responses.get(f"{BASE}/node/show/HQ.json", json=NODE_DATA)
    responses.get(f"{BASE}/node/fetch/grp/HQ", body=load("keenetic"))

    api = OxiAPI(url=BASE)
    config = api.node("HQ").config

    assert config.system.model == "Sprinter (KN-3710)"
    assert len(config.interfaces) > 0


@responses.activate
def test_node_not_found_maps_to_404():
    responses.get(f"{BASE}/node/show/missing.json", status=404)

    api = OxiAPI(url=BASE)
    with pytest.raises(OxiAPIError) as exc:
        api.node("missing")

    assert exc.value.status_code == 404


@responses.activate
def test_500_with_node_not_found_html_maps_to_404():
    responses.get(
        f"{BASE}/node/show/ghost.json",
        status=500,
        content_type="text/html",
        body="<html><title>Oxidized::NodeNotFound</title></html>",
    )

    api = OxiAPI(url=BASE)
    with pytest.raises(OxiAPIError) as exc:
        api.node("ghost")

    assert exc.value.status_code == 404


@responses.activate
def test_reload_returns_status_code():
    responses.get(f"{BASE}/reload", status=200)

    api = OxiAPI(url=BASE)
    assert api.reload() == 200


@responses.activate
def test_unknown_model_raises_value_error():
    data = {**NODE_DATA, "model": "unknown_vendor"}
    responses.get(f"{BASE}/node/show/HQ.json", json=data)
    responses.get(f"{BASE}/node/fetch/grp/HQ", body="whatever")

    api = OxiAPI(url=BASE)
    with pytest.raises(ValueError, match="not found in registry"):
        _ = api.node("HQ").config
