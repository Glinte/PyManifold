from os import getenv
from pathlib import Path
from typing import Any, Mapping

import pytest
from markdown import markdown
from pymanifold import ManifoldClient, __version__
from pymanifold.types import Bet, Group, JSONDict, LiteMarket, LiteUser, Market
from vcr import VCR


API_KEY = getenv("MANIFOLD_API_KEY", "fake_api_key")
LOCAL_FOLDER = str(Path(__file__).parent)

manifold_vcr = VCR(
    cassette_library_dir=LOCAL_FOLDER + "/fixtures/cassettes",
    record_mode="once",
    match_on=["uri", "method"],
    filter_headers=["authorization"],
)

get_bet_params: list[dict[str, str]] = [
    {"username": "LivInTheLookingGlass"},
    {"market": "will-bitcoins-price-fall-below-25k"},
    {},
]

markdown_comment = """This is an example Markdown comment to test the new Markdown-aware comment API

- This is part of PyManifold, which aims to provide native Python bindings to the Manifold API
- Source code can be found [here](https://github.com/bcongdon/PyManifold)
- Have a picture of a cat:

![A picture of a cat](http://images6.fanpop.com/image/photos/34300000/Kitten-cats-34352405-1600-1200.jpg)
"""
html_comment = markdown(markdown_comment.replace("Markdown", "HTML"))
tiptap_comment: JSONDict = {
    "type": "doc",
    "from": 0,
    "to": 403,
    "content": [
        {
            "type": "paragraph",
            "from": 0,
            "to": 80,
            "content": [
                {
                    "type": "text",
                    "from": 1,
                    "to": 79,
                    "text": "This is an example Tip-Tap comment to test the new Tip-Tap-aware comment API",
                }
            ],
        },
        {
            "type": "bulletList",
            "from": 80,
            "to": 294,
            "content": [
                {
                    "type": "listItem",
                    "from": 81,
                    "to": 189,
                    "content": [
                        {
                            "type": "paragraph",
                            "from": 82,
                            "to": 188,
                            "content": [
                                {
                                    "type": "text",
                                    "from": 83,
                                    "to": 187,
                                    "text": (
                                        "This is part of the PyManifold project, which aims to provide native "
                                        "Python bindings to the Manifold API"
                                    ),
                                }
                            ],
                        }
                    ],
                },
                {
                    "type": "listItem",
                    "from": 189,
                    "to": 264,
                    "content": [
                        {
                            "type": "paragraph",
                            "from": 190,
                            "to": 263,
                            "content": [
                                {
                                    "type": "text",
                                    "from": 191,
                                    "to": 262,
                                    "text": "Source code can be found [here](https://github.com/bcongdon/PyManifold)",
                                }
                            ],
                        }
                    ],
                },
                {
                    "type": "listItem",
                    "from": 264,
                    "to": 293,
                    "content": [
                        {
                            "type": "paragraph",
                            "from": 265,
                            "to": 292,
                            "content": [
                                {
                                    "type": "text",
                                    "from": 266,
                                    "to": 291,
                                    "text": "Have a picture of a cat: ",
                                }
                            ],
                        }
                    ],
                },
            ],
        },
        {
            "type": "paragraph",
            "from": 294,
            "to": 296,
            "content": [
                {
                    "type": "image",
                    "from": 295,
                    "to": 296,
                    "attrs": {
                        "src": "http://images6.fanpop.com/image/photos/34300000/Kitten-cats-34352405-1600-1200.jpg",
                        "alt": "A picture of a cat",
                        "title": None,
                    },
                }
            ],
        },
    ],
}


class DummyResponse:
    """Minimal response stub for request interception in unit tests."""

    def __init__(self, payload: Any):
        self._payload = payload

    def json(self) -> Any:
        """Return the stored payload."""

        return self._payload

    def raise_for_status(self) -> None:
        """Mirror requests.Response.raise_for_status with a no-op."""

        return None


def test_version() -> None:
    assert __version__ == "0.2.0"


@manifold_vcr.use_cassette()  # type: ignore
def test_list_markets() -> None:
    client = ManifoldClient()
    markets = client.list_markets()

    for m in markets:
        validate_lite_market(m)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_markets() -> None:
    client = ManifoldClient()
    markets = client.get_markets()

    for m in markets:
        validate_lite_market(m)


