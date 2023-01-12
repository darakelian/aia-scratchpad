from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime


Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    keywords = Column(String)
    date_published = Column(DateTime)
    unit_name = Column(String)

    def __repr__(self) -> str:
        return f"<Product(id='{self.id}', title='{self.title}', description='{self.description}'," \
               f" keywords='{self.keywords}', date_published='{self.date_published}', unit_name='{self.unit_name}'>"

    def __hash__(self) -> int:
        return hash(self.id) ^ hash(self.title)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return False
        return self.id == other.id and self.title == other.title
