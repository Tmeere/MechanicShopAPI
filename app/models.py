from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, CheckConstraint
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from typing import List

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with a custom model class
db = SQLAlchemy(model_class=Base)

# Association table for many-to-many relationship between service_tickets and mechanics
service_ticket_mechanic_association = db.Table(
    "service_ticket_mechanic_association",  # Table name
    Base.metadata,
    db.Column("service_ticket_id", ForeignKey("service_tickets.id")),  # Foreign key to service_tickets
    db.Column("mechanic_id", ForeignKey("mechanics.id"))  # Foreign key to mechanics
)

# Customer model representing the "Customers" table
class Customer(Base):
    __tablename__ = "customers"  # Table name
    
    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key
    name: Mapped[str] = mapped_column(db.String(100))  # Customer name
    email: Mapped[str] = mapped_column(db.String(150), unique=True)  # Unique email
    phone: Mapped[str] = mapped_column(db.String(15), unique=True)  # Unique phone number
    password: Mapped[str] = mapped_column(db.String(100)) 
    
    # Relationship to service_tickets
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(
        "ServiceTicket", 
        back_populates="customer", 
        cascade="all, delete"  # When a Customer is deleted, their ServiceTickets are also deleted
    )
# ServiceTicket model
class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False)  # Vehicle Identification Number
    service_date: Mapped[date]  # Date of service
    service_description: Mapped[str] = mapped_column(db.String(255), nullable=False)  # Description of the service
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)  # Foreign key to Customer

    # Relationships
    customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
    mechanics: Mapped[List["Mechanic"]] = db.relationship(
        secondary=service_ticket_mechanic_association, back_populates="assigned_service_tickets"
    )
# Mechanic model
class Mechanic(Base):
    __tablename__ = "mechanics"
    
    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))
    email: Mapped[str] = mapped_column(db.String(150), unique=True)
    salary: Mapped[int]
    
    # Relationships
    assigned_service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(
        "ServiceTicket", 
        secondary=service_ticket_mechanic_association, 
        back_populates="mechanics"
    )
