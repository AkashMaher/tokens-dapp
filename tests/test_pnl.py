
def test_get_pnl_fetch(client):
    response = client.get(
        "/api/hyperliquid/0xcd82f03d5df801a69af899a7f13263388e1f6274/pnl?start=2026-02-25&end=2026-03-05"
    )
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    
    
