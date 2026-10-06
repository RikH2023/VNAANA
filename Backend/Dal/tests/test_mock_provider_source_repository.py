import pytest

from Backend.Dal.repositories.mock_provider_source_repository import (
    MockProviderSourceRepository,
)


@pytest.mark.asyncio
async def test_get_active_sources():
    repository = MockProviderSourceRepository()

    sources = await repository.get_active_sources()

    assert sources
    assert all(source.is_active for source in sources)