from enum import StrEnum


class ConnectionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ItemStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ListingStatus(StrEnum):
    DRAFT = "draft"
    PUBLISH_QUEUED = "publish_queued"
    LIVE = "live"
    DELIST_QUEUED = "delist_queued"
    DELISTED = "delisted"
    ERROR = "error"


class OrderStatus(StrEnum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELED = "canceled"


class EventStatus(StrEnum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class MarketplaceChannel(StrEnum):
    EBAY = "ebay"
    ETSY = "etsy"
    POSHMARK = "poshmark"
