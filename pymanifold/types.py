"""Contains the various types of data that Manifold can return."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from inspect import signature
from typing import TYPE_CHECKING, Literal, Type, TypeVar, cast

if TYPE_CHECKING:  # pragma: no cover
    from .lib import ManifoldClient

T = TypeVar("T", bound="DictDeserializable")

JSONType = (
    int | float | bool | str | None | Sequence["JSONType"] | Mapping[str, "JSONType"]
)
JSONDict = dict[str, JSONType]
JSONContent = JSONDict
Answer = dict[str, JSONType]
Number = float | int


class DictDeserializable:
    """An object which can be deserialized from a known dictionary spec."""

    @classmethod
    def from_dict(cls: Type[T], env: JSONDict) -> T:
        """Take a dictionary and return an instance of the associated class.

        Args:
            env: Dictionary representation of the object.

        Returns:
            An instance of the class built from the dictionary.
        """
        allowed_keys = signature(cls).parameters
        filtered_env = {key: value for key, value in env.items() if key in allowed_keys}
        return cls(**filtered_env)  # type: ignore[arg-type]


@dataclass
class Bet(DictDeserializable):
    """Represents a bet.

    Attributes:
        amount: Amount of mana placed on the bet.
        contractId: Identifier of the market that the bet belongs to.
        createdTime: Millisecond timestamp describing when the bet was created.
        id: Unique identifier of the bet.
        loanAmount: Amount of the bet that was funded via a loan, if any.
        userId: Identifier of the user that placed the bet.
        userAvatarUrl: Avatar of the bettor.
        userUsername: Username of the bettor.
        userName: Display name of the bettor.
        orderAmount: Limit order amount if the bet was placed as an order.
        isCancelled: Whether the bet was cancelled before being filled.
        isFilled: Whether the bet was filled.
        fills: Details about partial fills.
        fees: Breakdown of fees collected for the bet.
        probBefore: Market probability before the bet was placed.
        probAfter: Market probability after the bet was placed.
    """

    amount: int
    """Amount of mana placed on the bet."""

    contractId: str
    """Identifier of the market that the bet belongs to."""

    createdTime: int
    """Millisecond timestamp describing when the bet was created."""

    id: str
    """Unique identifier of the bet."""

    loanAmount: int | None = None
    """Amount of the bet that was funded via a loan."""

    userId: str | None = None
    """Identifier of the user that placed the bet."""

    userAvatarUrl: str | None = None
    """Avatar URL of the bettor."""

    userUsername: str | None = None
    """Username of the bettor."""

    userName: str | None = None
    """Display name of the bettor."""

    orderAmount: int | None = None
    """Limit order amount if the bet was placed as an order."""

    isCancelled: bool = False
    """Whether the bet was cancelled before being filled."""

    isFilled: bool = True
    """Whether the bet was filled."""

    fills: list[dict[str, float | str | None]] | None = None
    """Details describing how the bet was filled."""

    fees: dict[str, float] | None = None
    """Breakdown of fees collected for the bet."""

    probBefore: float | None = None
    """Market probability before the bet was placed."""

    probAfter: float | None = None
    """Market probability after the bet was placed."""


@dataclass
class Comment(DictDeserializable):
    """Represents a comment on a market.

    Attributes:
        contractId: Identifier of the market that the comment belongs to.
        createdTime: Millisecond timestamp describing when the comment was created.
        id: Unique identifier of the comment.
        text: Body of the comment as plaintext.
        userId: Identifier of the author.
        userName: Display name of the author.
        userAvatarUrl: Avatar of the author.
        userUsername: Username of the author.
    """

    contractId: str
    """Identifier of the market that the comment belongs to."""

    createdTime: int
    """Millisecond timestamp describing when the comment was created."""

    id: str
    """Unique identifier of the comment."""

    text: str = ""
    """Body of the comment as plaintext."""

    userId: str = ""
    """Identifier of the author."""

    userName: str = ""
    """Display name of the author."""

    userAvatarUrl: str = ""
    """Avatar URL of the author."""

    userUsername: str = ""
    """Username of the author."""


@dataclass
class User(DictDeserializable):
    """Basic information about a user.

    Attributes:
        id: Unique identifier of the user.
        createdTime: Millisecond timestamp describing when the user joined.
        name: Display name of the user.
        username: Username used in URLs.
        url: Profile URL for the user.
        avatarUrl: Avatar of the user.
        bio: Short bio written by the user.
        bannerUrl: Header image for the user's profile.
        website: Personal website link.
        twitterHandle: Twitter handle for the user.
        discordHandle: Discord handle for the user.
        isBot: Whether the account is a bot.
        isAdmin: Whether the user is part of the Manifold team.
        isTrustworthy: Whether the user is a moderator.
        isBannedFromPosting: Whether the user is prevented from posting.
        userDeleted: Whether the user deleted their account.
        balance: Mana balance for the account.
        totalDeposits: Total lifetime deposits.
        lastBetTime: Millisecond timestamp of the last bet.
        currentBettingStreak: Length of the current betting streak.
    """

    id: str
    """Unique identifier of the user."""

    createdTime: int
    """Millisecond timestamp describing when the user joined."""

    name: str
    """Display name of the user."""

    username: str
    """Username used in URLs."""

    url: str
    """Profile URL for the user."""

    avatarUrl: str | None = None
    """Avatar of the user."""

    bio: str | None = None
    """Short bio written by the user."""

    bannerUrl: str | None = None
    """Header image for the user's profile."""

    website: str | None = None
    """Personal website link."""

    twitterHandle: str | None = None
    """Twitter handle for the user."""

    discordHandle: str | None = None
    """Discord handle for the user."""

    isBot: bool | None = None
    """Whether the account is a bot."""

    isAdmin: bool | None = None
    """Whether the user is part of the Manifold team."""

    isTrustworthy: bool | None = None
    """Whether the user is a moderator."""

    isBannedFromPosting: bool | None = None
    """Whether the user is prevented from posting."""

    userDeleted: bool | None = None
    """Whether the user deleted their account."""

    balance: float = 0.0
    """Mana balance for the account."""

    totalDeposits: float = 0.0
    """Total lifetime deposits."""

    lastBetTime: int | None = None
    """Millisecond timestamp of the last bet."""

    currentBettingStreak: int | None = None
    """Length of the current betting streak."""


