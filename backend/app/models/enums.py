import enum

class DeveloperRole(str, enum.Enum):
    AI_ML = "AI_ML"
    AUTOMATION = "AUTOMATION"
    DEVOPS = "DEVOPS"

class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
