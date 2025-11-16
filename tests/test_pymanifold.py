from os import getenv
from pathlib import Path

import asyncio
from collections.abc import Coroutine, Mapping
from typing import Any, Callable, TypeVar

from markdown import markdown
from pymanifold import ManifoldClient, __version__
from pymanifold.types import Bet, Group, JSONDict, LiteMarket, LiteUser, Market
from vcr import VCR

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Execute a coroutine in a dedicated event loop for pytest compatibility."""

    return asyncio.run(coro)


ClientTest = Callable[[ManifoldClient], Coroutine[Any, Any, None]]


def run_client_test(func: ClientTest, *, api_key: str | None = None) -> None:
    """Run a client-aware coroutine within an async context manager."""

    async def _runner() -> None:
        async with ManifoldClient(api_key=api_key) as client:
            await func(client)

    run_async(_runner())


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


def test_version() -> None:
    assert __version__ == "0.2.0"


@manifold_vcr.use_cassette()  # type: ignore
def test_list_markets() -> None:
    async def _run(client: ManifoldClient) -> None:
        markets = await client.list_markets()

        for market in markets:
            validate_lite_market(market)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_markets() -> None:
    async def _run(client: ManifoldClient) -> None:
        markets = await client.get_markets()

        for market in markets:
            validate_lite_market(market)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_list_groups() -> None:
    async def _run(client: ManifoldClient) -> None:
        groups = await client.list_groups()

        for group in groups:
            await validate_group(group, client)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_groups() -> None:
    async def _run(client: ManifoldClient) -> None:
        groups = await client.get_groups()

        for idx, group in enumerate(groups):
            await validate_group(group, client)
            if idx < 50:  # for the sake of time
                await validate_group(await client.get_group(slug=group.slug), client)
                await validate_group(await client.get_group(id_=group.id), client)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_user() -> None:
    async def _run(client: ManifoldClient) -> None:
        for username in ["v", "LivInTheLookingGlass"]:
            user = await client.get_user(username)
            validate_lite_user(user)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_list_bets() -> None:
    async def _run(client: ManifoldClient) -> None:
        limit = 45
        for kwargs in get_bet_params:
            key = "-".join(kwargs) or "none"
            with manifold_vcr.use_cassette(f"test_list_bet/{key}.yaml"):
                bets = await client.list_bets(limit=limit, **kwargs)

                for idx, bet in enumerate(bets):
                    assert idx < limit
                    validate_bet(bet)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_bets() -> None:
    async def _run(client: ManifoldClient) -> None:
        limit = 45
        for kwargs in get_bet_params:
            key = "-".join(kwargs) or "none"
            with manifold_vcr.use_cassette(f"test_get_bet/{key}.yaml"):
                bets = await client.get_bets(limit=limit, **kwargs)

                for idx, bet in enumerate(bets):
                    assert idx < limit
                    validate_bet(bet)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_market_by_url() -> None:
    async def _run(client: ManifoldClient) -> None:
        slug = "will-bitcoins-price-fall-below-25k"
        url = "https://manifold.markets/bcongdon/" + slug
        market = await client.get_market_by_url(url)
        assert market.slug == slug
        assert market.id == "rIR6mWqaO9xKLifr6cLL"
        assert market.url == url
        validate_market(market)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_market_by_slug() -> None:
    async def _run(client: ManifoldClient) -> None:
        slug = "will-bitcoins-price-fall-below-25k"
        market = await client.get_market_by_slug(slug)
        assert market.slug == slug
        assert market.id == "rIR6mWqaO9xKLifr6cLL"
        assert market.url == "https://manifold.markets/bcongdon/" + slug
        validate_market(market)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_get_market_by_id() -> None:
    async def _run(client: ManifoldClient) -> None:
        market_id = "rIR6mWqaO9xKLifr6cLL"
        market = await client.get_market_by_id(market_id)
        assert market.slug == "will-bitcoins-price-fall-below-25k"
        assert market.id == market_id
        assert (
            market.url
            == "https://manifold.markets/bcongdon/will-bitcoins-price-fall-below-25k"
        )
        assert len(market.bets) == 49
        assert len(market.comments) == 5
        validate_market(market)

    run_client_test(_run)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_comment() -> None:
    contract = "fobho6eQKxn4YhITF1a8"

    async def _run(client: ManifoldClient) -> None:
        await client.create_comment(
            market=contract, mode="markdown", comment=markdown_comment
        )
        await client.create_comment(market=contract, mode="html", comment=html_comment)
        await client.create_comment(
            market=contract, mode="tiptap", comment=tiptap_comment
        )

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_bet_binary() -> None:
    async def _run(client: ManifoldClient) -> None:
        bet_id = await client.create_bet(
            contractId="BxFQCoaaxBqRcnzJb1mV", amount=1, outcome="NO"
        )
        assert bet_id == "ZhwL5DngCKdrZ7TQQFad"

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_bet_free_response() -> None:
    async def _run(client: ManifoldClient) -> None:
        bet_id = await client.create_bet(
            contractId="Hbeirep6H6GXHFNiX6M1", amount=1, outcome="4"
        )
        assert bet_id == "8qgMoiHYfQlvkuyd3NRa"

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_market_binary() -> None:
    async def _run(client: ManifoldClient) -> None:
        market = await client.create_binary_market(
            question="Testing Binary Market creation through API",
            initialProb=99,
            description="Going to resolves as N/A",
            tags=["fun"],
            closeTime=4102444800000,
        )
        validate_lite_market(market)

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_market_free_response() -> None:
    async def _run(client: ManifoldClient) -> None:
        market = await client.create_free_response_market(
            question="Testing Free Response Market creation through API",
            description="Going to resolves as N/A",
            tags=["fun"],
            closeTime=4102444800000,
        )
        validate_lite_market(market)

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_market_multiple_choice() -> None:
    async def _run(client: ManifoldClient) -> None:
        market = await client.create_multiple_choice_market(
            question="Testing Multiple Choice creation through API",
            description="Going to resolves as N/A",
            tags=["fun"],
            closeTime=5102444800000,
            answers=["sounds good", "alright", "I don't care"],
        )
        validate_lite_market(market)

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_create_market_numeric() -> None:
    async def _run(client: ManifoldClient) -> None:
        market = await client.create_numeric_market(
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

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_resolve_market_binary() -> None:
    async def _run(client: ManifoldClient) -> None:
        await client.resolve_market("l6jsJPhOWSztXtzqhpU7", 100)

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_resolve_market_free_resonse() -> None:
    async def _run(client: ManifoldClient) -> None:
        await client.resolve_market("qjwjSMWj1s8Hr21hVbPC", {1: 50, 3: 50})

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_resolve_market_multiple_choice() -> None:
    async def _run(client: ManifoldClient) -> None:
        await client.resolve_market("TEW8dlA3pxk3GalxeQkI", {0: 50, 2: 50})

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_resolve_market_pseudo_numeric() -> None:
    async def _run(client: ManifoldClient) -> None:
        await client.resolve_market("MIVgHSvQ1s9MRGpm9QUb", 2045)

    run_client_test(_run, api_key=API_KEY)


@manifold_vcr.use_cassette()  # type: ignore
def test_cancel_market() -> None:
    async def _run(client: ManifoldClient) -> None:
        await client.cancel_market("H8Dc6yCj4TkvJfoOitYr")

    run_client_test(_run, api_key=API_KEY)


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


async def validate_group(group: Group, client: ManifoldClient | None = None) -> None:
    assert group.name
    assert group.creatorId
    assert group.id
    assert group.mostRecentActivityTime
    assert group.mostRecentContractAddedTime
    assert group.createdTime
    assert group.slug

    if client is None:
        async with ManifoldClient() as managed_client:
            contracts = await group.contracts(managed_client)
            for contract in contracts:
                validate_market(contract)

            members = await group.members(managed_client)
            for member in members:
                validate_lite_user(member)
        return

    contracts = await group.contracts(client)
    for contract in contracts:
        validate_market(contract)

    members = await group.members(client)
    for member in members:
        validate_lite_user(member)