LiteUser = User


@dataclass
class LiteMarket(DictDeserializable):
    """Represents information about a market without comments or bets.

    Attributes:
        id: Unique identifier of the market.
        creatorId: Identifier of the market creator.
        creatorUsername: Username of the creator.
        creatorName: Display name of the creator.
        creatorAvatarUrl: Avatar of the creator.
        createdTime: Millisecond timestamp describing when the market was created.
        closeTime: Desired close time for the market.
        question: Question that the market asks.
        url: Public URL for the market.
        outcomeType: Outcome type for the market.
        mechanism: Mechanism used by the market.
        probability: Current probability for binary markets.
        pool: Mapping of outcomes to shares invested.
        p: CPMM probability constant for cpmm-1 markets.
        totalLiquidity: Total amount of mana deposited into the liquidity pool.
        value: Value mapped from probability for pseudo-numeric markets.
        min: Minimum resolvable value for pseudo-numeric markets.
        max: Maximum resolvable value for pseudo-numeric markets.
        isLogScale: Whether the pseudo-numeric market uses log scaling.
        volume: Lifetime trade volume for the market.
        volume24Hours: Volume in the last 24 hours.
        volume7Days: Volume in the last 7 days.
        isResolved: Whether the market has resolved.
        resolutionTime: Millisecond timestamp describing when the market resolved.
        resolution: Resolution outcome if resolved.
        resolutionProbability: Probability assigned when resolving to MKT.
        uniqueBettorCount: Unique bettors who have participated.
        lastUpdatedTime: Time when the market was last updated.
        lastBetTime: Time when the most recent bet occurred.
        token: Currency used by the market.
        siblingContractId: Identifier of the paired market when toggling currencies.
        tags: Tags applied to the market.
    """

    id: str
    """Unique identifier of the market."""

    creatorId: str
    """Identifier of the market creator."""

    creatorUsername: str
    """Username of the creator."""

    creatorName: str
    """Display name of the creator."""

    creatorAvatarUrl: str | None = None
    """Avatar of the creator."""

    createdTime: int = 0
    """Millisecond timestamp describing when the market was created."""

    closeTime: int | None = None
    """Desired close time for the market."""

    question: str = ""
    """Question that the market asks."""

    url: str = ""
    """Public URL for the market."""

    outcomeType: str = ""
    """Outcome type for the market."""

    mechanism: str = ""
    """Mechanism used by the market."""

    probability: float = 0.0
    """Current probability for binary markets."""

    pool: dict[str, Number] | Number | None = None
    """Mapping of outcomes to shares invested, a numeric pool value, or None."""

    p: float | None = None
    """CPMM probability constant for cpmm-1 markets."""

    totalLiquidity: float | None = None
    """Total amount of mana deposited into the liquidity pool."""

    value: float | None = None
    """Value mapped from probability for pseudo-numeric markets."""

    min: float | None = None
    """Minimum resolvable value for pseudo-numeric markets."""

    max: float | None = None
    """Maximum resolvable value for pseudo-numeric markets."""

    isLogScale: bool | None = None
    """Whether the pseudo-numeric market uses log scaling."""

    volume: float = 0.0
    """Lifetime trade volume for the market."""

    volume24Hours: float = 0.0
    """Volume in the last 24 hours."""

    volume7Days: float = 0.0
    """Volume in the last seven days."""

    isResolved: bool = False
    """Whether the market has resolved."""

    resolutionTime: int | None = None
    """Millisecond timestamp describing when the market resolved."""

    resolution: str | None = None
    """Resolution outcome if resolved."""

    resolutionProbability: float | None = None
    """Probability assigned when resolving to MKT."""

    uniqueBettorCount: int = 0
    """Unique bettors who have participated."""

    lastUpdatedTime: int | None = None
    """Time when the market was last updated."""

    lastBetTime: int | None = None
    """Time when the most recent bet occurred."""

    token: Literal["MANA", "CASH"] | None = None
    """Currency used by the market."""

    siblingContractId: str | None = None
    """Identifier of the paired market when toggling currencies."""

    tags: list[str] = field(default_factory=list)
    """Tags applied to the market."""

    @classmethod
    def from_dict(cls, env: JSONDict) -> "LiteMarket":
        """Take a dictionary and return an instance of the associated class.

        Args:
            env: Dictionary representation of the market.

        Returns:
            LiteMarket constructed from the provided dictionary.
        """

        data = dict(env)
        data.setdefault("creatorId", "")
        data.setdefault("url", data.get("url", ""))
        return super().from_dict(data)

    @property
    def slug(self) -> str:
        """Generate the slug of a market, given it has an assigned URL."""

        if not self.url:
            raise ValueError("No url set")
        return self.url.split("/")[-1].split("#")[0]