@manifold_vcr.use_cassette()  # type: ignore
def test_list_groups() -> None:
    client = ManifoldClient()
    groups = client.list_groups()

    for g in groups:
        validate_group(g)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_groups() -> None:
    client = ManifoldClient()
    groups = client.get_groups()

    for idx, g in enumerate(groups):
        validate_group(g)
        if idx < 50:  # for the sake of time
            validate_group(client.get_group(slug=g.slug))
            validate_group(client.get_group(id_=g.id))


@manifold_vcr.use_cassette()  # type: ignore
def test_get_user() -> None:
    client = ManifoldClient()
    for username in ["v", "LivInTheLookingGlass"]:
        user = client.get_user(username)
        validate_lite_user(user)


@manifold_vcr.use_cassette()  # type: ignore
def test_list_bets() -> None:
    client = ManifoldClient()
    limit = 45
    for kwargs in get_bet_params:
        key = "-".join(kwargs) or "none"
        with manifold_vcr.use_cassette(f"test_list_bet/{key}.yaml"):
            bets = client.list_bets(limit=limit, **kwargs)

            for idx, b in enumerate(bets):
                assert idx < limit
                validate_bet(b)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_bets() -> None:
    client = ManifoldClient()
    limit = 45
    for kwargs in get_bet_params:
        key = "-".join(kwargs) or "none"
        with manifold_vcr.use_cassette(f"test_get_bet/{key}.yaml"):
            bets = client.get_bets(limit=limit, **kwargs)

            for idx, b in enumerate(bets):
                assert idx < limit
                validate_bet(b)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_market_by_url() -> None:
    client = ManifoldClient()

    slug = "will-bitcoins-price-fall-below-25k"
    url = "https://manifold.markets/bcongdon/" + slug
    market = client.get_market_by_url(url)
    assert market.slug == slug
    assert market.id == "rIR6mWqaO9xKLifr6cLL"
    assert market.url == url
    validate_market(market)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_market_by_slug() -> None:
    client = ManifoldClient()

    slug = "will-bitcoins-price-fall-below-25k"
    market = client.get_market_by_slug("will-bitcoins-price-fall-below-25k")
    assert market.slug == slug
    assert market.id == "rIR6mWqaO9xKLifr6cLL"
    assert market.url == "https://manifold.markets/bcongdon/" + slug
    validate_market(market)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_market_by_id() -> None:
    client = ManifoldClient()

    id = "rIR6mWqaO9xKLifr6cLL"
    market = client.get_market_by_id(id)
    assert market.slug == "will-bitcoins-price-fall-below-25k"
    assert market.id == id
    assert (
        market.url
        == "https://manifold.markets/bcongdon/will-bitcoins-price-fall-below-25k"
    )
    assert len(market.bets) == 49
    assert len(market.comments) == 5
    validate_market(market)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_comment() -> None:
    contract = "fobho6eQKxn4YhITF1a8"
    client = ManifoldClient(api_key=API_KEY)

    client.create_comment(market=contract, mode="markdown", comment=markdown_comment)
    client.create_comment(market=contract, mode="html", comment=html_comment)
    client.create_comment(market=contract, mode="tiptap", comment=tiptap_comment)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_bet_binary() -> None:
    client = ManifoldClient(api_key=API_KEY)
    betId = client.create_bet(contractId="BxFQCoaaxBqRcnzJb1mV", amount=1, outcome="NO")
    assert betId == "ZhwL5DngCKdrZ7TQQFad"


@manifold_vcr.use_cassette()  # type: ignore
def test_create_bet_free_response() -> None:
    client = ManifoldClient(api_key=API_KEY)
    betId = client.create_bet(contractId="Hbeirep6H6GXHFNiX6M1", amount=1, outcome="4")
    assert betId == "8qgMoiHYfQlvkuyd3NRa"


