from abc import abstractmethod, abstractstaticmethod
import os
import bcrypt
import base64
import logging
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from typing import Optional
from sqlalchemy.orm.session import Session
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Enum, Table, UniqueConstraint
from sqlalchemy.orm import relationship, validates
from .database import DeclarativeBase, engine, create_engine, DBContext

from . import errors, enums, config, utilities
from .mixins import AuditMixin

logger = logging.getLogger("backend")




class Base(DeclarativeBase):
    __abstract__ = True
    # __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)


class Status(Base):
    __abstract__ = True
    __table_args__ = {"sqlite_autoincrement": False}

    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<{self.__class__.name}(id={self.id}, name="{self.name}")>'
    
    def __str__(self) -> str:
        return self.name
    
    @abstractstaticmethod
    def find_by_id(session: Session, id_: int) -> Optional['Status']:
        pass
    
    @abstractstaticmethod
    def find_by_name(session: Session, name: str) -> Optional['Status']:
        pass


class Type_(Base):
    __abstract__ = True

    name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<{self.__class__.name}(id={self.id}, name="{self.name}")>'
    
    def __str__(self) -> str:
        return self.name
    
    @abstractmethod
    def find_by_id(self, session: Session, id_: int) -> Optional['Type_']:
        pass
    
    @abstractmethod
    def find_by_name(self, session: Session, name: str) -> Optional['Type_']:
        pass


class User(Base):
    __tablename__ = 'user'

    active = Column(Boolean, nullable=False, default=True)
    last_login_date = Column(DateTime) # type: datetime
    email = Column(String(256))
    first_name = Column(String(15), nullable=False)
    last_name = Column(String(15), nullable=False)
    phone = Column(String(256))
    username = Column(String(256), nullable=False, unique=True, index=True)
    password_hash = Column(String(256), nullable=False)

    # Relationship

    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}')"
    
    def __str__(self) -> str:
        return self.full_name
    
    def on_login(self) -> 'UserLoginLog':
        """Log a login event."""
        return UserLoginLog.create(event_type=enums.LoginEventType.Login, user=self)
    
    def on_logout(self) -> 'UserLoginLog':
        """Log a logout event."""
        return UserLoginLog.create(event_type=enums.LoginEventType.Logout, user=self)
    
    @property
    def last_login_date_str(self) -> str:
        return self.last_login_date.strftime(config.DATETIME_FORMAT)
    
    @property
    def password(self) -> None:
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute!')
    
    @property
    def is_superuser(self) -> bool:
        """Check if the user is a superuser."""
        return self.id == 1

    @password.setter
    def password(self, password: str):
        """Hash password on the fly. This allows the plan text password to be used when creating a User instance."""
        self.password_hash = User.generate_password_hash(password)
    
    @property
    def full_name(self) -> str:
        """Return the full name of the user. In the following format: first_name, last_name"""
        return f"{self.first_name}, {self.last_name}"
    
    @property
    def initials(self) -> str:
        """Return the initials of the user."""
        return f"{self.first_name[0].upper()}{self.last_name[0].upper()}"
    
    def check_password(self, password: str) -> bool:
        return User.verify_password(self.password_hash, password)
    
    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """Check if password matches the one provided."""
        return bcrypt.checkpw(password.encode(config.ENCODING_STR), password_hash.encode(config.ENCODING_STR))
    
    @staticmethod
    def generate_password_hash(password: str) -> str:
        """Generate a hashed password."""
        return bcrypt.hashpw(password.encode(config.ENCODING_STR), bcrypt.gensalt()).decode(config.ENCODING_STR)


class UserLoginLog(Base):
    """A simple log for tracking who logged in or out and when."""
    __tablename__ = 'user_login'

    event_date = Column(DateTime, nullable=False, default=datetime.now)
    event_type = Column(Enum(enums.LoginEventType))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # Relationships
    user = relationship('User', foreign_keys=[user_id]) # type: User

    def __repr__(self) -> str:
        return f"<UserLoginLog(id={self.id}, event_date={self.event_date}, event_type={self.event_type}, user={self.user})>"
    
    def __str__(self) -> str:
        return f"{self.event_date} - {self.event_type} - {self.user}"

    @staticmethod
    def create(event_type: enums.LoginEventType, user: User) -> 'UserLoginLog':
        """Create a new user login log."""
        log = UserLoginLog(event_type=event_type, user=user)
        return log

    @staticmethod
    def on_login(user: User) -> 'UserLoginLog':
        """Log a login event."""
        return UserLoginLog.create(event_type=enums.LoginEventType.Login, user=user)
    
    @staticmethod
    def on_logout(user: User) -> 'UserLoginLog':
        """Log a logout event."""
        return UserLoginLog.create(event_type=enums.LoginEventType.Logout, user=user)


