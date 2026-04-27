# Лабораторная работа 6

Kustomize и Helm. Разделение приложения и инфраструктуры.

Приложение: TODO Matrix на FastAPI.  
База данных: PostgreSQL.

## Что сделано

- PostgreSQL вынесен в отдельный каталог `infra/postgres/`;
- приложение описано отдельно в каталоге `k8s/`;
- PostgreSQL запускается через `StatefulSet`;
- для PostgreSQL используется `Headless Service`;
- данные PostgreSQL хранятся в `PersistentVolumeClaim`;
- для инфраструктуры есть Kustomize overlays `dev` и `prod`;
- для инфраструктуры есть Helm chart `postgres-infra`;
- для приложения есть Kustomize overlays `dev` и `prod`;
- для приложения есть Helm chart `todo-matrix-app`;
- в `k8s/kustomization` и `k8s/helm` нет манифестов PostgreSQL;
- параметры подключения к БД передаются приложению через `ConfigMap` и `Secret`;
- dev-окружение доступно через `NodePort` на порту `30080`.

## Структура инфраструктуры

```text
infra/postgres/
  README.md
  k8s/
    kustomization/
      base/
        service.yaml
        statefulset.yaml
      overlays/
        dev/
        prod/
    helm/
      postgres-infra/
        Chart.yaml
        values.yaml
        values-dev.yaml
        values-prod.yaml
        templates/
```

В этом каталоге лежит только PostgreSQL.

## Структура приложения

```text
k8s/
  kustomization/
    base/
      deployment.yaml
      service.yaml
    overlays/
      dev/
      prod/
  helm/
    todo-matrix-app/
      Chart.yaml
      values.yaml
      values-dev.yaml
      values-prod.yaml
      templates/
```

В этом каталоге лежит только приложение.

## Контракт с PostgreSQL

Dev:

```text
namespace: todo-matrix
host: postgres-0.postgres
port: 5432
database: todo_app
```

Prod:

```text
namespace приложения: todo-matrix-prod
namespace PostgreSQL: todo-matrix-infra
host: postgres-0.postgres.todo-matrix-infra.svc.cluster.local
port: 5432
database: todo_app
```

Логин и пароль лежат в `Secret`.
В учебных манифестах используются placeholders `change_me_dev` и `change_me_prod`.

Если поменять пароль в инфраструктуре, такой же пароль нужно поменять в настройках приложения.
Иначе приложение не подключится к PostgreSQL.

## Проверка локального приложения

Запустить тесты:

```bash
.venv/bin/python -m pytest -q
```

Ожидаемый результат:

```text
10 passed
```

## Проверка Kustomize

Проверить сборку инфраструктуры:

```bash
kubectl kustomize infra/postgres/k8s/kustomization/overlays/dev
kubectl kustomize infra/postgres/k8s/kustomization/overlays/prod
```

Проверить сборку приложения:

```bash
kubectl kustomize k8s/kustomization/overlays/dev
kubectl kustomize k8s/kustomization/overlays/prod
```

## Запуск через Kustomize

Сначала применить инфраструктуру:

```bash
kubectl apply -k infra/postgres/k8s/kustomization/overlays/dev
```

Потом применить приложение:

```bash
kubectl apply -k k8s/kustomization/overlays/dev
```

## Проверка Kustomize-запуска

Проверить pod-ы:

```bash
kubectl get pods -n todo-matrix
```

Ожидаемый результат:

```text
postgres-0   1/1   Running
todo-app     1/1   Running
```

Проверить диск PostgreSQL:

```bash
kubectl get pvc -n todo-matrix
```

Статус должен быть `Bound`.

Проверить сервисы:

```bash
kubectl get services -n todo-matrix
```

У `todo-app` должен быть тип `NodePort` и порт `30080`.

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

## Проверка Helm

Проверить шаблоны инфраструктуры:

```bash
helm template todo-db infra/postgres/k8s/helm/postgres-infra \
  -f infra/postgres/k8s/helm/postgres-infra/values-dev.yaml
```

Проверить шаблоны приложения:

```bash
helm template todo-app k8s/helm/todo-matrix-app \
  -f k8s/helm/todo-matrix-app/values-dev.yaml
```

## Запуск через Helm

Сначала установить инфраструктуру:

```bash
helm upgrade --install todo-db infra/postgres/k8s/helm/postgres-infra \
  --namespace todo-matrix --create-namespace \
  -f infra/postgres/k8s/helm/postgres-infra/values-dev.yaml
```

Потом установить приложение:

```bash
helm upgrade --install todo-app k8s/helm/todo-matrix-app \
  --namespace todo-matrix --create-namespace \
  -f k8s/helm/todo-matrix-app/values-dev.yaml
```

Проверка такая же:

```bash
kubectl get pods,pvc -n todo-matrix
curl http://localhost:30080/health
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

## Удаление ресурсов

Удалить Kustomize-запуск:

```bash
kubectl delete -k k8s/kustomization/overlays/dev
kubectl delete -k infra/postgres/k8s/kustomization/overlays/dev
```

Удалить Helm-запуск:

```bash
helm uninstall todo-app -n todo-matrix
helm uninstall todo-db -n todo-matrix
```
