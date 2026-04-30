# Lab 8: API Mock with Stoplight Prism

Це приклад мок-сервісу для бібліотеки на базі специфікації OpenAPI.

## Як запустити

1. Встановіть Docker.
2. Перейдіть у папку `lab8`.
3. Запустіть:

```bash
docker compose up
```

## Доступні ендпоінти

- `GET http://localhost:4010/health`
- `POST http://localhost:4010/auth/token`
- `POST http://localhost:4010/auth/refresh`
- `GET http://localhost:4010/books`
- `POST http://localhost:4010/books`
- `GET http://localhost:4010/books/{book_id}`
- `DELETE http://localhost:4010/books/{book_id}`

## Особливості mock API

- Всі відповіді мають `examples`, щоб Prism міг повертати реальні приклади.
- Для `/books` використовується `bearerAuth`.
- Docker Compose запускає Prism з command.
