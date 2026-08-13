import re
from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    id: Any
    __name__: str

    # Generate __tablename__ automatically in snake_case format
    @declared_attr
    def __tablename__(cls) -> str:
        name = cls.__name__
        # Convert CamelCase to snake_case
        parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', name)
        snake_name = "_".join(parts).lower()
        if snake_name.endswith('y'):
            return f"{snake_name[:-1]}ies"
        elif snake_name.endswith('s'):
            return f"{snake_name}es"
        else:
            return f"{snake_name}s"
