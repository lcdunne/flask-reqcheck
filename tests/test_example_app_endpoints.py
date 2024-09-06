import pytest


@pytest.mark.parametrize(
    "a, b, c, d, expected_status_code",
    [
        ("hello", "2", "3", "1bf221b1-6b8e-439c-9dbb-cc281bc6757d", 200),
        ("1", "2", "3", "5e7f6324-5027-4311-a971-b40eb58aa4a6", 200),
        # TODO: These should be 400 bad requests, not 500
        ("hello", "invalid literal", "3", "1bf221b1-6b8e-439c-9dbb-cc281bc6757d", 500),
        ("hello", False, "3", "1bf221b1-6b8e-439c-9dbb-cc281bc6757d", 500),
        ("hello", "2", "3", "not-a-uuid", 500),
    ],
)
def test_validated_from_route_function_fully_typed(
    client, a, b, c, d, expected_status_code
):
    r = client.get(f"/path/typed/{a}/{b}/{c}/{d}")
    assert r.status_code == expected_status_code


def test_validated_from_route_function_fully_typed_return(client):
    a = "hello"
    b = "2"
    c = "3"
    d = "1bf221b1-6b8e-439c-9dbb-cc281bc6757d"

    r = client.get(f"/path/typed/{a}/{b}/{c}/{d}")
    assert r.status_code == 200

    path_params = r.json["path_params"]
    assert path_params == {"a": a, "b": int(b), "c": int(c), "d": d}


def test_validated_from_route_function_partially_typed(client):
    a = "hello"
    b = "2"
    c = "3"
    d = "68"

    r = client.get(f"/path/partially_typed/{a}/{b}/{c}/{d}")
    assert r.status_code == 200

    path_params = r.json["path_params"]
    # b & c become ints but d remains a string
    assert path_params == {"a": a, "b": int(b), "c": int(c), "d": d}


def test_validated_from_route_function_untyped(client):
    a = "hello"
    b = "2"
    c = "3"
    d = "68"

    r = client.get(f"/path/untyped/{a}/{b}/{c}/{d}")
    assert r.status_code == 200

    path_params = r.json["path_params"]
    # no typing exists so all remain strings
    assert path_params == {"a": a, "b": b, "c": c, "d": d}


@pytest.mark.parametrize(
    "q, expected_status_code",
    [
        (
            {
                "a": "hello",
                "arr": ["2", "3", "4"],
                "b": "21",
                "c": "3.141",
                "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
            },
            200,
        ),
        (
            {
                "a": "hello",
                "arr": ["b", "a", "d"],
                "b": "21",
                "c": "3.141",
                "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
            },
            500,
        ),
        (
            {
                "a": "hello",
                "arr": ["1", "2", "3"],
                "b": "21",
                "c": "3.141",
                "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
            },
            200,
        ),
        (
            {
                "a": "hello",
                "arr": ["1", "2", "3"],
                "b": "21",
                "c": "3.141",
                "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
                "unexpected": "parameter",
            },
            200,
        ),
        (
            {},
            200,
        ),
    ],
)
def test_query_parameters_validated(client, q, expected_status_code):
    r = client.get("/query", query_string=q)
    assert r.status_code == expected_status_code


@pytest.mark.parametrize(
    "q, expected_status_code",
    [
        (
            {
                "a": "hello",
                "arr": ["2", "3", "4"],
                "b": "21",
                "c": "3.141",
                "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
                "x": "important",
            },
            200,
        ),
        (
            {
                "a": "hello",
                "arr": ["b", "a", "d"],
                "b": "21",
                "c": "3.141",
                "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
                "x": "important",
            },
            500,
        ),
        (
            {
                "a": "hello",
                "arr": ["1", "2", "3"],
                "b": "21",
                "c": "3.141",
                "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
            },
            500,
        ),
        (
            {
                "x": "important",
            },
            200,
        ),
    ],
)
def test_query_parameters_required_validated(client, q, expected_status_code):
    r = client.get("/query_required", query_string=q)
    assert r.status_code == expected_status_code


def test_query_parameters_return_validated(client):
    q = {
        "a": "hello",
        "arr": ["2", "3", "4"],
        "b": "21",
        "c": "3.141",
        "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
    }

    r = client.get("/query", query_string=q)
    assert r.status_code == 200

    query_params = r.json["query_params"]
    # Types should get validated

    assert query_params == {
        "a": "hello",
        "arr": [2, 3, 4],
        "b": 21,
        "c": 3.141,
        "d": "1bf221b1-6b8e-439c-9dbb-cc281bc6757d",
    }


@pytest.mark.parametrize(
    "body, expected_status_code",
    [
        (
            {
                "a": "Hello",
                "b": 42,
                "c": 3.141,
                "d": "06b57c96-e066-4c20-862a-180754ab24f5",
                "arr": [1, 2, 3, 4, 5],
            },
            200,
        ),
        (
            {
                "a": "Hello",
                "b": 42.98765,
                "c": 3.141,
                "d": "06b57c96-e066-4c20-862a-180754ab24f5",
                "arr": [1, 2, 3, 4, 5],
            },
            500,
        ),
        (
            {
                "a": "Hello",
                "b": 42,
                "c": 3.141,
                "d": "not-a-uuid",
                "arr": [1, 2, 3, 4, 5],
            },
            500,
        ),
        (
            {
                "a": "Hello",
                "b": 42,
                "c": 3.141,
                "d": "not-a-uuid",
                "arr": [1, 2, 3, 4, 5],
                "unexpected": "This field is not included in the model",
            },
            500,
        ),
        (
            {
                "a": "Lots of missing stuff",
                "arr": [1, 2, 3, 4, 5],
            },
            500,
        ),
        ({}, 500),
    ],
)
def test_posted_json_body_validated(client, body, expected_status_code):
    r = client.post("/body", json=body)
    print(r.text)
    assert r.status_code == expected_status_code


def test_posted_json_body_validated_return(client):
    body = {
        "a": "Hello",
        "b": 42,
        "c": 3.141,
        "d": "06b57c96-e066-4c20-862a-180754ab24f5",
        "arr": [1, 2, 3, 4, 5],
    }

    r = client.post("/body", json=body)
    assert r.status_code == 200

    body_data = r.json["body"]
    assert body_data == body


@pytest.mark.parametrize(
    "form, expected_status_code",
    [
        ({"a": "Hello", "b": 21}, 200),
        ({"a": "Hello", "b": 21, "unexpected": "Succeeds (set in model def)"}, 200),
        ({"a": "Something is missing..."}, 500),
    ],
)
def test_posted_form_validated(client, form, expected_status_code):
    r = client.post("/form", data=form)
    assert r.status_code == expected_status_code


def test_not_a_form(client):
    r = client.post("/form", json={"a": "Hello", "b": 21})
    assert r.status_code == 415


def test_posted_form_validated_return(client):
    form = {"a": "Hello", "b": 21}

    r = client.post("/form", data=form)
    assert r.status_code == 200

    body_data = r.json["form"]
    assert body_data == form
