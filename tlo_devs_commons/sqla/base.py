from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import MetaData, Integer, Column
from re import sub


class _declared_Base:
    @declared_attr
    def __tablename__(self):
        """
        Automatically sets the name for created tables.\n
        Converts CamelCase class names to snake_case table names.
        """
        return sub(r"(?<!^)(?=[A-Z])", "_", self.__name__).lower()

    pk = Column(Integer(), primary_key=True)


Base = declarative_base(
    cls=_declared_Base,
    metadata=MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",  # index
            "uq": "uq_%(table_name)s_%(column_0_name)s",  # unique constraint
            "ck": "ck_%(table_name)s_%(constraint_name)s",  # check constraint
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # foreign key
            "pk": "pk_%(table_name)s",  # primary key
        }
    ),
)


__all__ = ["Base"]