@manifold_vcr.use_cassette()  # type: ignore
def test_create_market_binary() -> None:
    client = ManifoldClient(api_key=API_KEY)
    market = client.create_binary_market(
        question="Testing Binary Market creation through API",
        initialProb=99,
        description="Going to resolves as N/A",
        tags=["fun"],
        closeTime=4102444800000,
    )
    validate_lite_market(market)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_market_free_response() -> None:
    client = ManifoldClient(api_key=API_KEY)
    market = client.create_free_response_market(
        question="Testing Free Response Market creation through API",
        description="Going to resolves as N/A",
        tags=["fun"],
        closeTime=4102444800000,
    )
    validate_lite_market(market)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_market_multiple_choice() -> None:
    client = ManifoldClient(api_key=API_KEY)
    market = client.create_multiple_choice_market(
        question="Testing Multiple Choice creation through API",
        description="Going to resolves as N/A",
        tags=["fun"],
        closeTime=5102444800000,
        answers=["sounds good", "alright", "I don't care"],
    )
    validate_lite_market(market)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_market_numeric() -> None:
    client = ManifoldClient(api_key=API_KEY)
    market = client.create_numeric_market(
        question="Testing Numeric Response Market creation through API",
        minValue=0,
        maxValue=100,
        isLogScale=False,
        initialValue=50,
        description="Going to resolves as N/A",
        tags=["fun"],
        closeTime=5102444800000,
    )
    validate_lite_market(market)


@manifold_vcr.use_cassette()  # type: ignore
def test_resolve_market_binary() -> None:
    client = ManifoldClient(api_key=API_KEY)
    client.resolve_market("l6jsJPhOWSztXtzqhpU7", 100)


@manifold_vcr.use_cassette()  # type: ignore
def test_resolve_market_free_resonse() -> None:
    client = ManifoldClient(api_key=API_KEY)
    client.resolve_market("qjwjSMWj1s8Hr21hVbPC", {1: 50, 3: 50})


@manifold_vcr.use_cassette()  # type: ignore
def test_resolve_market_multiple_choice() -> None:
    client = ManifoldClient(api_key=API_KEY)
    client.resolve_market("TEW8dlA3pxk3GalxeQkI", {0: 50, 2: 50})


@manifold_vcr.use_cassette()  # type: ignore
def test_resolve_market_pseudo_numeric() -> None:
    client = ManifoldClient(api_key=API_KEY)
    client.resolve_market("MIVgHSvQ1s9MRGpm9QUb", 2045)


@manifold_vcr.use_cassette()  # type: ignore
def test_cancel_market() -> None:
    client = ManifoldClient(api_key=API_KEY)
    client.cancel_market("H8Dc6yCj4TkvJfoOitYr")


def test_get_markets_includes_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_get(*, url: str, params: dict[str, Any]) -> DummyResponse:
        captured["url"] = url
        captured["params"] = params
        return DummyResponse(
            [
                {
                    "id": "m1",
                    "creatorId": "c1",
                    "creatorUsername": "user",
                    "creatorName": "User",
                }
            ]
        )

    monkeypatch.setattr("pymanifold.lib.requests.get", fake_get)

    client = ManifoldClient()
    markets = list(
        client.get_markets(
            limit=10,
            before="before-id",
            sort="last-bet-time",
            order="asc",
            userId="uid",
            groupId="gid",
        )
    )

    assert captured["url"].endswith("/markets")
    assert captured["params"] == {
        "limit": 10,
        "before": "before-id",
        "sort": "last-bet-time",
        "order": "asc",
        "userId": "uid",
        "groupId": "gid",
    }
    assert markets[0].id == "m1"


