"""Checking the table schemas before continue"""
import unittest
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import create_engine, event, inspect, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, configure_mappers
from sqlalchemy.schema import CreateTable

from Backend.Dal.models import (
    Article, Base, EngagementEvent, Provider, Story,
    StoryArticle, StoryStatus, StoryTag, Tag, User, UserTag,
    EventWeight,
)
from Backend.Dal.repositories import ArticleRepository, UserRepository, EngagementEventRepository
from Backend.Logic.exceptions import NotFoundError
from sqlalchemy.exc import IntegrityError
from Backend.Presentation.schemas.users import UserCreate, UserRead, EngagementEventRead


@compiles(JSONB, "sqlite")
def compile_test_jsonb(type_, compiler, **kwargs):
    return "JSON"


class SchemaTests(unittest.TestCase):
    def test_revised_columns_and_indexes(self):
        self.assertTrue(any(
            type(constraint).__name__ == "UniqueConstraint"
            and list(constraint.columns.keys()) == ["auth_provider", "auth_subject"]
            for constraint in User.__table__.constraints
        ))
        for column in (User.__table__.c.auth_provider, User.__table__.c.auth_subject,
                       UserTag.__table__.c.is_declared, UserTag.__table__.c.score,
                       EngagementEvent.__table__.c.ingested_at):
            self.assertFalse(column.nullable)
            self.assertIsNone(column.server_default)
            self.assertIsNone(column.default)
        for column in (User.__table__.c.affinity_updated_at, UserTag.__table__.c.computed_at):
            self.assertTrue(column.nullable)
            self.assertTrue(column.type.timezone)
        self.assertTrue(EngagementEvent.__table__.c.ingested_at.type.timezone)
        self.assertEqual(str(UserTag.__table__.c.score.type.compile(dialect=postgresql.dialect())), "FLOAT")
        self.assertEqual(list(EventWeight.__table__.primary_key.columns.keys()), ["event_type"])
        self.assertEqual(str(EventWeight.__table__.c.weight.type), "NUMERIC(6, 2)")
        self.assertFalse(EventWeight.__table__.c.weight.nullable)
        fk = next(iter(EngagementEvent.__table__.c.event_type.foreign_keys))
        self.assertEqual(fk.target_fullname, "event_weights.event_type")
        self.assertEqual(fk.name, "fk_engagement_events_event_type")
        self.assertEqual(
            {tuple(index.columns.keys()) for index in EngagementEvent.__table__.indexes},
            {("user_id", "occurred_at"), ("story_id", "occurred_at"), ("session_id", "occurred_at")},
        )

    def test_postgresql_schema_contract(self):
        configure_mappers()
        self.assertEqual([s.value for s in StoryStatus], ["draft", "published", "archived"])
        self.assertEqual(Story.__table__.c.status.default.arg, StoryStatus.draft)
        self.assertEqual(Story.__table__.c.status.server_default.arg, "draft")
        self.assertEqual(Story.__table__.c.status.type.enums, ["draft", "published", "archived"])
        self.assertEqual(len(Base.metadata.tables), 10)
        self.assertEqual(sum(len(t.columns) for t in Base.metadata.tables.values()), 61)
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
                expected = "SET NULL" if table.name == "engagement_events" and fk.parent.name != "event_type" else (
                    None if table.name in ("articles", "engagement_events") else "CASCADE"
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
        self.db.add(EventWeight(event_type="view", weight=Decimal("1.00")))
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
                    user = User(auth_provider="test", auth_subject=str(uuid.uuid4()))
                    story, tag = Story(title="Story"), Tag(name=str(uuid.uuid4()))
                    article = Article(provider_id=self.provider.id, canonical_url=str(uuid.uuid4()), title="Article")
                    self.db.add_all([user, story, tag, article])
                    self.db.flush()
                    self.db.add_all([
                        UserTag(user_id=user.id, tag_id=tag.id, is_declared=True, score=0.0),
                        StoryTag(story_id=story.id, tag_id=tag.id),
                        StoryArticle(story_id=story.id, article_id=article.id),
                    ])
                    engagement = EngagementEvent(user_id=user.id, story_id=story.id, article_id=article.id,
                                                 session_id=uuid.uuid4(), event_type="view",
                                                 ingested_at=datetime.now(timezone.utc))
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
        self.db.execute(text("INSERT INTO users (id, auth_provider, auth_subject) VALUES (:id, 'test', :id)"), {"id": user_id})
        story = self.db.get(Story, uuid.UUID(story_id))
        user = self.db.get(User, uuid.UUID(user_id))
        self.assertEqual(story.status, StoryStatus.draft)
        self.assertIsNotNone(story.last_updated_at)
        self.assertFalse(user.analytics_consent)

    def test_auth_identity_and_domain_mapping(self):
        payload = UserCreate(auth_provider="test", auth_subject="subject").model_dump()
        repo = UserRepository(self.db)
        user = repo.add(**payload)
        self.assertEqual(repo.get(user.id).auth_subject, "subject")
        self.assertIsNone(UserRead.model_validate(user).affinity_updated_at)
        with self.assertRaises(IntegrityError):
            with self.db.begin_nested():
                repo.add(**payload)
        repo.add(auth_provider="another", auth_subject="subject")

    def test_tag_selection_preserves_affinity(self):
        repo = UserRepository(self.db)
        user = repo.add(auth_provider="test", auth_subject="tags")
        tag = Tag(name="science")
        self.db.add(tag)
        self.db.flush()
        repo.replace_tags(user, [tag.id])
        row = self.db.get(UserTag, (user.id, tag.id))
        self.assertTrue(row.is_declared)
        self.assertEqual(row.score, 0.0)
        row.score = 2.5
        row.computed_at = datetime.now(timezone.utc)
        self.db.flush()
        repo.replace_tags(user, [])
        self.assertFalse(row.is_declared)
        self.assertEqual(row.score, 2.5)
        self.assertEqual(repo.get_tag_ids(user.id), [])
        repo.replace_tags(user, [tag.id])
        self.assertTrue(row.is_declared)
        self.assertEqual(row.score, 2.5)
        self.assertIsNotNone(row.computed_at)

    def test_event_receipt_time_and_valid_type(self):
        repo = EngagementEventRepository(self.db)
        recorded = repo.add(session_id=uuid.uuid4(), event_type="view")
        self.assertIsNotNone(recorded.ingested_at)
        self.assertEqual(EngagementEventRead.model_validate(recorded).ingested_at, recorded.ingested_at)
        with self.assertRaises(NotFoundError):
            repo.add(session_id=uuid.uuid4(), event_type="unknown")
        with self.assertRaises(IntegrityError):
            with self.db.begin_nested():
                self.db.add(EngagementEvent(session_id=uuid.uuid4(), event_type="unknown",
                                            ingested_at=datetime.now(timezone.utc)))
                self.db.flush()
        with self.assertRaises(IntegrityError):
            with self.db.begin_nested():
                self.db.add(EngagementEvent(session_id=uuid.uuid4(), event_type="view"))
                self.db.flush()


if __name__ == "__main__":
    unittest.main()
