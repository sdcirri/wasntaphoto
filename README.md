# ⚠️🚧[WIP] WASNTAPhoto - A production-ready implementation of WASAPhoto in FastAPI

The original project (available [here](https://github.com/sdcirri/wasaphoto)) was developed
for the [Web And Software Architecture course](https://gamificationlab.uniroma1.it/en/wasa/)
at Sapienza. The assignment was to build a full-stack social network app in Go+Vue.js, with
little focus on security and robustness, but instead fully focused on the software architecture.

## Why FastAPI?
The original assignment mandated to implement API endpoints over a basic REST API template written in Go.
I chose FastAPI over Go because it provides:
- Dependency Injection (no clunky struct games)
- Automatic schema generation and docs (OpenAPI, ReDoc)
- Automatic validation and serialization with Pydantic v2
- The whole stack fits nicely with SQLAlchemy
- I am an experienced Python + FastAPI dev, so it's just easier 🙂

## Features
- A real database (Postgres, but it's designed to be quite DB-agnostic), the original project relied on SQLite
  - Dedicated DB role to restrict attack surface in case of compromise (no DDL nor DCL) **[TBA]**
- **Real** authentication, opaque token-based bearer auth, session management and secure credential 
  storage (argon2 hashing for passwords)
  - Hence login and registration are now distinct
- CORS and rate limiting
- UI and UX are essentially the same as in my original project, just extended to work with the new API
- Scalable and fully reproducible application deployment and configuration with docker-compose
- Cleaned up the mess in the old API design (that's on me 😅)

## Build and run
**[TBA]**

## The name
The original project was named "WASAPhoto" → "Was-A-Photo" → "Wasn't-A-Photo".
