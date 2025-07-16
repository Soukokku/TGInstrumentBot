from sqlalchemy import (
    Column, Integer, String, ForeignKey, Enum, BigInteger, TIMESTAMP, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    users = relationship("User", back_populates="role")

class Object(Base):
    __tablename__ = 'objects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    address = Column(String)

    users = relationship("User", back_populates="object")
    tools = relationship("Tool", back_populates="object")
    inventories = relationship("Inventory", back_populates="object")
    requests_from = relationship("Request", back_populates="object_from", foreign_keys='Request.object_from_id')
    requests_to = relationship("Request", back_populates="object_to", foreign_keys='Request.object_to_id')

class ToolStatus(Base):
    __tablename__ = 'tool_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    tools = relationship("Tool", back_populates="status")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_username = Column(String)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    full_name = Column(String)
    role_id = Column(Integer, ForeignKey('roles.id'))
    object_id = Column(Integer, ForeignKey('objects.id'))

    role = relationship("Role", back_populates="users")
    object = relationship("Object", back_populates="users")
    inventories = relationship("Inventory", back_populates="user")
    requests_from = relationship("Request", back_populates="user_from", foreign_keys='Request.user_from_id')
    requests_to = relationship("Request", back_populates="user_to", foreign_keys='Request.user_to_id')

class Tool(Base):
    __tablename__ = 'tools'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    serial_number = Column(String, unique=True)
    qr_code = Column(String, unique=True)
    object_id = Column(Integer, ForeignKey('objects.id'))
    status_id = Column(Integer, ForeignKey('tool_status.id'))

    object = relationship("Object", back_populates="tools")
    status = relationship("ToolStatus", back_populates="tools")
    inventories = relationship("ToolInventory", back_populates="tool")
    requests = relationship("Request", back_populates="tool")

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    inventory_date = Column(TIMESTAMP, nullable=False)
    object_id = Column(Integer, ForeignKey('objects.id'))

    user = relationship("User", back_populates="inventories")
    object = relationship("Object", back_populates="inventories")
    tool_inventories = relationship("ToolInventory", back_populates="inventory")

class ToolInventory(Base):
    __tablename__ = 'tool_inventory'
    inventory_id = Column(Integer, ForeignKey('inventory.id'), primary_key=True)
    tool_id = Column(Integer, ForeignKey('tools.id'), primary_key=True)

    inventory = relationship("Inventory", back_populates="tool_inventories")
    tool = relationship("Tool", back_populates="inventories")

class RequestStatus(Base):
    __tablename__ = 'request_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    requests = relationship("Request", back_populates="status")

class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tool_id = Column(Integer, ForeignKey('tools.id'))
    object_from_id = Column(Integer, ForeignKey('objects.id'))
    object_to_id = Column(Integer, ForeignKey('objects.id'))
    user_from_id = Column(Integer, ForeignKey('users.id'))
    user_to_id = Column(Integer, ForeignKey('users.id'))
    status_id = Column(Integer, ForeignKey('request_status.id'))

    tool = relationship("Tool", back_populates="requests")
    object_from = relationship("Object", back_populates="requests_from", foreign_keys=[object_from_id])
    object_to = relationship("Object", back_populates="requests_to", foreign_keys=[object_to_id])
    user_from = relationship("User", back_populates="requests_from", foreign_keys=[user_from_id])
    user_to = relationship("User", back_populates="requests_to", foreign_keys=[user_to_id])
    status = relationship("RequestStatus", back_populates="requests")
