import enum


class GroupStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ResponseStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"
    OVERDUE = "OVERDUE"


class UserResponseEnum(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"
