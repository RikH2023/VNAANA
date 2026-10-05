"""Checking the table schemas before continue"""
import unittest
import uuid

from sqlalchemy import create_engine, event, inspect, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, configure_mappers
from sqlalchemy.schema import CreateTable

from Backend.Dal.models import (
    Article, Base, EngagementEvent, Provider, Story,
    StoryArticle, StoryStatus, StoryTag, Tag, User, UserTag,
)
from Backend.Dal.repositories import ArticleRepository, UserRepository


@compiles(JSONB, "sqlite")
def compile_test_jsonb(type_, compiler, **kwargs):
    return "JSON"


class SchemaTests(unittest.TestCase):
    def test_postgresql_schema_contract(self):
        configure_mappers()
        self.assertEqual([s.value for s in StoryStatus], ["draft", "published", "archived"])
        self.assertEqual(Story.__table__.c.status.default.arg, StoryStatus.draft)
        self.assertEqual(Story.__table__.c.status.server_default.arg, "draft")
        self.assertEqual(Story.__table__.c.status.type.enums, ["draft", "published", "archived"])
        self.assertEqual(len(Base.metadata.tables), 9)
        self.assertEqual(sum(len(t.columns) for t in Base.metadata.tables.values()), 52)
        expected_server_defaults = {
            ("users", "analytics_consent"),
            ("providers", "created_at"),
            ("articles", "first_seen_at"),
            ("articles", "last_seen_at"),
            ("stories", "status"),
            ("stories", "last_updated_at"),
            ("story_articles", "is_primary"),
            ("story_articles", "added_at"),
            ("user_tags", "updated_at"),
            ("engagement_events", "occurred_at"),
        }
        actual_server_defaults = {
            (table.name, column.name)
            for table in Base.metadata.tables.values()
            for column in table.columns
            if column.server_default is not None
        }
        self.assertEqual(actual_server_defaults, expected_server_defaults)
        for model, name in [(Provider, "domain"), (Article, "canonical_url"), (Tag, "name")]:
            self.assertTrue(model.__table__.c[name].unique)
        for table in Base.metadata.tables.values():
            ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
            self.assertIn("PRIMARY KEY", ddl)
            for fk in table.foreign_keys:
                expected = "SET NULL" if table.name == "engagement_events" else (
                    None if table.name == "articles" else "CASCADE"
                )
                self.assertEqual(fk.ondelete, expected)
        for model, columns in [(StoryArticle, ["story_id", "article_id"]),
                               (StoryTag, ["story_id", "tag_id"]),
                               (UserTag, ["user_id", "tag_id"])]:
            self.assertEqual(list(model.__table__.primary_key.columns.keys()), columns)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        event.listen(self.engine, "connect", lambda db, _: db.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)
        self.provider = Provider(name="Source", domain="example.test", reliability_status="verified")
        self.db.add(self.provider)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_ingestion_preserves_identity_and_non_null_content(self):
        repo = ArticleRepository(self.db)
        first, created = repo.ingest(provider_id=self.provider.id, canonical_url="https://example.test/a",
                                     title="Initial", description="Keep me")
        self.assertTrue(created)
        self.db.commit()
        original_id, first_seen = first.id, first.first_seen_at
        updated, created = repo.ingest(provider_id=self.provider.id, canonical_url=first.canonical_url,
                                       title="Refreshed", description=None)
        self.db.commit()
        self.assertFalse(created)
        self.assertEqual(updated.id, original_id)
        self.assertEqual(updated.first_seen_at, first_seen)
        self.assertEqual(updated.title, "Refreshed")
        self.assertEqual(updated.description, "Keep me")
        self.assertEqual(len(self.db.scalars(select(Article)).all()), 1)
        self.assertIsNotNone(updated.last_seen_at)

    def test_deletion_retains_events_and_removes_associations(self):
        for parent_kind in ("user", "story", "article", "tag"):
            for loaded in (False, True):
                with self.subTest(parent=parent_kind, loaded=loaded):
                    user, story, tag = User(), Story(title="Story"), Tag(name=str(uuid.uuid4()))
                    article = Article(provider_id=self.provider.id, canonical_url=str(uuid.uuid4()), title="Article")
                    self.db.add_all([user, story, tag, article])
                    self.db.flush()
                    self.db.add_all([
                        UserTag(user_id=user.id, tag_id=tag.id),
                        StoryTag(story_id=story.id, tag_id=tag.id),
                        StoryArticle(story_id=story.id, article_id=article.id),
                    ])
                    engagement = EngagementEvent(user_id=user.id, story_id=story.id, article_id=article.id,
                                                 session_id=uuid.uuid4(), event_type="view")
                    self.db.add(engagement)
                    self.db.commit()
                    parent = {"user": user, "story": story, "article": article, "tag": tag}[parent_kind]
                    if loaded:
                        for relation in inspect(type(parent)).relationships:
                            getattr(parent, relation.key)
                    if parent_kind == "user":
                        UserRepository(self.db).delete(parent)
                    else:
                        self.db.delete(parent)
                    self.db.commit()
                    self.db.expire_all()
                    retained = self.db.get(EngagementEvent, engagement.id)
                    self.assertIsNotNone(retained)
                    if parent_kind != "tag":
                        self.assertIsNone(getattr(retained, parent_kind + "_id"))
                    associations = {
                        "user": [(UserTag, "user_id", user.id)],
                        "story": [(StoryTag, "story_id", story.id), (StoryArticle, "story_id", story.id)],
                        "article": [(StoryArticle, "article_id", article.id)],
                        "tag": [(StoryTag, "tag_id", tag.id), (UserTag, "tag_id", tag.id)],
                    }
                    for model, field, value in associations[parent_kind]:
                        self.assertIsNone(self.db.scalars(select(model).where(getattr(model, field) == value)).first())

    def test_server_defaults_without_orm_defaults(self):
        # Raw SQL proves these defaults are supplied by the database.
        story_id, user_id = uuid.uuid4().hex, uuid.uuid4().hex
        self.db.execute(text("INSERT INTO stories (id, title) VALUES (:id, 'New')"), {"id": story_id})
        self.db.execute(text("INSERT INTO users (id) VALUES (:id)"), {"id": user_id})
        story = self.db.get(Story, uuid.UUID(story_id))
        user = self.db.get(User, uuid.UUID(user_id))
        self.assertEqual(story.status, StoryStatus.draft)
        self.assertIsNotNone(story.last_updated_at)
        self.assertFalse(user.analytics_consent)


if __name__ == "__main__":
    unittest.main()