@dataclass
class Market(LiteMarket):
    """Represents a complete market, including bets and comments.

    Attributes:
        bets: List of bets for the market.
        comments: List of comments for the market.
        answers: Answers for multi-answer markets.
        shouldAnswersSumToOne: Whether answers are dependent and should sum to 100%.
        addAnswersMode: Who may add answers to the market.
        options: Poll options and vote counts.
        totalBounty: Total bounty amount for bounty markets.
        bountyLeft: Remaining bounty amount.
        description: Rich text description for the market.
        textDescription: Plain text description.
        coverImageUrl: Optional cover image for the market.
        groupSlugs: Topic tags for the market.
    """

    bets: list[Bet] = field(default_factory=list)
    """List of bets for the market."""

    comments: list[Comment] = field(default_factory=list)
    """List of comments for the market."""

    answers: list[Answer] | None = None
    """Answers for multi-answer markets."""

    shouldAnswersSumToOne: bool | None = None
    """Whether answers are dependent and should sum to 100%."""

    addAnswersMode: Literal["ANYONE", "ONLY_CREATOR", "DISABLED"] | None = None
    """Who may add answers to the market."""

    options: list[dict[str, str | Number]] = field(default_factory=list)
    """Poll options and vote counts."""

    totalBounty: float | None = None
    """Total bounty amount for bounty markets."""

    bountyLeft: float | None = None
    """Remaining bounty amount."""

    description: JSONContent | str = field(default_factory=dict)
    """Rich text description for the market."""

    textDescription: str = ""
    """Plain text description of the market."""

    coverImageUrl: str | None = None
    """Optional cover image for the market."""

    groupSlugs: list[str] = field(default_factory=list)
    """Topic tags applied to the market."""

    @classmethod
    def from_dict(cls, env: JSONDict) -> "Market":
        """Take a dictionary and return an instance of the associated class.

        Args:
            env: Dictionary representation of the market.

        Returns:
            Market constructed from the provided dictionary.
        """
        market = super().from_dict(env)
        bet_dicts = env.get("bets", [])
        comment_dicts = env.get("comments", [])
        if isinstance(bet_dicts, Sequence):
            market.bets = [
                Bet.from_dict(cast(JSONDict, dict(bet)))
                for bet in bet_dicts
                if isinstance(bet, Mapping)
            ]
        if isinstance(comment_dicts, Sequence):
            market.comments = [
                Comment.from_dict(cast(JSONDict, dict(comment)))
                for comment in comment_dicts
                if isinstance(comment, Mapping)
            ]
        return market


