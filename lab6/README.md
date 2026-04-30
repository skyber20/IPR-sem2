# Лабораторная работа 6

Kustomize и Helm. Разделение приложения и инфраструктуры.

Приложение: TODO Matrix на FastAPI.  
База данных: PostgreSQL.

## Что сделано

- PostgreSQL вынесен в отдельный каталог `infra/postgres/`
- приложение описано отдельно в каталоге `k8s/`
- PostgreSQL запускается через `StatefulSet`
- для PostgreSQL используется `Headless Service`
- данные PostgreSQL хранятся в `PersistentVolumeClaim`
- для инфраструктуры есть Kustomize overlays `dev` и `prod`
- для инфраструктуры есть Helm chart `postgres-infra`
- для приложения есть Kustomize overlays `dev` и `prod`
- для приложения есть Helm chart `todo-matrix-app`
- в `k8s/kustomization` и `k8s/helm` нет манифестов PostgreSQL
- параметры подключения к БД передаются приложению через `ConfigMap` и `Secret`
- dev-окружение доступно через `NodePort` на порту `30080`

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

## Запуск через Kustomize

Сначала применить инфраструктуру:

```bash
kubectl apply -k infra/postgres/k8s/kustomization/overlays/dev
```

Потом применить приложение:

```bash
kubectl apply -k k8s/kustomization/overlays/dev
```

Открыть приложение:

```text
http://localhost:30080
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

## Логи

Логи приложения:

```bash
kubectl logs deployment/todo-app -n todo-matrix
```

Логи PostgreSQL:

```bash
kubectl logs statefulset/postgres -n todo-matrix
```
