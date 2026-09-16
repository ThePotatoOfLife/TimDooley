import json

from scripts.house_public_surfaces import generated_public_route_roots


def test_generated_route_roots_come_from_registered_surface_ids(tmp_path):
    registry = tmp_path / 'data' / 'house'
    registry.mkdir(parents=True)
    (registry / 'public-surfaces.json').write_text(
        json.dumps(
            {
                'primary_gateway_ids': ['tim', 'religion', 'philosophy', 'science', 'world'],
                'generated_surface_ids': ['questions', 'index-a-z'],
                'surfaces': [
                    {'id': 'questions', 'canonical_route': '/questions/'},
                    {'id': 'index-a-z', 'canonical_route': '/index-a-z/'},
                    {'id': 'explore', 'canonical_route': '/explore/'},
                ],
            }
        ),
        encoding='utf-8',
    )

    assert generated_public_route_roots(tmp_path) == {'questions', 'index-a-z'}


def test_generated_route_roots_fail_closed_on_unknown_surface_id(tmp_path):
    registry = tmp_path / 'data' / 'house'
    registry.mkdir(parents=True)
    (registry / 'public-surfaces.json').write_text(
        json.dumps(
            {
                'primary_gateway_ids': ['tim', 'religion', 'philosophy', 'science', 'world'],
                'generated_surface_ids': ['missing'],
                'surfaces': [],
            }
        ),
        encoding='utf-8',
    )

    try:
        generated_public_route_roots(tmp_path)
    except ValueError as exc:
        assert 'missing registered generated surface' in str(exc)
    else:
        raise AssertionError('unknown generated surface ID must fail closed')