@dataclass
class Group(DictDeserializable):
    """Represents a group of related markets.

    Attributes:
        name: Display name of the group.
        creatorId: Identifier of the user that created the group.
        id: Unique identifier of the group.
        contractIds: Identifiers of the contracts that belong to the group.
        mostRecentActivityTime: Timestamp of the most recent activity.
        anyoneCanJoin: Whether anyone can join the group.
        mostRecentContractAddedTime: Timestamp of the most recent contract addition.
        createdTime: Timestamp describing when the group was created.
        memberIds: Identifiers of the users in the group.
        slug: Slug that identifies the group in URLs.
        about: Description of the group.
    """

    name: str = ""
    """Display name of the group."""

    creatorId: str = ""
    """Identifier of the user that created the group."""

    id: str = ""
    """Unique identifier of the group."""

    contractIds: list[str] = field(default_factory=list)
    """Identifiers of the contracts that belong to the group."""

    mostRecentActivityTime: int = -1
    """Timestamp of the most recent activity."""

    anyoneCanJoin: bool = False
    """Whether anyone can join the group."""

    mostRecentContractAddedTime: int = -1
    """Timestamp of the most recent contract addition."""

    createdTime: int = -1
    """Timestamp describing when the group was created."""

    memberIds: list[str] = field(default_factory=list)
    """Identifiers of the users in the group."""

    slug: str = ""
    """Slug that identifies the group in URLs."""

    about: str = ""
    """Description of the group."""

    def contracts(self, client: "ManifoldClient") -> Iterable["Market"]:
        """Iterate over the markets in this group.

        Args:
            client: Client used to fetch the markets.

        Returns:
            Iterable over the group's markets.
        """

        return (client.get_market_by_id(id_) for id_ in self.contractIds)

    def members(self, client: "ManifoldClient") -> Iterable["User"]:
        """Iterate over the members in this group.

        Args:
            client: Client used to fetch members.

        Returns:
            Iterable over the group's members.
        """

        return (client.get_user(id_) for id_ in self.memberIds)


