from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True)
    branch = Column(String, nullable=True)
    credits = relationship("Credit")
    description = Column(String)
    duration = Column(Integer, nullable=True)
    keywords = Column(String, nullable=True)
    date = Column(DateTime)
    date_published = Column(DateTime)
    files = relationship("File")
    image = Column(String, nullable=True)
    location = relationship("Location")
    timestamp = Column(DateTime, nullable=True)
    title = Column(String)
    unit_name = Column(String, nullable=True)
    url = Column(String, nullable=True)
    virin = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<Product(id='{self.id}', title='{self.title}', description='{self.description}'," \
               f" keywords='{self.keywords}', date_published='{self.date_published}', unit_name='{self.unit_name}'>"

    def __hash__(self) -> int:
        return hash(self.id) ^ hash(self.title)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return False
        return self.id == other.id and self.title == other.title


class Credit(Base):
    __tablename__ = "credits"
    id = Column(Integer, primary_key=True)
    credit_id = Column(Integer)
    name = Column(String)
    rank = Column(String)
    url = Column(String)
    asset_id = Column(String, ForeignKey("products.id"))


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    state_abbreviation = Column(String)
    country_abbreviation = Column(String)
    asset_id = Column(String, ForeignKey("products.id"))


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    src = Column(String)
    type = Column(String)
    height = Column(Integer)
    width = Column(Integer)
    size = Column(Integer)
    bitrate = Column(Integer)
    asset_id = Column(String, ForeignKey("products.id"))
