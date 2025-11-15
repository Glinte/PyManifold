"""Contains the client interface."""

from collections.abc import Iterable, Sequence
from typing import Any, Dict, Literal, Optional, Union, cast, overload

import requests

from .types import Bet, Comment, Group, JSONDict, LiteMarket, LiteUser, Market
from .utils.math import number_to_prob_cpmm1

BASE_URI = "https://api.manifold.markets/v0"


class ManifoldClient:
    """A client for interacting with the website manifold.markets."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize a Manifold client, optionally with an API key."""
        self.api_key = api_key

    def list_markets(
        self,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        userId: Optional[str] = None,
        groupId: Optional[str] = None,
    ) -> list[LiteMarket]:
        """List markets with optional filtering."""

        return list(
            self.get_markets(
                limit=limit,
                before=before,
                sort=sort,
                order=order,
                userId=userId,
                groupId=groupId,
            )
        )

    def get_markets(
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

        response = requests.get(url=BASE_URI + "/markets", params=params)
        return (LiteMarket.from_dict(market) for market in response.json())

    def list_groups(
        self,
        availableToUserId: Optional[str] = None,
        beforeTime: Optional[int] = None,
    ) -> list[Group]:
        """List all groups."""

        return list(self.get_groups(availableToUserId, beforeTime))

    def get_groups(
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
        response = requests.get(url=BASE_URI + "/groups", params=params)
        return (Group.from_dict(group) for group in response.json())

    def get_group(self, slug: Optional[str] = None, id_: Optional[str] = None) -> Group:
        """Iterate over all markets."""
        if id_ is not None:
            response = requests.get(url=BASE_URI + "/group/by-id/" + id_)
        elif slug is not None:
            response = requests.get(url=BASE_URI + "/group/" + slug)
        else:
            raise ValueError("Requires one or more of (slug, id_)")
        return Group.from_dict(response.json())

    def list_bets(
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

        return list(
            self.get_bets(
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
        )

    def get_bets(
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

        contract_param: Optional[Union[str, Sequence[str]]] = contractId
        if contract_param is None and market is not None:
            contract_param = market
        if contract_param is not None:
            if isinstance(contract_param, str):
                params["contractId"] = contract_param
            else:
                params["contractId"] = list(contract_param)

        if kinds is not None:
            if isinstance(kinds, str):
                params["kinds"] = kinds
            else:
                params["kinds"] = ",".join(kinds)

        response = requests.get(url=BASE_URI + "/bets", params=params)
        return (Bet.from_dict(market) for market in response.json())

    def get_market_by_id(self, market_id: str) -> Market:
        """Get a market by id."""
        return Market.from_dict(self._get_market_by_id_raw(market_id))

    def _get_market_by_id_raw(self, market_id: str) -> JSONDict:
        """Get a market by id."""
        response = requests.get(url=BASE_URI + "/market/" + market_id)
        return cast(JSONDict, response.json())

    def get_market_by_slug(self, slug: str) -> Market:
        """Get a market by slug."""
        return Market.from_dict(self._get_market_by_slug_raw(slug))

    def _get_market_by_slug_raw(self, slug: str) -> JSONDict:
        """Get a market by slug."""
        response = requests.get(url=BASE_URI + "/slug/" + slug)
        return cast(JSONDict, response.json())

    def get_market_by_url(self, url: str) -> Market:
        """Get a market by url."""
        return Market.from_dict(self._get_market_by_url_raw(url))

    def _get_market_by_url_raw(self, url: str) -> JSONDict:
        """Get a market by url."""
        slug = url.split("/")[-1].split("#")[0]
        response = requests.get(url=BASE_URI + "/slug/" + slug)
        return cast(JSONDict, response.json())

    def get_user(self, handle: str) -> LiteUser:
        """Get a user by handle."""
        return LiteUser.from_dict(self._get_user_raw(handle))

    def _get_user_raw(self, handle: str) -> JSONDict:
        response = requests.get(url=BASE_URI + "/user/" + handle)
        return cast(JSONDict, response.json())

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

    def cancel_market(self, market: Union[LiteMarket, str]) -> requests.Response:
        """Cancel a market, resolving it N/A."""
        if isinstance(market, LiteMarket):
            marketId = market.id
        else:
            marketId = market
        response = requests.post(
            url=BASE_URI + "/market/" + marketId + "/resolve",
            json={
                "outcome": "CANCEL",
            },
            headers=self._auth_headers(),
        )
        response.raise_for_status()
        return response

    def create_bet(
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
        response = requests.post(
            url=BASE_URI + "/bet",
            json=json,
            headers=self._auth_headers(),
        )
        response.raise_for_status()
        return cast(str, response.json()["betId"])

    def create_free_response_market(
        self,
        question: str,
        description: str,
        closeTime: int,
        tags: Optional[list[str]] = None,
    ) -> LiteMarket:
        """Create a free response market."""
        return self._create_market(
            "FREE_RESPONSE", question, description, closeTime, tags
        )

    def create_multiple_choice_market(
        self,
        question: str,
        description: str,
        closeTime: int,
        answers: list[str],
        tags: Optional[list[str]] = None,
    ) -> LiteMarket:
        """Create a free response market."""
        return self._create_market(
            "MULTIPLE_CHOICE", question, description, closeTime, tags, answers=answers
        )

    def create_numeric_market(
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
        return self._create_market(
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

    def create_binary_market(
        self,
        question: str,
        description: str,
        closeTime: int,
        tags: Optional[list[str]] = None,
        initialProb: Optional[int] = 50,
    ) -> LiteMarket:
        """Create a binary market."""
        return self._create_market(
            "BINARY", question, description, closeTime, tags, initialProb=initialProb
        )

    # TODO: Support the expanded POST /v0/market payload (visibility, groups, etc.).
    def _create_market(
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

        response = requests.post(
            url=BASE_URI + "/market",
            json=data,
            headers=self._auth_headers(),
        )
        if response.status_code in range(400, 500):
            response.raise_for_status()
        elif response.status_code >= 500:
            # Sometimes when there is a serverside error the market is still posted
            # We want to make sure we still return it in those instances
            for mkt in self.list_markets():
                if (question, outcomeType, closeTime) == (
                    mkt.question,
                    mkt.outcomeType,
                    mkt.closeTime,
                ):
                    return mkt
        return LiteMarket.from_dict(response.json())

    def resolve_market(
        self, market: Union[LiteMarket, str], *args: Any, **kwargs: Any
    ) -> requests.Response:
        """Resolve a market, with different inputs depending on its type."""
        if not isinstance(market, LiteMarket):
            market = self.get_market_by_id(market)
        if market.outcomeType == "BINARY":
            return self._resolve_binary_market(market, *args, **kwargs)
        elif market.outcomeType == "FREE_RESPONSE":
            return self._resolve_free_response_market(market, *args, **kwargs)
        elif market.outcomeType == "MULTIPLE_CHOICE":
            return self._resolve_multiple_choice_market(market, *args, **kwargs)
        elif market.outcomeType == "PSEUDO_NUMERIC":
            return self._resolve_pseudo_numeric_market(market, *args, **kwargs)
        else:  # pragma: no cover
            raise NotImplementedError()

    def _resolve_binary_market(
        self, market: LiteMarket, probabilityInt: float
    ) -> requests.Response:
        if probabilityInt == 100 or probabilityInt is True:
            json: Dict[str, Union[float, str]] = {"outcome": "YES"}
        elif probabilityInt == 0 or probabilityInt is False:
            json = {"outcome": "NO"}
        else:
            json = {"outcome": "MKT", "probabilityInt": probabilityInt}

        response = requests.post(
            url=BASE_URI + "/market/" + market.id + "/resolve",
            json=json,
            headers=self._auth_headers(),
        )
        response.raise_for_status()
        return response

    def _resolve_pseudo_numeric_market(
        self, market: LiteMarket, resolutionValue: float
    ) -> requests.Response:
        assert market.min is not None
        assert market.max is not None
        prob = 100 * number_to_prob_cpmm1(
            resolutionValue, market.min, market.max, bool(market.isLogScale)
        )
        json = {"outcome": "MKT", "value": resolutionValue, "probabilityInt": prob}
        response = requests.post(
            url=BASE_URI + "/market/" + market.id + "/resolve",
            json=json,
            headers=self._auth_headers(),
        )
        response.raise_for_status()
        return response

    def _resolve_free_response_market(
        self, market: LiteMarket, weights: Dict[int, float]
    ) -> requests.Response:
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
        response = requests.post(
            url=BASE_URI + "/market/" + market.id + "/resolve",
            json=json,
            headers=self._auth_headers(),
        )
        response.raise_for_status()
        return response

    _resolve_multiple_choice_market = _resolve_free_response_market

    def _resolve_numeric_market(
        self, market: LiteMarket, number: float
    ) -> requests.Response:
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

    def cancel_bet(self, bet_id: str) -> requests.Response:
        """Cancel a limit order via POST /v0/bet/cancel/[id].

        Args:
            bet_id: The identifier of the bet to cancel.

        Returns:
            requests.Response: Placeholder for the cancellation response.

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
    ) -> requests.Response: ...

    @overload
    def create_comment(
        self, market: LiteMarket | str, comment: JSONDict, mode: Literal["tiptap"]
    ) -> requests.Response: ...

    def create_comment(
        self, market: LiteMarket | str, comment: str | JSONDict, mode: str
    ) -> requests.Response:
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
        response = requests.post(
            url=BASE_URI + "/comment",
            json=data,
            headers=self._auth_headers(),
        )
        response.raise_for_status()
        return response