def test_get_groups_supports_before_time(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_get(*, url: str, params: dict[str, Any]) -> DummyResponse:
        captured["url"] = url
        captured["params"] = params
        return DummyResponse([{"id": "g1", "name": "Group", "creatorId": "creator"}])

    monkeypatch.setattr("pymanifold.lib.requests.get", fake_get)

    client = ManifoldClient()
    groups = list(client.get_groups(availableToUserId="uid", beforeTime=123))

    assert captured["url"].endswith("/groups")
    assert captured["params"] == {"availableToUserId": "uid", "beforeTime": 123}
    assert groups[0].id == "g1"


def test_get_bets_includes_new_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_get(*, url: str, params: dict[str, Any]) -> DummyResponse:
        captured["url"] = url
        captured["params"] = params
        return DummyResponse(
            [
                {
                    "id": "b1",
                    "contractId": "c1",
                    "amount": 5,
                    "createdTime": 1,
                }
            ]
        )

    monkeypatch.setattr("pymanifold.lib.requests.get", fake_get)

    client = ManifoldClient()
    bets = list(
        client.get_bets(
            limit=50,
            before="before-bet",
            username="name",
            market="legacy",
            userId="uid",
            contractId=["c1", "c2"],
            contractSlug="slug",
            after="after-bet",
            beforeTime=111,
            afterTime=42,
            kinds=["open-limit", "other"],
            order="asc",
        )
    )

    assert captured["url"].endswith("/bets")
    assert captured["params"] == {
        "limit": 50,
        "before": "before-bet",
        "username": "name",
        "userId": "uid",
        "contractSlug": "slug",
        "after": "after-bet",
        "beforeTime": 111,
        "afterTime": 42,
        "order": "asc",
        "contractId": ["c1", "c2"],
        "kinds": "open-limit,other",
    }
    assert bets[0].id == "b1"


def test_get_bets_supports_market_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_get(*, url: str, params: dict[str, Any]) -> DummyResponse:
        captured["params"] = params
        return DummyResponse(
            [{"id": "b2", "contractId": "legacy", "amount": 1, "createdTime": 2}]
        )

    monkeypatch.setattr("pymanifold.lib.requests.get", fake_get)

    client = ManifoldClient()
    list(client.get_bets(market="legacy"))

    assert captured["params"] == {"contractId": "legacy"}


def test_create_bet_accepts_optional_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_post(
        *, url: str, json: dict[str, Any], headers: dict[str, str]
    ) -> DummyResponse:
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return DummyResponse({"betId": "bid"})

    monkeypatch.setattr("pymanifold.lib.requests.post", fake_post)

    client = ManifoldClient(api_key="key")
    bet_id = client.create_bet(
        contractId="c1",
        amount=10,
        outcome="YES",
        limitProb=0.5,
        expiresAt=123,
        expiresMillisAfter=456,
        dryRun=True,
    )

    assert bet_id == "bid"
    assert captured["json"] == {
        "amount": 10,
        "contractId": "c1",
        "outcome": "YES",
        "limitProb": 0.5,
        "expiresAt": 123,
        "expiresMillisAfter": 456,
        "dryRun": True,
    }
    assert captured["headers"]["Authorization"] == "Key key"


def validate_lite_market(market: LiteMarket) -> None:
    assert market.id
    assert market.creatorUsername
    assert market.question
    # assert market.description
    assert market.outcomeType in [
        "BINARY",
        "FREE_RESPONSE",
        "NUMERIC",
        "PSEUDO_NUMERIC",
        "NUMERIC",
        "MULTIPLE_CHOICE",
    ]
    assert market.pool is None or isinstance(market.pool, (int, float, Mapping))
    assert all(
        hasattr(market, attr)
        for attr in [
            "description",
            "creatorAvatarUrl",
            "tags",
            "volume7Days",
            "volume24Hours",
            "isResolved",
            "lastUpdatedTime",
            "probability",
            "resolutionTime",
            "resolution",
            "resolutionProbability",
            "p",
            "totalLiquidity",
            "min",
            "max",
            "isLogScale",
        ]
    )


def validate_market(market: Market) -> None:
    validate_lite_market(market)

    for b in market.bets:
        assert b.id
        assert b.amount != 0

    for c in market.comments:
        assert c.id
        assert c.contractId
        assert c.text
        assert c.userAvatarUrl
        assert c.userId
        assert c.userName
        assert c.userUsername


def validate_bet(bet: Bet) -> None:
    # assert bet.amount
    assert bet.contractId
    assert bet.createdTime
    assert bet.id
    assert hasattr(bet, "amount")


def validate_lite_user(user: LiteUser) -> None:
    assert user.id
    assert user.createdTime
    assert user.name
    assert user.username
    assert user.url
    assert all(
        hasattr(user, attr)
        for attr in [
            "avatarUrl",
            "bio",
            "bannerUrl",
            "website",
            "twitterHandle",
            "discordHandle",
            "balance",
            "totalDeposits",
            "totalPnLCached",
            "creatorVolumeCached",
        ]
    )


def validate_group(group: Group) -> None:
    assert group.name
    assert group.creatorId
    assert group.id
    assert group.mostRecentActivityTime
    assert group.mostRecentContractAddedTime
    assert group.createdTime
    assert group.slug

    client = ManifoldClient()

    for contract in group.contracts(client):
        validate_market(contract)

    for member in group.members(client):
        validate_lite_user(member)
