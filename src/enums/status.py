from enum import StrEnum


class GroupStatusEnum(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ResponseStatusEnum(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"
    OVERDUE = "OVERDUE"


class UserResponseEnum(StrEnum):
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"
