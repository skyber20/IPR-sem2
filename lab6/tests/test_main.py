def test_health(client):
    """Тест health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_tasks_empty(client):
    """Тест получения пустого списка задач"""
    response = client.get("/get_tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_add_task(client):
    """Тест добавления задачи"""
    response = client.post("/add_task", json={"text": "Тестовая задача", "quadrant": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Тестовая задача"
    assert data["quadrant"] == 1
    assert data["done"] is False
    assert "id" in data


def test_get_tasks_with_data(client):
    """Тест получения задач после добавления"""
    response = client.post("/add_task", json={"text": "Тестовая задача", "quadrant": 1})
    task = response.json()

    response = client.get("/get_tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task["id"]
    assert tasks[0]["text"] == "Тестовая задача"


def test_update_done_task(client):
    """Тест изменения статуса задачи"""
    response = client.post("/add_task", json={"text": "Тестовая задача", "quadrant": 1})
    task = response.json()
    task_id = task["id"]

    response = client.put(f"/done_task/{task_id}")
    assert response.status_code == 200

    response = client.get("/get_tasks")
    tasks = response.json()
    assert tasks[0]["done"] is True


def test_move_task(client):
    """Тест перемещения задачи"""
    response = client.post("/add_task", json={"text": "Тестовая задача", "quadrant": 1})
    assert response.status_code == 200
    task = response.json()
    task_id = task["id"]

    response = client.put(f"/move_task/{task_id}", json={"quadrant": 2})
    assert response.status_code in [200, 204]

    response = client.get("/get_tasks")
    assert response.status_code == 200
    tasks = response.json()

    moved_task = None
    for t in tasks:
        if t["id"] == task_id:
            moved_task = t
            break

    assert moved_task is not None, f"Задача с ID {task_id} не найдена"
    assert moved_task["quadrant"] == 2, f"Квадрант должен быть 2, а получили {moved_task['quadrant']}"


def test_delete_task(client):
    """Тест удаления задачи"""
    response = client.post("/add_task", json={"text": "Тестовая задача", "quadrant": 1})
    task = response.json()
    task_id = task["id"]

    response = client.delete(f"/delete_task/{task_id}")
    assert response.status_code == 200

    response = client.get("/get_tasks")
    tasks = response.json()
    assert len(tasks) == 0