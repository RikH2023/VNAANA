"""Data Access Layer: ORM models, the database session, and repositories.

The database schema itself is owned and created outside this project. The
models only MAP to those existing tables; they don't create or migrate them.
If a column is renamed in the database, update the matching model here.

Nothing outside this package should write SQL or build queries.
"""
