"""Unit tests for the high-level client helpers."""

import asyncio
from dataclasses import dataclass
from typing import Any, Coroutine, Sequence, TypeVar
from unittest.mock import AsyncMock

import pytest

from pymanifold import ManifoldClient
from pymanifold.types import Bet, Comment, DisplayUser, JSONDict, LiteMarket, LiteUser

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Execute a coroutine for synchronous pytest helpers."""

    return asyncio.run(coro)


@dataclass(slots=True)
class EndpointSpec:
    """Parameters describing a single client helper invocation."""

    method_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    http_method: str
    path: str
    response: Any
    expected: Any
    params: Any | None = None
    json_data: JSONDict | None = None
    auth: bool = False


DISPLAY_USER_RAW = {
    "id": "user-id",
    "name": "User",
    "username": "user",
    "avatarUrl": "avatar",
}

LITE_USER_RAW = {
    "id": "lite-id",
    "createdTime": 1,
    "name": "Lite",
    "username": "lite",
    "url": "https://example.com",
}

LITE_MARKET_RAW = {
    "id": "market",
    "creatorId": "creator",
    "creatorUsername": "creator",
    "creatorName": "Creator",
    "question": "Q?",
    "url": "https://manifold.markets",
    "outcomeType": "BINARY",
    "mechanism": "cpmm-1",
}

COMMENT_RAW = {
    "id": "comment",
    "contractId": "contract",
    "createdTime": 1,
    "text": "hello",
}

BET_RAW = {
    "id": "bet",
    "contractId": "contract",
    "createdTime": 1,
    "amount": 10,
}

ENDPOINT_SPECS: Sequence[EndpointSpec] = (
    EndpointSpec(
        method_name="get_user_lite",
        args=("user",),
        kwargs={},
        http_method="GET",
        path="/user/user/lite",
        response=DISPLAY_USER_RAW,
        expected=DisplayUser.from_dict(DISPLAY_USER_RAW),
    ),
    EndpointSpec(
        method_name="get_user_by_id",
        args=("lite-id",),
        kwargs={},
        http_method="GET",
        path="/user/by-id/lite-id",
        response=LITE_USER_RAW,
        expected=LiteUser.from_dict(LITE_USER_RAW),
    ),
    EndpointSpec(
        method_name="get_user_by_id_lite",
        args=("lite-id",),
        kwargs={},
        http_method="GET",
        path="/user/by-id/lite-id/lite",
        response=DISPLAY_USER_RAW,
        expected=DisplayUser.from_dict(DISPLAY_USER_RAW),
    ),
    EndpointSpec(
        method_name="get_authenticated_user",
        args=(),
        kwargs={},
        http_method="GET",
        path="/me",
        response=LITE_USER_RAW,
        expected=LiteUser.from_dict(LITE_USER_RAW),
        auth=True,
    ),
    EndpointSpec(
        method_name="get_user_bets_deprecated",
        args=("user",),
        kwargs={},
        http_method="GET",
        path="/user/user/bets",
        response=[BET_RAW],
        expected=[Bet.from_dict(BET_RAW)],
    ),
    EndpointSpec(
        method_name="get_user_portfolio",
        args=("user-id",),
        kwargs={},
        http_method="GET",
        path="/get-user-portfolio",
        response={"balance": 10},
        expected={"balance": 10},
        params={"userId": "user-id"},
    ),
    EndpointSpec(
        method_name="get_user_portfolio_history",
        args=("user-id", "weekly"),
        kwargs={},
        http_method="GET",
        path="/get-user-portfolio-history",
        response=[{"balance": 1}],
        expected=[{"balance": 1}],
        params={"userId": "user-id", "period": "weekly"},
    ),
    EndpointSpec(
        method_name="get_group_markets_by_id",
        args=("group",),
        kwargs={},
        http_method="GET",
        path="/group/by-id/group/markets",
        response=[LITE_MARKET_RAW],
        expected=[LiteMarket.from_dict(LITE_MARKET_RAW)],
    ),
    EndpointSpec(
        method_name="search_markets",
        args=("term",),
        kwargs={
            "sort": "score",
            "filter_": "open",
            "contractType": "BINARY",
            "topicSlug": "news",
            "creatorId": "creator",
            "limit": 5,
            "offset": 1,
            "liquidity": 50.0,
        },
        http_method="GET",
        path="/search-markets",
        response=[LITE_MARKET_RAW],
        expected=[LiteMarket.from_dict(LITE_MARKET_RAW)],
        params={
            "term": "term",
            "sort": "score",
            "filter": "open",
            "contractType": "BINARY",
            "topicSlug": "news",
            "creatorId": "creator",
            "limit": 5,
            "offset": 1,
            "liquidity": 50.0,
        },
    ),
    EndpointSpec(
        method_name="get_market_probability",
        args=("market",),
        kwargs={},
        http_method="GET",
        path="/market/market/prob",
        response={"prob": 0.5},
        expected={"prob": 0.5},
    ),
    EndpointSpec(
        method_name="get_market_probabilities",
        args=(("m1", "m2"),),
        kwargs={},
        http_method="GET",
        path="/market-probs",
        response={"m1": {"prob": 0.1}, "m2": {"prob": 0.2}},
        expected={"m1": {"prob": 0.1}, "m2": {"prob": 0.2}},
        params=[("ids", "m1"), ("ids", "m2")],
    ),
    EndpointSpec(
        method_name="get_market_positions",
        args=("market",),
        kwargs={
            "order": "shares",
            "top": 5,
            "bottom": 1,
            "userId": "uid",
            "answerId": "aid",
        },
        http_method="GET",
        path="/market/market/positions",
        response=[{"position": 1}],
        expected=[{"position": 1}],
        params={
            "order": "shares",
            "top": 5,
            "bottom": 1,
            "userId": "uid",
            "answerId": "aid",
        },
    ),
    EndpointSpec(
        method_name="get_user_contract_metrics_with_contracts",
        args=("user", 50),
        kwargs={"offset": 5, "order": "profit", "perAnswer": True},
        http_method="GET",
        path="/get-user-contract-metrics-with-contracts",
        response={"contracts": []},
        expected={"contracts": []},
        params={
            "userId": "user",
            "limit": 50,
            "offset": 5,
            "order": "profit",
            "perAnswer": True,
        },
    ),
    EndpointSpec(
        method_name="list_users",
        args=(),
        kwargs={"limit": 2, "before": "cursor"},
        http_method="GET",
        path="/users",
        response=[LITE_USER_RAW],
        expected=[LiteUser.from_dict(LITE_USER_RAW)],
        params={"limit": 2, "before": "cursor"},
    ),
    EndpointSpec(
        method_name="get_market_comments",
        args=(),
        kwargs={
            "contractId": "market",
            "limit": 3,
            "page": 1,
            "userId": "uid",
            "order": "likes",
        },
        http_method="GET",
        path="/comments",
        response=[COMMENT_RAW],
        expected=[Comment.from_dict(COMMENT_RAW)],
        params={
            "contractId": "market",
            "limit": 3,
            "page": 1,
            "userId": "uid",
            "order": "likes",
        },
    ),
    EndpointSpec(
        method_name="create_multi_bet",
        args=("market", ("a1", "a2"), 100),
        kwargs={"limitProb": 0.7, "expiresAt": 10},
        http_method="POST",
        path="/multi-bet",
        response={"betId": "bet"},
        expected={"betId": "bet"},
        json_data={
            "contractId": "market",
            "answerIds": ["a1", "a2"],
            "amount": 100,
            "limitProb": 0.7,
            "expiresAt": 10,
        },
        auth=True,
    ),
    EndpointSpec(
        method_name="cancel_bet",
        args=("bet",),
        kwargs={},
        http_method="POST",
        path="/bet/cancel/bet",
        response={"status": "ok"},
        expected={"status": "ok"},
        auth=True,
    ),
    EndpointSpec(
        method_name="add_market_answer",
        args=("market", "answer"),
        kwargs={},
        http_method="POST",
        path="/market/market/answer",
        response={"newAnswerId": "ans"},
        expected={"newAnswerId": "ans"},
        json_data={"text": "answer"},
        auth=True,
    ),
    EndpointSpec(
        method_name="add_market_liquidity",
        args=("market", 50),
        kwargs={},
        http_method="POST",
        path="/market/market/add-liquidity",
        response={"liquidity": 50},
        expected={"liquidity": 50},
        json_data={"amount": 50},
        auth=True,
    ),
    EndpointSpec(
        method_name="add_market_bounty",
        args=("market", 25),
        kwargs={},
        http_method="POST",
        path="/market/market/add-bounty",
        response={"bounty": 25},
        expected={"bounty": 25},
        json_data={"amount": 25},
        auth=True,
    ),
    EndpointSpec(
        method_name="award_market_bounty",
        args=("market", 25, "comment"),
        kwargs={},
        http_method="POST",
        path="/market/market/award-bounty",
        response={"status": "ok"},
        expected={"status": "ok"},
        json_data={"amount": 25, "commentId": "comment"},
        auth=True,
    ),
    EndpointSpec(
        method_name="close_market_early",
        args=("market",),
        kwargs={"closeTime": 1},
        http_method="POST",
        path="/market/market/close",
        response={"closeTime": 1},
        expected={"closeTime": 1},
        json_data={"closeTime": 1},
        auth=True,
    ),
    EndpointSpec(
        method_name="update_market_group",
        args=("market", "group"),
        kwargs={"remove": True},
        http_method="POST",
        path="/market/market/group",
        response={"success": True},
        expected={"success": True},
        json_data={"groupId": "group", "remove": True},
        auth=True,
    ),
    EndpointSpec(
        method_name="sell_shares",
        args=("market", "YES"),
        kwargs={"shares": 5.0, "answerId": "answer"},
        http_method="POST",
        path="/market/market/sell",
        response={"betId": "bet"},
        expected={"betId": "bet"},
        json_data={"outcome": "YES", "shares": 5.0, "answerId": "answer"},
        auth=True,
    ),
    EndpointSpec(
        method_name="list_managrams",
        args=(),
        kwargs={"toId": "to", "fromId": "from", "limit": 5, "before": 10, "after": 1},
        http_method="GET",
        path="/managrams",
        response=[["txn"]],
        expected=[["txn"]],
        params={"toId": "to", "fromId": "from", "limit": 5, "before": 10, "after": 1},
    ),
    EndpointSpec(
        method_name="send_managram",
        args=(("user1", "user2"), 10),
        kwargs={"message": "hi"},
        http_method="POST",
        path="/managram",
        response={"status": "sent"},
        expected={"status": "sent"},
        json_data={"toIds": ["user1", "user2"], "amount": 10, "message": "hi"},
        auth=True,
    ),
    EndpointSpec(
        method_name="get_leagues",
        args=(),
        kwargs={"userId": "user", "season": 1, "cohort": "alpha"},
        http_method="GET",
        path="/leagues",
        response=[["league"]],
        expected=[["league"]],
        params={"userId": "user", "season": 1, "cohort": "alpha"},
    ),
)


@pytest.mark.parametrize("spec", ENDPOINT_SPECS)
def test_endpoint_wrappers(spec: EndpointSpec) -> None:
    """Ensure every wrapper issues the expected HTTP request and parses results."""

    client = ManifoldClient(api_key="key")
    mock = AsyncMock(return_value=spec.response)
    client._request_json = mock  # type: ignore[assignment]

    async def _call() -> Any:
        method = getattr(client, spec.method_name)
        return await method(*spec.args, **spec.kwargs)

    result = run_async(_call())

    assert result == spec.expected
    expected_kwargs: dict[str, Any] = {}
    if spec.params is not None:
        expected_kwargs["params"] = spec.params
    if spec.json_data is not None:
        expected_kwargs["json_data"] = spec.json_data
    if spec.auth:
        expected_kwargs["auth"] = True
    mock.assert_awaited_once_with(spec.http_method, spec.path, **expected_kwargs)


def test_get_market_probabilities_single_id_uses_single_endpoint() -> None:
    """A single identifier should fall back to the single-market endpoint."""

    client = ManifoldClient()
    single_prob = {"prob": 0.1}
    client.get_market_probability = AsyncMock(return_value=single_prob)  # type: ignore[assignment]
    client._request_json = AsyncMock()  # type: ignore[assignment]

    result = run_async(client.get_market_probabilities(["only"]))

    assert result == {"only": single_prob}
    client.get_market_probability.assert_awaited_once_with("only")
    client._request_json.assert_not_awaited()


def test_get_market_probabilities_requires_ids() -> None:
    """The batch endpoint must reject an empty request."""

    client = ManifoldClient()

    with pytest.raises(ValueError):
        run_async(client.get_market_probabilities(()))


def test_sell_shares_requires_outcome() -> None:
    """Selling shares should require an outcome label."""

    client = ManifoldClient()

    with pytest.raises(ValueError):
        run_async(client.sell_shares("market"))


def test_resolve_numeric_market_delegates_to_pseudo_numeric() -> None:
    """Numeric resolutions should reuse the pseudo-numeric logic."""

    client = ManifoldClient()
    pseudo_mock = AsyncMock(return_value={"status": "ok"})
    client.resolve_pseudo_numeric_market = pseudo_mock  # type: ignore[assignment]

    market = LiteMarket.from_dict(LITE_MARKET_RAW)
    result = run_async(client.resolve_numeric_market(market, 42.0))

    assert result == {"status": "ok"}
    pseudo_mock.assert_awaited_once_with(market, 42.0)
