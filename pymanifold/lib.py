"""Contains the client interface."""

from collections.abc import Iterable, Sequence
from types import TracebackType
from typing import Any, Literal, Optional, Union, cast, overload

import aiohttp
import gzip
import json

from .types import Bet, Comment, Group, JSONDict, LiteMarket, LiteUser, Market
from .utils.math import number_to_prob_cpmm1

BASE_URI = "https://manifold.markets/api/v0"


class ManifoldClient:
    """A client for interacting with the website manifold.markets."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """Initialize a Manifold client, optionally with an API key."""
        self.api_key = api_key
        self._session = session
        self._owns_session = session is None

    async def __aenter__(self) -> "ManifoldClient":
        """Create the internal session when used as an async context manager."""

        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Close the internal session when exiting a context manager."""

        await self.close()

    async def connect(self) -> None:
        """Ensure the HTTP session exists."""

        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close the HTTP session if it was created by the client."""

        if self._session is not None and self._owns_session:
            await self._session.close()
        self._session = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Return the currently active HTTP session."""

        if self._session is None:
            raise RuntimeError(
                "Client session is not initialized. Use 'async with' or call 'connect' before making requests."
            )
        return self._session

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[JSONDict] = None,
        auth: bool = False,
    ) -> Any:
        """Send an HTTP request and parse its JSON payload."""

        session = self._get_session()
        headers = self._auth_headers() if auth else None
        async with session.request(
            method=method,
            url=BASE_URI + path,
            params=params,
            json=json_data,
            headers=headers,
        ) as response:
            response.raise_for_status()
            body = await response.read()
            if not body:
                return None
            if body.startswith(b"\x1f\x8b"):
                body = gzip.decompress(body)
            encoding = response.get_encoding() or "utf-8"
            return json.loads(body.decode(encoding))

    async def list_markets(
        self,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        userId: Optional[str] = None,
        groupId: Optional[str] = None,
    ) -> list[LiteMarket]:
        """List markets with optional filtering."""

        markets = await self.get_markets(
            limit=limit,
            before=before,
            sort=sort,
            order=order,
            userId=userId,
            groupId=groupId,
        )
        return list(markets)

    async def get_markets(
        self,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        userId: Optional[str] = None,
        groupId: Optional[str] = None,
    ) -> Iterable[LiteMarket]:
        """Iterate over markets with optional filtering."""

        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if before is not None:
            params["before"] = before
        if sort is not None:
            params["sort"] = sort
        if order is not None:
            params["order"] = order
        if userId is not None:
            params["userId"] = userId
        if groupId is not None:
            params["groupId"] = groupId

        markets_raw = cast(
            list[JSONDict], await self._request_json("GET", "/markets", params=params)
        )
        return (LiteMarket.from_dict(market) for market in markets_raw)

    async def list_groups(
        self,
        availableToUserId: Optional[str] = None,
        beforeTime: Optional[int] = None,
    ) -> list[Group]:
        """List all groups."""

        groups = await self.get_groups(availableToUserId, beforeTime)
        return list(groups)

    async def get_groups(
        self,
        availableToUserId: Optional[str] = None,
        beforeTime: Optional[int] = None,
    ) -> Iterable[Group]:
        """Iterate over all groups."""

        params: dict[str, Any] = {}
        if availableToUserId is not None:
            params["availableToUserId"] = availableToUserId
        if beforeTime is not None:
            params["beforeTime"] = beforeTime
        groups_raw = cast(
            list[JSONDict], await self._request_json("GET", "/groups", params=params)
        )
        return (Group.from_dict(group) for group in groups_raw)

    async def get_group(
        self, slug: Optional[str] = None, id_: Optional[str] = None
    ) -> Group:
        """Iterate over all markets."""
        if id_ is not None:
            group_raw = await self._request_json("GET", "/group/by-id/" + id_)
        elif slug is not None:
            group_raw = await self._request_json("GET", "/group/" + slug)
        else:
            raise ValueError("Requires one or more of (slug, id_)")
        return Group.from_dict(cast(JSONDict, group_raw))

    async def list_bets(
        self,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        username: Optional[str] = None,
        market: Optional[str] = None,
        userId: Optional[str] = None,
        contractId: Optional[Union[str, Sequence[str]]] = None,
        contractSlug: Optional[str] = None,
        after: Optional[str] = None,
        beforeTime: Optional[int] = None,
        afterTime: Optional[int] = None,
        kinds: Optional[Union[str, Sequence[str]]] = None,
        order: Optional[str] = None,
    ) -> list[Bet]:
        """List bets with the available API filters."""

        bets = await self.get_bets(
            limit=limit,
            before=before,
            username=username,
            market=market,
            userId=userId,
            contractId=contractId,
            contractSlug=contractSlug,
            after=after,
            beforeTime=beforeTime,
            afterTime=afterTime,
            kinds=kinds,
            order=order,
        )
        return list(bets)

    async def get_bets(
        self,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        username: Optional[str] = None,
        market: Optional[str] = None,
        userId: Optional[str] = None,
        contractId: Optional[Union[str, Sequence[str]]] = None,
        contractSlug: Optional[str] = None,
        after: Optional[str] = None,
        beforeTime: Optional[int] = None,
        afterTime: Optional[int] = None,
        kinds: Optional[Union[str, Sequence[str]]] = None,
        order: Optional[str] = None,
    ) -> Iterable[Bet]:
        """Iterate over bets while exposing all documented filters."""

        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if before is not None:
            params["before"] = before
        if username is not None:
            params["username"] = username
        if userId is not None:
            params["userId"] = userId
        if contractSlug is not None:
            params["contractSlug"] = contractSlug
        if after is not None:
            params["after"] = after
        if beforeTime is not None:
            params["beforeTime"] = beforeTime
        if afterTime is not None:
            params["afterTime"] = afterTime
        if order is not None:
            params["order"] = order

        if contractId is not None:
            if isinstance(contractId, str):
                params["contractId"] = contractId
            else:
                params["contractId"] = list(contractId)
        elif market is not None:
            if isinstance(market, str):
                params["market"] = market
            else:
                params["market"] = list(market)

        if kinds is not None:
            if isinstance(kinds, str):
                params["kinds"] = kinds
            else:
                params["kinds"] = ",".join(kinds)

        bets_raw = cast(
            list[JSONDict], await self._request_json("GET", "/bets", params=params)
        )
        return (Bet.from_dict(market) for market in bets_raw)

    async def get_market_by_id(self, market_id: str) -> Market:
        """Get a market by id."""
        return Market.from_dict(await self._get_market_by_id_raw(market_id))

    async def _get_market_by_id_raw(self, market_id: str) -> JSONDict:
        """Get a market by id."""
        data = await self._request_json("GET", "/market/" + market_id)
        return cast(JSONDict, data)

    async def get_market_by_slug(self, slug: str) -> Market:
        """Get a market by slug."""
        return Market.from_dict(await self._get_market_by_slug_raw(slug))

    async def _get_market_by_slug_raw(self, slug: str) -> JSONDict:
        """Get a market by slug."""
        data = await self._request_json("GET", "/slug/" + slug)
        return cast(JSONDict, data)

    async def get_market_by_url(self, url: str) -> Market:
        """Get a market by url."""
        return Market.from_dict(await self._get_market_by_url_raw(url))

    async def _get_market_by_url_raw(self, url: str) -> JSONDict:
        """Get a market by url."""
        slug = url.split("/")[-1].split("#")[0]
        data = await self._request_json("GET", "/slug/" + slug)
        return cast(JSONDict, data)

    async def get_user(self, handle: str) -> LiteUser:
        """Get a user by handle."""
        return LiteUser.from_dict(await self._get_user_raw(handle))

    async def _get_user_raw(self, handle: str) -> JSONDict:
        data = await self._request_json("GET", "/user/" + handle)
        return cast(JSONDict, data)

    # FIXME: Add a DisplayUser dataclass for lite user responses.
    def get_user_lite(self, handle: str) -> Any:
        """Get basic public information for a user by username.

        Args:
            handle: The username to look up.

        Returns:
            Any: Placeholder for the DisplayUser payload.

        """
        raise NotImplementedError()

    def get_user_by_id(self, user_id: str) -> LiteUser:
        """Get a user by ID.

        Args:
            user_id: The unique identifier to fetch.

        Returns:
            LiteUser: Placeholder for the /v0/user/by-id response.

        """
        raise NotImplementedError()

    # FIXME: Add a DisplayUser dataclass for lite user responses.
    def get_user_by_id_lite(self, user_id: str) -> Any:
        """Get basic public information for a user by ID.

        Args:
            user_id: The user identifier to look up.

        Returns:
            Any: Placeholder for the DisplayUser payload.

        """
        raise NotImplementedError()

    def get_authenticated_user(self) -> LiteUser:
        """Return the authenticated user profile.

        Returns:
            LiteUser: Placeholder for the authenticated user payload.

        """
        raise NotImplementedError()

    def get_user_bets_deprecated(self, username: str) -> list[Bet]:
        """Get bets for a user via the deprecated /v0/user/[username]/bets endpoint.

        Args:
            username: The username whose bets should be retrieved.

        Returns:
            list[Bet]: Placeholder for the bet list returned by the legacy endpoint.

        """
        raise NotImplementedError()

    def get_user_portfolio(self, user_id: str) -> JSONDict:
        """Get live portfolio metrics for the given user.

        Args:
            user_id: The identifier of the user.

        Returns:
            JSONDict: Placeholder for the live portfolio metrics response.

        """
        raise NotImplementedError()

    def get_user_portfolio_history(self, user_id: str, period: str) -> list[JSONDict]:
        """Get historical portfolio metrics for the given user.

        Args:
            user_id: The identifier of the user.
            period: The history bucket to request.

        Returns:
            list[JSONDict]: Placeholder for the historical portfolio data.

        """
        raise NotImplementedError()

    def get_group_markets_by_id(self, group_id: str) -> list[LiteMarket]:
        """Get markets associated with a group via /v0/group/by-id/[id]/markets.

        Args:
            group_id: The group identifier from the API response.

        Returns:
            list[LiteMarket]: Placeholder for the group market list.

        """
        raise NotImplementedError()

    def search_markets(
        self,
        term: str,
        sort: Optional[str] = None,
        filter_: Optional[str] = None,
        contractType: Optional[str] = None,
        topicSlug: Optional[str] = None,
        creatorId: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        liquidity: Optional[float] = None,
    ) -> list[LiteMarket]:
        """Search or filter markets via GET /v0/search-markets.

        Args:
            term: The query string.
            sort: Optional sort mode.
            filter_: Optional closing-state filter.
            contractType: Optional contract type filter.
            topicSlug: Optional topic slug.
            creatorId: Optional creator identifier filter.
            limit: Optional maximum number of markets.
            offset: Optional offset for pagination.
            liquidity: Optional minimum liquidity threshold.

        Returns:
            list[LiteMarket]: Placeholder for the matching markets.

        """
        raise NotImplementedError()

    def get_market_probability(self, market_id: str) -> JSONDict:
        """Get cached probability data for a single market.

        Args:
            market_id: The market identifier.

        Returns:
            JSONDict: Placeholder for the probability payload.

        """
        raise NotImplementedError()

    def get_market_probabilities(self, market_ids: Sequence[str]) -> JSONDict:
        """Get cached probability data for multiple markets.

        Args:
            market_ids: The contract identifiers to query.

        Returns:
            JSONDict: Placeholder for the probability batch response.

        """
        raise NotImplementedError()

    def get_market_positions(
        self,
        market_id: str,
        order: Optional[str] = None,
        top: Optional[int] = None,
        bottom: Optional[int] = None,
        userId: Optional[str] = None,
        answerId: Optional[str] = None,
    ) -> list[JSONDict]:
        """Get position data for a market via GET /v0/market/[marketId]/positions.

        Args:
            market_id: The contract identifier.
            order: Optional ordering field.
            top: Optional number of top positions.
            bottom: Optional number of bottom positions.
            userId: Optional user identifier to filter for.
            answerId: Optional answer identifier for multi-choice markets.

        Returns:
            list[JSONDict]: Placeholder for the position summaries.

        """
        raise NotImplementedError()

    def get_user_contract_metrics_with_contracts(
        self,
        user_id: str,
        limit: int,
        offset: Optional[int] = None,
        order: Optional[str] = None,
        perAnswer: Optional[bool] = None,
    ) -> JSONDict:
        """Get a user's contract metrics bundled with market data.

        Args:
            user_id: The identifier of the user.
            limit: The number of markets to retrieve.
            offset: Optional pagination offset.
            order: Optional sort order.
            perAnswer: Whether to return per-answer metrics.

        Returns:
            JSONDict: Placeholder for the metrics-with-contracts payload.

        """
        raise NotImplementedError()

    def list_users(
        self, limit: Optional[int] = None, before: Optional[str] = None
    ) -> list[LiteUser]:
        """List users via GET /v0/users.

        Args:
            limit: Optional maximum number of users.
            before: Optional paging cursor.

        Returns:
            list[LiteUser]: Placeholder for the returned users.

        """
        raise NotImplementedError()

    def _auth_headers(self) -> dict[str, str]:
        if self.api_key:
            return {"Authorization": "Key " + self.api_key}
        else:
            raise RuntimeError("No API key provided")

    async def cancel_market(self, market: Union[LiteMarket, str]) -> JSONDict:
        """Cancel a market, resolving it N/A."""
        if isinstance(market, LiteMarket):
            marketId = market.id
        else:
            marketId = market
        data = await self._request_json(
            "POST",
            f"/market/{marketId}/resolve",
            json_data={"outcome": "CANCEL"},
            auth=True,
        )
        return cast(JSONDict, data)

    async def create_bet(
        self,
        contractId: str,
        amount: int,
        outcome: str,
        limitProb: Optional[float] = None,
        expiresAt: Optional[int] = None,
        expiresMillisAfter: Optional[int] = None,
        dryRun: Optional[bool] = None,
    ) -> str:
        """Place a bet.

        Returns the ID of the created bet.
        """
        json = {
            "amount": int(amount),
            "contractId": contractId,
            "outcome": outcome,
        }
        if limitProb is not None:
            json["limitProb"] = limitProb
        if expiresAt is not None:
            json["expiresAt"] = expiresAt
        if expiresMillisAfter is not None:
            json["expiresMillisAfter"] = expiresMillisAfter
        if dryRun is not None:
            json["dryRun"] = dryRun
        data = await self._request_json("POST", "/bet", json_data=json, auth=True)
        return cast(str, data["betId"])

    async def create_free_response_market(
        self,
        question: str,
        description: str,
        closeTime: int,
        tags: Optional[list[str]] = None,
    ) -> LiteMarket:
        """Create a free response market."""
        return await self._create_market(
            "FREE_RESPONSE", question, description, closeTime, tags
        )

    async def create_multiple_choice_market(
        self,
        question: str,
        description: str,
        closeTime: int,
        answers: list[str],
        tags: Optional[list[str]] = None,
    ) -> LiteMarket:
        """Create a free response market."""
        return await self._create_market(
            "MULTIPLE_CHOICE", question, description, closeTime, tags, answers=answers
        )

    async def create_numeric_market(
        self,
        question: str,
        description: str,
        closeTime: int,
        minValue: int,
        maxValue: int,
        isLogScale: bool,
        initialValue: Optional[float] = None,
        tags: Optional[list[str]] = None,
    ) -> LiteMarket:
        """Create a numeric market."""
        return await self._create_market(
            "PSEUDO_NUMERIC",
            question,
            description,
            closeTime,
            tags,
            minValue=minValue,
            maxValue=maxValue,
            isLogScale=isLogScale,
            initialValue=initialValue,
        )

    async def create_binary_market(
        self,
        question: str,
        description: str,
        closeTime: int,
        tags: Optional[list[str]] = None,
        initialProb: Optional[int] = 50,
    ) -> LiteMarket:
        """Create a binary market."""
        return await self._create_market(
            "BINARY", question, description, closeTime, tags, initialProb=initialProb
        )

    # TODO: Support the expanded POST /v0/market payload (visibility, groups, etc.).
    async def _create_market(
        self,
        outcomeType: str,
        question: str,
        description: str,
        closeTime: int,
        tags: Optional[list[str]] = None,
        initialProb: Optional[int] = 50,
        initialValue: Optional[float] = None,
        minValue: Optional[int] = None,
        maxValue: Optional[int] = None,
        isLogScale: Optional[bool] = None,
        answers: Optional[Sequence[str]] = None,
    ) -> LiteMarket:
        """Create a market."""
        data = {
            "outcomeType": outcomeType,
            "question": question,
            "description": description,
            "closeTime": closeTime,
            "tags": tags or [],
        }
        if outcomeType == "BINARY":
            data["initialProb"] = initialProb
        elif outcomeType == "FREE_RESPONSE":
            pass
        elif outcomeType == "PSEUDO_NUMERIC":
            data["min"] = minValue
            data["max"] = maxValue
            data["isLogScale"] = isLogScale
            if initialValue is None:
                raise ValueError("Needs initial value")
            data["initialValue"] = initialValue
        elif outcomeType == "MULTIPLE_CHOICE":
            data["answers"] = answers
        else:
            raise Exception(
                "Invalid outcome type. Outcome should be one of: BINARY, FREE_RESPONSE, PSEUDO_NUMERIC, MULTIPLE_CHOICE"
            )

        try:
            market_raw = cast(
                JSONDict,
                await self._request_json("POST", "/market", json_data=data, auth=True),
            )
        except aiohttp.ClientResponseError as error:
            if error.status >= 500:
                for mkt in await self.list_markets():
                    if (question, outcomeType, closeTime) == (
                        mkt.question,
                        mkt.outcomeType,
                        mkt.closeTime,
                    ):
                        return mkt
            raise
        return LiteMarket.from_dict(market_raw)

    async def resolve_market(
        self, market: Union[LiteMarket, str], *args: Any, **kwargs: Any
    ) -> JSONDict:
        """Resolve a market, with different inputs depending on its type."""
        if not isinstance(market, LiteMarket):
            market = await self.get_market_by_id(market)
        if market.outcomeType == "BINARY":
            return await self._resolve_binary_market(market, *args, **kwargs)
        elif market.outcomeType == "FREE_RESPONSE":
            return await self._resolve_free_response_market(market, *args, **kwargs)
        elif market.outcomeType == "MULTIPLE_CHOICE":
            return await self._resolve_multiple_choice_market(market, *args, **kwargs)
        elif market.outcomeType == "PSEUDO_NUMERIC":
            return await self._resolve_pseudo_numeric_market(market, *args, **kwargs)
        else:  # pragma: no cover
            raise NotImplementedError()

    async def _resolve_binary_market(
        self, market: LiteMarket, probabilityInt: float
    ) -> JSONDict:
        if probabilityInt == 100 or probabilityInt is True:
            json: dict[str, float | str] = {"outcome": "YES"}
        elif probabilityInt == 0 or probabilityInt is False:
            json = {"outcome": "NO"}
        else:
            json = {"outcome": "MKT", "probabilityInt": probabilityInt}

        data = await self._request_json(
            "POST",
            f"/market/{market.id}/resolve",
            json_data=json,
            auth=True,
        )
        return cast(JSONDict, data)

    async def _resolve_pseudo_numeric_market(
        self, market: LiteMarket, resolutionValue: float
    ) -> JSONDict:
        assert market.min is not None
        assert market.max is not None
        prob = 100 * number_to_prob_cpmm1(
            resolutionValue, market.min, market.max, bool(market.isLogScale)
        )
        json = {"outcome": "MKT", "value": resolutionValue, "probabilityInt": prob}
        data = await self._request_json(
            "POST",
            f"/market/{market.id}/resolve",
            json_data=json,
            auth=True,
        )
        return cast(JSONDict, data)

    async def _resolve_free_response_market(
        self, market: LiteMarket, weights: dict[int, float]
    ) -> JSONDict:
        if len(weights) == 1:
            json: JSONDict = {"outcome": next(iter(weights))}
        else:
            total = sum(weights.values())
            json = {
                "outcome": "MKT",
                "resolutions": [
                    {"answer": index, "pct": 100 * weight / total}
                    for index, weight in weights.items()
                ],
            }
        data = await self._request_json(
            "POST",
            f"/market/{market.id}/resolve",
            json_data=json,
            auth=True,
        )
        return cast(JSONDict, data)

    _resolve_multiple_choice_market = _resolve_free_response_market

    async def _resolve_numeric_market(
        self, market: LiteMarket, number: float
    ) -> JSONDict:
        raise NotImplementedError("TODO: I suspect the relevant docs are out of date")

    def get_market_comments(
        self,
        contractId: Optional[str] = None,
        contractSlug: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        userId: Optional[str] = None,
        order: Optional[str] = None,
    ) -> list[Comment]:
        """Get comments via GET /v0/comments.

        Args:
            contractId: Optional market identifier to filter by.
            contractSlug: Optional market slug to filter by.
            limit: Optional maximum number of comments.
            page: Optional pagination page.
            userId: Optional user identifier to filter by.
            order: Optional order specifier.

        Returns:
            list[Comment]: Placeholder for the comment list.

        """
        raise NotImplementedError()

    def create_multi_bet(
        self,
        contractId: str,
        answerIds: Sequence[str],
        amount: int,
        limitProb: Optional[float] = None,
        expiresAt: Optional[int] = None,
    ) -> JSONDict:
        """Place a multi-answer bet via POST /v0/multi-bet.

        Args:
            contractId: The market to bet on.
            answerIds: The answers to buy shares in.
            amount: The mana amount to spend.
            limitProb: Optional limit probability.
            expiresAt: Optional cancellation timestamp.

        Returns:
            JSONDict: Placeholder for the created order payload.

        """
        raise NotImplementedError()

    def cancel_bet(self, bet_id: str) -> JSONDict:
        """Cancel a limit order via POST /v0/bet/cancel/[id].

        Args:
            bet_id: The identifier of the bet to cancel.

        Returns:
            JSONDict: Placeholder for the cancellation response.

        """
        raise NotImplementedError()

    def add_market_answer(self, market_id: str, text: str) -> JSONDict:
        """Add an answer to a market via POST /v0/market/[marketId]/answer.

        Args:
            market_id: The contract receiving a new answer.
            text: The answer text.

        Returns:
            JSONDict: Placeholder for the new answer payload.

        """
        raise NotImplementedError()

    def add_market_liquidity(self, market_id: str, amount: int) -> JSONDict:
        """Add liquidity via POST /v0/market/[marketId]/add-liquidity.

        Args:
            market_id: The contract identifier.
            amount: The mana amount to add.

        Returns:
            JSONDict: Placeholder for the liquidity transaction.

        """
        raise NotImplementedError()

    def add_market_bounty(self, market_id: str, amount: int) -> JSONDict:
        """Add bounty funds via POST /v0/market/[marketId]/add-bounty.

        Args:
            market_id: The bounty market identifier.
            amount: The additional bounty amount.

        Returns:
            JSONDict: Placeholder for the bounty transaction.

        """
        raise NotImplementedError()

    def award_market_bounty(
        self, market_id: str, amount: int, commentId: str
    ) -> JSONDict:
        """Award a bounty via POST /v0/market/[marketId]/award-bounty.

        Args:
            market_id: The market identifier.
            amount: The bounty payout amount.
            commentId: The comment receiving the reward.

        Returns:
            JSONDict: Placeholder for the resulting transaction.

        """
        raise NotImplementedError()

    def close_market_early(
        self, market_id: str, closeTime: Optional[int] = None
    ) -> JSONDict:
        """Close a market via POST /v0/market/[marketId]/close.

        Args:
            market_id: The market identifier.
            closeTime: Optional timestamp at which to close.

        Returns:
            JSONDict: Placeholder for the closure payload.

        """
        raise NotImplementedError()

    def update_market_group(
        self, market_id: str, groupId: str, remove: bool = False
    ) -> JSONDict:
        """Add or remove a group tag via POST /v0/market/[marketId]/group.

        Args:
            market_id: The market identifier.
            groupId: The group identifier to toggle.
            remove: Whether to remove the group assignment.

        Returns:
            JSONDict: Placeholder for the updated group assignment.

        """
        raise NotImplementedError()

    def sell_shares(
        self,
        market_id: str,
        outcome: Optional[str] = None,
        shares: Optional[float] = None,
        answerId: Optional[str] = None,
    ) -> JSONDict:
        """Sell shares via POST /v0/market/[marketId]/sell.

        Args:
            market_id: The market identifier.
            outcome: Optional outcome label to sell.
            shares: Optional share count.
            answerId: Optional answer identifier for multi-choice markets.

        Returns:
            JSONDict: Placeholder for the resulting transaction.

        """
        raise NotImplementedError()

    def list_managrams(
        self,
        toId: Optional[str] = None,
        fromId: Optional[str] = None,
        limit: Optional[int] = None,
        before: Optional[int] = None,
        after: Optional[int] = None,
    ) -> list[JSONDict]:
        """List managrams via GET /v0/managrams.

        Args:
            toId: Optional recipient identifier filter.
            fromId: Optional sender identifier filter.
            limit: Optional maximum number of rows.
            before: Optional createdTime upper bound.
            after: Optional createdTime lower bound.

        Returns:
            list[JSONDict]: Placeholder for the managram list.

        """
        raise NotImplementedError()

    def send_managram(
        self, toIds: Sequence[str], amount: int, message: Optional[str] = None
    ) -> JSONDict:
        """Send a managram via POST /v0/managram.

        Args:
            toIds: The recipient identifiers.
            amount: The mana amount to send to each user.
            message: Optional note to attach.

        Returns:
            JSONDict: Placeholder for the transaction payload.

        """
        raise NotImplementedError()

    def get_leagues(
        self,
        userId: Optional[str] = None,
        season: Optional[int] = None,
        cohort: Optional[str] = None,
    ) -> list[JSONDict]:
        """Get league standings via GET /v0/leagues.

        Args:
            userId: Optional identifier to filter by user.
            season: Optional season identifier.
            cohort: Optional cohort slug.

        Returns:
            list[JSONDict]: Placeholder for the league standings.

        """
        raise NotImplementedError()

    @overload
    def create_comment(
        self, market: LiteMarket | str, comment: str, mode: Literal["markdown", "html"]
    ) -> JSONDict: ...

    @overload
    def create_comment(
        self, market: LiteMarket | str, comment: JSONDict, mode: Literal["tiptap"]
    ) -> JSONDict: ...

    async def create_comment(
        self, market: LiteMarket | str, comment: str | JSONDict, mode: str
    ) -> JSONDict:
        """Create a comment on a given market, using Markdown, HTML, or TipTap formatting."""
        if isinstance(market, LiteMarket):
            market = market.id
        data: JSONDict = {"contractId": market}
        if mode == "tiptap":
            data["content"] = comment
        elif mode == "html":
            data["html"] = comment
        elif mode == "markdown":
            data["markdown"] = comment
        else:
            raise ValueError("Invalid format mode")
        response = await self._request_json(
            "POST", "/comment", json_data=data, auth=True
        )
        return cast(JSONDict, response)
