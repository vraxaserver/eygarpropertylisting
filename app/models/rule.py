from sqlalchemy import Column, String, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base


class RuleType(str, enum.Enum):
    HOUSE_RULES = "house_rules"
    CANCELLATION_POLICY = "cancellation_policy"
    CHECK_IN_POLICY = "check_in_policy"


class PropertyRule(Base):
    __tablename__ = "property_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    
    rule_text = Column(String(500), nullable=False)
    rule_type = Column(Enum(RuleType), nullable=False, index=True)
    
    # Relationships
    property = relationship("Property", back_populates="rules")
    
    __table_args__ = (
        Index('idx_property_rules_type', 'property_id', 'rule_type'),
    )
    
    def __repr__(self):
        return f"<PropertyRule(property_id={self.property_id}, type='{self.rule_type}')>"