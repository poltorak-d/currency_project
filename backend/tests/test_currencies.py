async def test_list_currencies_returns_200(client):
    response = await client.get("/currencies")
    assert response.status_code == 200


async def test_list_currencies_contains_expected(client):
    response = await client.get("/currencies")
    currencies = response.json()["currencies"]
    for code in ("USD", "EUR", "CHF", "GBP"):
        assert code in currencies


async def test_list_currencies_schema(client):
    response = await client.get("/currencies")
    body = response.json()
    assert "currencies" in body
    assert isinstance(body["currencies"], list)
    assert all(isinstance(c, str) and len(c) == 3 for c in body["currencies"])