@dataclass
class PortfolioMetrics(DictDeserializable):
    """Represents the portfolio metrics for a user.

    Attributes:
        investmentValue: Current investment value.
        cashInvestmentValue: Value of cash investments.
        balance: Mana balance.
        cashBalance: Cash balance.
        spiceBalance: Spice balance.
        totalDeposits: Total lifetime deposits.
        totalCashDeposits: Total lifetime cash deposits.
        loanTotal: Outstanding loan balance.
        timestamp: Millisecond timestamp describing when the snapshot was taken.
        profit: Total profit at the snapshot.
        userId: Identifier of the user that owns the portfolio.
    """

    investmentValue: float = 0.0
    """Current investment value."""

    cashInvestmentValue: float = 0.0
    """Value of cash investments."""

    balance: float = 0.0
    """Mana balance."""

    cashBalance: float = 0.0
    """Cash balance."""

    spiceBalance: float = 0.0
    """Spice balance."""

    totalDeposits: float = 0.0
    """Total lifetime deposits."""

    totalCashDeposits: float = 0.0
    """Total lifetime cash deposits."""

    loanTotal: float = 0.0
    """Outstanding loan balance."""

    timestamp: int = 0
    """Millisecond timestamp describing when the snapshot was taken."""

    profit: float | None = None
    """Total profit at the snapshot."""

    userId: str = ""
    """Identifier of the user that owns the portfolio."""


@dataclass
class LivePortfolioMetrics(PortfolioMetrics):
    """Represents live portfolio metrics updated with daily profit.

    Attributes:
        dailyProfit: Profit accrued during the current day.
    """

    dailyProfit: float = 0.0
    """Profit accrued during the current day."""


@dataclass
class ContractMetric(DictDeserializable):
    """Represents a single position in a market.

    Attributes:
        contractId: Identifier of the market.
        from_metrics: Historical performance keyed by time period.
        hasNoShares: Whether the user holds no shares.
        hasShares: Whether the user holds any shares.
        hasYesShares: Whether the user holds YES shares.
        invested: Amount invested in the market.
        loan: Outstanding loan amount tied to the position.
        maxSharesOutcome: Outcome for which the user holds the most shares.
        payout: Expected payout at current prices.
        profit: Profit from this position.
        profitPercent: Profit expressed as a percentage.
        totalShares: Quantity of shares held per outcome.
        userId: Identifier of the user that holds the position.
        userUsername: Username of the user that holds the position.
        userName: Display name of the user that holds the position.
        userAvatarUrl: Avatar of the user that holds the position.
        lastBetTime: Timestamp describing when the last bet occurred.
    """

    contractId: str
    """Identifier of the market."""

    from_metrics: dict[str, dict[str, Number]] | None = None
    """Historical performance keyed by time period."""

    hasNoShares: bool = False
    """Whether the user holds no shares."""

    hasShares: bool = False
    """Whether the user holds any shares."""

    hasYesShares: bool = False
    """Whether the user holds YES shares."""

    invested: float = 0.0
    """Amount invested in the market."""

    loan: float = 0.0
    """Outstanding loan amount tied to the position."""

    maxSharesOutcome: str | None = None
    """Outcome for which the user holds the most shares."""

    payout: float = 0.0
    """Expected payout at current prices."""

    profit: float = 0.0
    """Profit from this position."""

    profitPercent: float = 0.0
    """Profit expressed as a percentage."""

    totalShares: dict[str, Number] = field(default_factory=dict)
    """Quantity of shares held per outcome."""

    userId: str = ""
    """Identifier of the user that holds the position."""

    userUsername: str = ""
    """Username of the user that holds the position."""

    userName: str = ""
    """Display name of the user that holds the position."""

    userAvatarUrl: str = ""
    """Avatar of the user that holds the position."""

    lastBetTime: int = 0
    """Timestamp describing when the last bet occurred."""

    @classmethod
    def from_dict(cls, env: JSONDict) -> "ContractMetric":
        """Take a dictionary and return an instance of the associated class.

        Args:
            env: Dictionary representation of the contract metric.

        Returns:
            Contract metric built from the provided dictionary.
        """

        data: JSONDict = dict(env)
        from_data = data.pop("from", None)
        if isinstance(from_data, Mapping):
            data["from_metrics"] = {
                str(period): dict(cast(Mapping[str, Number], metrics))
                for period, metrics in from_data.items()
                if isinstance(metrics, Mapping)
            }
        return super().from_dict(data)
