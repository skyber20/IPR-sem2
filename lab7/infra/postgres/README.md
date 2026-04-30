# PostgreSQL infrastructure

Этот каталог описывает только инфраструктуру PostgreSQL для TODO Matrix.
Манифесты приложения лежат отдельно в `k8s/` проекта.

## Контракт для приложения

Dev:

- namespace: `todo-matrix`
- host внутри namespace: `postgres-0.postgres`
- FQDN: `postgres-0.postgres.todo-matrix.svc.cluster.local`
- port: `5432`
- database: `todo_app`
- user: Secret `postgres-secret`, key `POSTGRES_USER`
- password: Secret `postgres-secret`, key `POSTGRES_PASSWORD`

Prod:

- namespace БД: `todo-matrix-infra`
- FQDN: `postgres-0.postgres.todo-matrix-infra.svc.cluster.local`
- port: `5432`
- database: `todo_app`
- user: Secret `postgres-secret`, key `POSTGRES_USER`
- password: Secret `postgres-secret`, key `POSTGRES_PASSWORD`

В репозиторий добавлены только учебные значения `change_me_*`.
Для реальной установки пароль нужно передавать через Secret, CI или `--set`.

## Kustomize

Dev:

```bash
kubectl apply -k infra/postgres/k8s/kustomization/overlays/dev
kubectl get pods,pvc -n todo-matrix -l app=postgres
```

Prod:

```bash
kubectl apply -k infra/postgres/k8s/kustomization/overlays/prod
kubectl get pods,pvc -n todo-matrix-infra -l app=postgres
```

Удаление dev:

```bash
kubectl delete -k infra/postgres/k8s/kustomization/overlays/dev
```

## Helm

Dev:

```bash
helm upgrade --install todo-db infra/postgres/k8s/helm/postgres-infra \
  --namespace todo-matrix --create-namespace \
  -f infra/postgres/k8s/helm/postgres-infra/values-dev.yaml
```

Prod:

```bash
helm upgrade --install todo-db infra/postgres/k8s/helm/postgres-infra \
  --namespace todo-matrix-infra --create-namespace \
  -f infra/postgres/k8s/helm/postgres-infra/values-prod.yaml
```

Проверка:

```bash
kubectl get pods,pvc -n todo-matrix -l app=postgres
```

Удаление dev:

```bash
helm uninstall todo-db -n todo-matrix
```
