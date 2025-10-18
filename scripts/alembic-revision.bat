@echo off
alembic -c backend/alembic.ini revision --autogenerate -m %*
