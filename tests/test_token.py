
def test_get_insight(client):
    response = client.post("/api/token/bitcoin/insight")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "coingecko"
    assert "token" in data
    assert data["token"]["id"] == "bitcoin"
    assert "market_data" in data["token"]