class UomConversion(DeclarativeBase):
    """Represents how to convert from one Uom to another."""
    __tablename__ = 'uom_conversion'

    to_uom_id = Column(Integer, ForeignKey('uom.id'), nullable=False, primary_key=True)
    from_uom_id = Column(Integer, ForeignKey('uom.id'), nullable=False, primary_key=True)
    description = Column(String(100))
    factor = Column(Float, nullable=False)
    multiply = Column(Float, nullable=False)

    # Relationships
    from_uom = relationship('Uom', foreign_keys=[from_uom_id])  # type: Uom
    to_uom = relationship('Uom', foreign_keys=[to_uom_id])  # type: Uom

    def __repr__(self) -> str:
        return f'UomConversion(from_uom="{self.from_uom}", to_uom="{self.to_uom}")'

    def convert(self, value: float) -> float:
        """Apply the conversion to the givin value."""
        return value * self.multiply / self.factor
    
    @staticmethod
    def create(session: Session, user: User, from_uom: 'Uom', to_uom: 'Uom', factor: float, multiply: float, description: str=None) -> 'UomConversion':
        """Creates a new conversion and adds it to the session.

        Args:
            session (Session): The DB session used for saving.
            user (User): The user creating this conversion.
            from_uom (Uom): The uom to convert from.
            to_uom (Uom): The uom to convert to.
            factor (float): When converting, the value is multiplied by multiply then divided by this.
            multiply (float): When converting, the value is multiplied by this.
            description (str, optional): A shot description for this conversion. Defaults to None.

        Returns:
            UomConversion: Returns the new conversion obj.
        """

        conversion = UomConversion(
            from_uom=from_uom,
            to_uom=to_uom,
            factor=factor,
            multiply=multiply,
            description=description,
            created_by_user=user,
            modified_by_user=user
        )
        session.add(conversion)
        return conversion


class Uom(Base):
    """Represents a unit of measure."""
    __tablename__ = 'uom'
    __table_args__ = (
        UniqueConstraint("code", "name"),
    )

    active = Column(Boolean, default=True)
    code = Column(String(10), nullable=False)
    description = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)
    read_only = Column(Boolean, default=False)
    type_name = Column(Enum(enums.UomType), nullable=False) # type: enums.UomType

    # Relationships
    conversions = relationship("UomConversion", back_populates="from_uom", foreign_keys=UomConversion.from_uom_id) # type: list[UomConversion]

    def __repr__(self) -> str:
        return f'<Uom(id={self.id}, name="{self.name}")>'
    
    def add_conversion(self, session: Session, user: User, to_uom: 'Uom', factor: float, multiply: float, description: str=None) -> UomConversion:
        """Add a new conversion to this uom.

        Args:
            session (Session): The DB session used for saving.
            user (User): The user creating this conversion.
            to_uom (Uom): The uom to convert to.
            factor (float): When converting, the value is multiplied by multiply then divided by this.
            multiply (float): When converting, the value is multiplied by this.
            description (str, optional): A shot description for this conversion. Defaults to None.
        
        Raises:
            errors.UomConversionError: Raised if uom types are incompatible.

        Returns:
            UomConversion: Returns the new conversion obj.
        """
        for conversion in self.conversions:
            if conversion.to_uom == to_uom:
                return conversion
        
        if self.type_name != to_uom.type_name:
            raise errors.UomConversionError(f"Can not add uom conversion from {self.name} to {to_uom.name}. Uoms have incompatible types {self.type_name} - {to_uom.type_name}.")

        conversion = UomConversion.create(
                        session,
                        user,
                        from_uom=self,
                        to_uom=to_uom,
                        factor=factor,
                        multiply=multiply,
                        description=description
                        )
        self.conversions.append(conversion)
        self.date_modified = datetime.now()
        self.modified_by_user = user
        return conversion
    
    def remove_conversion(self, session: Session, user: User, conversion: UomConversion) -> None:
        """Remove a conversion.

        Args:
            session (Session): The DB session used for saving.
            user (User): The user removing this conversion.
            conversion (UomConversion): The conversion to remove.
        """
        if conversion not in self.conversions:
            return None
        self.conversions.remove(conversion)
        session.delete(conversion)
        self.date_modified = datetime.now()
        self.modified_by_user = user
    
    def convert_to(self, to_uom: 'Uom', value: float) -> float:
        """Returns conversion to another Uom.

        Args:
            to_uom (Uom): The Uom to convert to.
            value (float): The value to convert.

        Raises:
            errors.UomConversionError: Raised if the Uom types are not compatible.
            errors.UomConversionError: Raised if unable to find conversion.

        Returns:
            float: The converted value.
        """
        if self.id == to_uom.id:
            return value
        if self.type_name != to_uom.type_name:
            raise errors.UomConversionError("Uoms must be of the same type.")
        if to_uom not in [conversion.to_uom for conversion in self.conversions]:
            raise errors.UomConversionError(f"Unknown conversion from '{self.name}' to '{to_uom.name}'")

        for uom_conversion in self.conversions:
            if uom_conversion.to_uom == to_uom:
                break
        return uom_conversion.convert(value)

    @staticmethod
    def find_by_name(session: Session, name: str) -> Optional['Uom']:
        """Returns a Uom by name."""
        return session.query(Uom).filter_by(name=name).first() # type: Uom

    @staticmethod
    def find_by_code(session: Session, code: str) -> Optional['Uom']:
        """Returns a Uom by code."""
        return session.query(Uom).filter_by(code=code).first() # type: Uom

    @staticmethod
    def find_by_id(session: Session, id: int) -> Optional['Uom']:
        """Returns a Uom by id."""
        return session.query(Uom).filter_by(id=id).first() # type: Uom


