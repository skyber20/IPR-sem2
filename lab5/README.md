# Лабораторная работа 5

Развертывание приложения из лабораторной работы 4 в Kubernetes.

Приложение: TODO Matrix на FastAPI.  
База данных: PostgreSQL.

## Что сделано

- приложение собрано в Docker image `skyber2/ipr-lab-3:latest`;
- добавлены Kubernetes-манифесты в папке `k8s/`;
- приложение запускается через `Deployment`;
- PostgreSQL запускается через `StatefulSet`;
- БД хранит данные в `PersistentVolumeClaim`;
- настройки вынесены в `ConfigMap`;
- логин и пароль БД вынесены в `Secret`;
- приложение доступно через `NodePort` на порту `30080`.

## Структура k8s

```text
k8s/
  namespace.yaml
  configmap.yaml
  secret.yaml.example
  postgres-service.yaml
  postgres-statefulset.yaml
  app-deployment.yaml
  app-service.yaml
```

`secret.yaml` создается локально и не пушится в git.

## Подготовка Secret

Создать локальный файл:

```bash
cp k8s/secret.yaml.example k8s/secret.yaml
```

В `k8s/secret.yaml` заменить пароль:

```yaml
stringData:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: lab5_postgres_password
```

Не использовать реальные личные пароли.

## Запуск в Kubernetes
Применить манифесты:

```bash
kubectl apply -f k8s/
```

## Проверка

Проверить pod-ы:

```bash
kubectl get pods -n todo-matrix
```

Ожидаемый результат:

```text
postgres-0   1/1   Running
todo-app     1/1   Running
```

Проверить сервисы:

```bash
kubectl get services -n todo-matrix
```

У `todo-app` должен быть тип `NodePort` и порт `30080`.

Проверить диск PostgreSQL:

```bash
kubectl get pvc -n todo-matrix
```

Статус должен быть `Bound`.

Проверить API:

```bash
curl http://localhost:30080/health
curl http://localhost:30080/get_tasks
```

Ожидаемый ответ health:

```json
{"status":"healthy"}
```

Открыть приложение:

```text
http://localhost:30080
```

## Логи

Логи приложения:

```bash
kubectl logs deployment/todo-app -n todo-matrix
```

Логи PostgreSQL:

```bash
kubectl logs statefulset/postgres -n todo-matrix
```

При старте приложение создает таблицы в БД. Если PostgreSQL еще не готов, приложение делает повторные попытки подключения.
