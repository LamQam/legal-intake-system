from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    CLIENT = "client"
    LAWYER = "lawyer"
    ADMIN = "admin"
    STAFF = "staff"

class CaseStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING_DOCUMENTS = "pending_documents"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class CasePriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ConversationStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, index=True)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    cases = relationship("Case", back_populates="client")
    conversations = relationship("Conversation", back_populates="client")
    appointments = relationship("Appointment", back_populates="client")
    lawyer_profile = relationship("Lawyer", back_populates="user", uselist=False)

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    case_type = Column(String, nullable=False)  # e.g., "criminal", "civil", "family"
    status = Column(Enum(CaseStatus), default=CaseStatus.NEW)
    priority = Column(Enum(CasePriority), default=CasePriority.MEDIUM)
    jurisdiction = Column(String)
    estimated_value = Column(Float)
    actual_value = Column(Float)
    case_data = Column(JSON)  # Additional case-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))

    # Relationships
    client = relationship("User", back_populates="cases")
    lawyer = relationship("Lawyer", back_populates="cases")
    documents = relationship("Document", back_populates="case")
    appointments = relationship("Appointment", back_populates="case")
    payments = relationship("Payment", back_populates="case")

class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    license_number = Column(String, unique=True, index=True)
    specialization = Column(String)
    experience_years = Column(Integer)
    hourly_rate = Column(Float)
    bio = Column(Text)
    is_available = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    total_cases = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="lawyer_profile")
    cases = relationship("Case", back_populates="lawyer")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone_number = Column(String, nullable=False)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.NEW)
    language = Column(String, default="en")
    current_stage = Column(String, default="greeting")
    conversation_data = Column(JSON)  # Store conversation flow data
    whatsapp_message_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    client = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    message_type = Column(String, default="text")  # text, media, location, etc.
    content = Column(Text)
    media_url = Column(String)
    media_type = Column(String)  # image, video, document, audio
    whatsapp_message_id = Column(String)
    is_from_user = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String)
    document_type = Column(String)  # contract, evidence, correspondence, etc.
    is_confidential = Column(Boolean, default=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    case = relationship("Case", back_populates="documents")
    uploader = relationship("User")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    appointment_datetime = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    meeting_link = Column(String)
    location = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    case = relationship("Case", back_populates="appointments")
    client = relationship("User", back_populates="appointments")
    lawyer = relationship("Lawyer")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String)  # stripe, razorpay, bank_transfer
    transaction_id = Column(String)
    description = Column(String)
    payment_data = Column(JSON)  # Store payment provider specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    case = relationship("Case", back_populates="payments")
    client = relationship("User")
