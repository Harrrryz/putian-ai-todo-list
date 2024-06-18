from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


# TODO: all tests

def test_read_todos():
    response = client.get("/get_todos/?page=1&per_page=5")
    assert response.status_code == 200
    assert response.json()['page'] == 1
    assert response.json()['per_page'] == 5
    assert response.json()['total_items'] == 14
    assert len(response.json()['items']) == 5
    assert [item['item'] for item in response.json()['items']] == ['Code', 'Groceries', 'Clean', 'Call', 'Bills']
