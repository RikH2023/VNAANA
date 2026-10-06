from uuid import UUID, uuid5, NAMESPACE_URL

from Backend.Logic.domain.provider_source import ProviderSource


def _provider_id(domain: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"provider:{domain}")


def _source_id(provider_domain: str, source_url: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"source:{provider_domain}:{source_url}")


def _source(
    *,
    name: str,
    domain: str,
    source_type: str,
    url: str,
    poll_interval_minutes: int,
    is_active: bool = True,
    configuration: dict | None = None,
) -> ProviderSource:
    provider_id = _provider_id(domain)

    return ProviderSource(
        id=_source_id(domain, url),
        provider_id=provider_id,
        provider_name=name,
        provider_domain=domain,
        name=f"{name} RSS",
        source_type=source_type,
        url=url,
        poll_interval_minutes=poll_interval_minutes,
        is_active=is_active,
        configuration=configuration or {},
    )


MOCK_PROVIDER_SOURCES: list[ProviderSource] = [
    # National
    _source(
        name="NOS",
        domain="nos.nl",
        source_type="rss",
        url="https://feeds.nos.nl/nosnieuwsalgemeen",
        poll_interval_minutes=15,
    ),
    _source(
        name="NU.nl",
        domain="nu.nl",
        source_type="rss",
        url="https://www.nu.nl/rss",
        poll_interval_minutes=10,
    ),
    _source(
        name="RTL Nieuws",
        domain="rtl.nl",
        source_type="external_rss",
        url="",
        poll_interval_minutes=20,
        is_active=False,
        configuration={
            "provider": "feeder",
            "status": "feed_url_not_mapped_yet",
            "website_url": "https://www.rtl.nl",
        },
    ),

    # DPG Media
    _source(
        name="AD",
        domain="ad.nl",
        source_type="rss",
        url="https://www.ad.nl/home/rss.xml",
        poll_interval_minutes=45,
    ),
    _source(
        name="De Volkskrant",
        domain="volkskrant.nl",
        source_type="rss",
        url="https://www.volkskrant.nl/voorpagina/rss",
        poll_interval_minutes=45,
    ),
    _source(
        name="Het Parool",
        domain="parool.nl",
        source_type="rss",
        url="https://www.parool.nl/voorpagina/rss.xml",
        poll_interval_minutes=45,
    ),
    _source(
        name="Trouw",
        domain="trouw.nl",
        source_type="rss",
        url="https://www.trouw.nl/voorpagina/rss.xml",
        poll_interval_minutes=45,
    ),
    _source(
        name="De Gelderlander",
        domain="gelderlander.nl",
        source_type="rss",
        url="https://www.gelderlander.nl/home/rss.xml",
        poll_interval_minutes=45,
    ),
    _source(
        name="De Stentor",
        domain="destentor.nl",
        source_type="rss",
        url="https://www.destentor.nl/home/rss.xml",
        poll_interval_minutes=45,
    ),
    _source(
        name="Brabants Dagblad",
        domain="bd.nl",
        source_type="rss",
        url="https://www.bd.nl/home/rss.xml",
        poll_interval_minutes=45,
    ),
    _source(
        name="Eindhovens Dagblad",
        domain="ed.nl",
        source_type="rss",
        url="https://www.ed.nl/home/rss.xml",
        poll_interval_minutes=20,
    ),
    _source(
        name="Tubantia",
        domain="tubantia.nl",
        source_type="rss",
        url="https://www.tubantia.nl/home/rss.xml",
        poll_interval_minutes=20,
    ),
    _source(
        name="PZC",
        domain="pzc.nl",
        source_type="rss",
        url="https://www.pzc.nl/home/rss.xml",
        poll_interval_minutes=20,
    ),

    # Mediahuis / financial
    _source(
        name="NRC",
        domain="nrc.nl",
        source_type="rss",
        url="https://www.nrc.nl/rss/",
        poll_interval_minutes=45,
    ),
    _source(
        name="De Telegraaf",
        domain="telegraaf.nl",
        source_type="rss",
        url="https://www.telegraaf.nl/rss",
        poll_interval_minutes=45,
    ),
    _source(
        name="Het Financieele Dagblad",
        domain="fd.nl",
        source_type="rss",
        url="https://fd.nl/?rss",
        poll_interval_minutes=25,
    ),
    _source(
        name="BNR Nieuwsradio",
        domain="bnr.nl",
        source_type="rss",
        url="https://static.bnr.nl/assets/bnr-next/rss/home.xml",
        poll_interval_minutes=25,
    ),
    _source(
        name="De Limburger",
        domain="limburger.nl",
        source_type="rss",
        url="",
        poll_interval_minutes=20,
        is_active=False,
        configuration={
            "status": "feed_url_not_mapped_yet",
            "website_url": "https://www.limburger.nl",
        },
    ),
    _source(
        name="Dagblad van het Noorden",
        domain="dvhn.nl",
        source_type="rss",
        url="https://dvhn.nl/api/feed/rss",
        poll_interval_minutes=20,
    ),

    # Technology / digital
    _source(
        name="Tweakers",
        domain="tweakers.net",
        source_type="rss",
        url="https://tweakers.net/feeds/mixed.xml",
        poll_interval_minutes=30,
    ),
    _source(
        name="Emerce",
        domain="emerce.nl",
        source_type="rss",
        url="https://www.emerce.nl/feed",
        poll_interval_minutes=30,
    ),
    _source(
        name="Bright",
        domain="bright.nl",
        source_type="rss",
        url="https://www.bright.nl/feed/news.xml",
        poll_interval_minutes=20,
    ),
    _source(
        name="Android Planet",
        domain="androidplanet.nl",
        source_type="rss",
        url="https://www.androidplanet.nl/feed/",
        poll_interval_minutes=30,
    ),

    # Government
    _source(
        name="Rijksoverheid",
        domain="rijksoverheid.nl",
        source_type="rss",
        url=(
            "https://www.rijksoverheid.nl/api/rss?"
            "query=%7B%22filters%22%3A%5B%7B%22field%22%3A%22content_type%22%2C"
            "%22values%22%3A%5B%22pro%3AdownloadDocument%22%2C"
            "%22pro%3AvideoDocument%22%2C%22pro%3AaudioFragmentDocument%22%2C"
            "%22pro%3AfaqDocument%22%5D%2C%22type%22%3A%22any%22%7D%5D%2C"
            "%22resultSearchTerm%22%3A%22%22%2C%22pageTitle%22%3A%22Documenten%22%7D"
        ),
        poll_interval_minutes=20,
    ),
]
