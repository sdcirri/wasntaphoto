[![Tests](https://github.com/sdcirri/wasntaphoto/actions/workflows/backend_tests.yml/badge.svg)](https://github.com/sdcirri/wasntaphoto/actions/workflows/backend_tests.yml)
[![Coverage](https://codecov.io/gh/sdcirri/wasntaphoto/graph/badge.svg)](https://codecov.io/gh/sdcirri/wasntaphoto)
[![Backend Build](https://github.com/sdcirri/wasntaphoto/actions/workflows/ci_backend.yml/badge.svg)](https://github.com/sdcirri/wasntaphoto/actions/workflows/ci_backend.yml)
[![Frontend Build](https://github.com/sdcirri/wasntaphoto/actions/workflows/ci_frontend.yml/badge.svg)](https://github.com/sdcirri/wasntaphoto/actions/workflows/ci_frontend.yml)
[![Semgrep](https://github.com/sdcirri/wasntaphoto/actions/workflows/semgrep.yml/badge.svg)](https://github.com/sdcirri/wasntaphoto/actions/workflows/semgrep.yml)

# WASNTAPhoto - A production-ready implementation of WASAPhoto in FastAPI

![wasa-screenshot](https://github.com/user-attachments/assets/f2860f88-6ccc-47b3-bc59-328d06eb585c)
Keep in touch with your friends by sharing photos of special moments, thanks to WASAPhoto! You can
upload your photos directly from your PC, and they will be visible to everyone following you.

The original project (available [here](https://github.com/sdcirri/wasaphoto)) was developed
for the [Web And Software Architecture course](https://gamificationlab.uniroma1.it/en/wasa/)
at Sapienza. The assignment was to build a full-stack social network app in Go+Vue.js, with
little focus on security and robustness, but instead fully focused on the software architecture.

## Stack
### Docs
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)

### Backend
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![Pydantic](https://img.shields.io/badge/pydantic-%23E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23D71F00.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)

### Frontend
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)

### Data and infrastructure
![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

### Security and testing
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![Codecov](https://img.shields.io/badge/codecov-%23ff0077.svg?style=for-the-badge&logo=codecov&logoColor=white)
![Semgrep](https://img.shields.io/badge/semgrep-%2300C7B7.svg?style=for-the-badge&logoColor=white)

## Why FastAPI?
The original assignment mandated to implement API endpoints over a basic REST API template written in Go.
I chose FastAPI over Go because it provides:
- Dependency Injection (no clunky struct games)
- Automatic schema generation and docs (OpenAPI, ReDoc)
- Automatic validation and serialization with Pydantic v2
- The whole stack fits nicely with SQLAlchemy
- I am an experienced Python + FastAPI dev, so it's just easier 🙂

## Features
- A real database (PostgreSQL), the original project relied on SQLite
  - Dedicated DB role to restrict attack surface in case of compromise (no DDL nor DCL)
- **Real** authentication, opaque token-based bearer auth, session management and secure credential 
  storage (argon2 hashing for passwords)
  - Hence login and registration are now distinct
- CORS and rate limiting
- UI and UX are essentially the same as in my original project, just with minor fixes and extensions to work with the new API
- Scalable and fully reproducible application deployment and configuration with docker-compose
- Cleaned up the mess in the old API design (that's on me 😅)

## Build and run
Clone the repo:
```shell
$ git clone https://github.com/sdcirri/wasntaphoto
$ cd wasntaphoto/
```
Install [Docker Compose](https://docs.docker.com/compose/install), then, on the project root, simply run:
```shell
$ docker compose -f docker-compose.sample.yml up -d
```
Everything will build and start automatically. When it's done, visit http://localhost:8080/.

## Debug

### Backend
To run the backend in debug mode:
```shell
$ python backend_demo.py
```
It will also initialize a demo DB and file storage under `/tmp/wasntaphoto`.

### Frontend
In the `webui` folder:
```shell
$ npm install
$ npm run dev
```
Then follow the link on your terminal.

## The name
The original project was named "WASAPhoto" → "Was-A-Photo" → "Wasn't-A-Photo".
