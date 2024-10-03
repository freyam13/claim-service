from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ConfiguredModel(BaseModel):

    class Config:
        from_attributes = True
        populate_by_name = True


class ClaimModel(ConfiguredModel):
    allowed_fees: float = Field(..., alias='Allowed fees', ge=0)
    id: str = None
    member_coinsurance: float = Field(..., alias='member coinsurance', ge=0)
    member_copay: float = Field(..., alias='member copay', ge=0)
    plan_group: str = Field(..., alias='Plan/Group #')
    provider_fees: float = Field(..., alias='provider fees', ge=0)
    provider_npi: int = Field(..., alias='Provider NPI')
    quadrant: Optional[str] = Field(default='', alias='quadrant')
    service_date: datetime = Field(..., alias='service date')
    submitted_procedure: str = Field(..., alias='submitted procedure')
    subscriber_number: str = Field(..., alias='Subscriber#')

    @field_validator(
        'allowed_fees',
        'member_coinsurance',
        'member_copay',
        'provider_fees',
        mode='before',
    )
    def convert_currency(cls, value):
        if isinstance(value, str):
            return float(value.replace('$', '').strip())
        return value

    @field_validator('service_date', mode='before')
    def parse_service_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, '%m/%d/%y %H:%M')
        return value

    @field_validator('provider_npi')
    def validate_provider_npi(cls, value):
        if len(str(value)) != 10:
            raise ValueError('The Providers NPI number is invalid; should be 10 digits long.')
        return value

    @field_validator('submitted_procedure')
    def validate_submitted_procedure(cls, value):
        if not value.startswith('D'):
            raise ValueError('The submitted procedure must start with the letter "D".')
        return value

    @property
    def net_fee(self) -> float:
        return (
            self.provider_fees + self.member_coinsurance + self.member_copay
        ) - self.allowed_fees

    def dict(self, **kwargs):
        data = super().model_dump(**kwargs)
        data['net_fee'] = self.net_fee
        return data


class ProviderQuery(ConfiguredModel):
    provider_npi: str
    total_net_fee: float
    claim_count: int
    average_net_fee: float

    @field_validator(
        'total_net_fee',
        'average_net_fee',
        check_fields=False,
        mode='before',
    )
    def round_decimals(cls, value):
        return round(value, 2)

    def dict(self, **kwargs):
        return super().model_dump(**kwargs)
