import uuid

from sqlalchemy import Column, String, DateTime, Float, Numeric

from src.db import Base


class Claim(Base):
    __tablename__ = 'claim'

    id = Column(String, primary_key=True, default=uuid.uuid4)

    allowed_fees = Column(Float, nullable=False)
    member_coinsurance = Column(Float, nullable=False)
    member_copay = Column(Float, nullable=False)
    net_fee = Column(Numeric(precision=10, scale=2), nullable=True)
    plan_group = Column(String, nullable=False)
    provider_fees = Column(Float, nullable=False)
    provider_npi = Column(String, nullable=False)
    quadrant = Column(String, nullable=True)
    service_date = Column(DateTime, nullable=False)
    submitted_procedure = Column(String, nullable=False)
    subscriber_number = Column(String, nullable=False)

    def dict(self):
        return {
            'id': self.id,
            'allowed_fees': self.allowed_fees,
            'member_coinsurance': self.member_coinsurance,
            'member_copay': self.member_copay,
            'net_fee': self.net_fee,
            'plan_group': self.plan_group,
            'provider_fees': self.provider_fees,
            'provider_npi': self.provider_npi,
            'quadrant': self.quadrant,
            'service_date': (
                self.service_date.isoformat() if self.service_date else None
            ),
            'submitted_procedure': self.submitted_procedure,
            'subscriber_number': self.subscriber_number,
        }