class Food(Base, AuditMixin):
    """Represents a food."""
    __tablename__ = 'food'
    __table_args__ = (
        UniqueConstraint("barcode", "name"),
    )

    active = Column(Boolean, nullable=False, default=True)
    barcode = Column(String(100), nullable=False)
    calories_per_serving = Column(Float, nullable=False)
    brand = Column(String(100), nullable=False)
    description = Column(String(500))
    name = Column(String(100), nullable=False)
    serving_size = Column(Float, nullable=False)
    serving_size_uom_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # Relationships
    serving_size_uom = relationship('Uom', foreign_keys=[serving_size_uom_id]) # type: Uom

    @validates
    def validates_serving_size_uom_id(self, key: str, value: int) -> int:
        """Validates that serving_size_uom is of type Weight or Count."""
        valid_types = [enums.UomType.Count, enums.UomType.Weight]

        with DBContext() as session:
            uom = session.query(Uom).filter(Uom.id==value).first()# type: Uom
            if uom.type_name not in valid_types:
                raise errors.ValidationError(f"'{uom}' does not have the right type [{[name.value for name in valid_types]}].")
        return value

    @classmethod
    def brands(cls) -> List[str]:
        brands = []
        with DBContext() as session:
            food = session.query(cls).order_by(cls.brand).all() # type: List[Food]
            for item in food:
                if item.brand in brands:
                    continue
                brands.append(item.brand)
        return brands
    

class FoodConsumption(Base):
    """Represents a food consumption."""
    __tablename__ = 'food_consumption'

    date_consumed = Column(DateTime, nullable=False, default=datetime.now())
    food_id = Column(Integer, ForeignKey('food.id'), nullable=False)
    serving_size = Column(Float, nullable=False)
    serving_size_uom_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # Relationships
    food = relationship('Food', foreign_keys=[food_id]) # type: Food
    serving_size_uom = relationship('Uom', foreign_keys=[serving_size_uom_id]) # type: Uom
    user = relationship('User', foreign_keys=[user_id]) # type: User



def create_tables():
    logger.info("[SYSTEM] Creating tables...")
    Base.metadata.create_all(engine)


def drop_tables():
    logger.warning("[SYSTEM] Droping tables...")
    Base.metadata.drop_all(engine)


def create_test_data():
    logger.info("[SYSTEM] Creating test data...")
    pass


def force_recreate():
    logger.warning("[SYSTEM] Force recreating database. Data loss will occur.")
    if config.DATABASE_URL_WITHOUT_SCHEMA.startswith("mysql"):
        temp_engine = create_engine(config.DATABASE_URL_WITHOUT_SCHEMA)
        temp_engine.execute(config.SCHEMA_CREATE_STATEMENT)
        temp_engine.dispose()

    drop_tables()
    create_database()


def create_database():
    logger.info("[SYSTEM] Creating database...")
    if config.DATABASE_URL_WITHOUT_SCHEMA.startswith("mysql"):
        temp_engine = create_engine(config.DATABASE_URL_WITHOUT_SCHEMA)
        temp_engine.execute(config.SCHEMA_CREATE_STATEMENT)
        temp_engine.dispose()

    create_tables()