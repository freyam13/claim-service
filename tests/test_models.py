from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models import ClaimModel


def test_valid_claim_model():
    data = _valid_claim_data()
    claim = ClaimModel(**data)

    assert claim.allowed_fees == data['allowed_fees']
    assert claim.provider_npi == data['provider_npi']
    assert claim.net_fee == -15.0
    assert claim.submitted_procedure == data['submitted_procedure']


@pytest.mark.parametrize(
    'field, value',
    [
        ('allowed_fees', -10.0),
        ('member_coinsurance', -5.0),
        ('member_copay', -3.0),
        ('provider_fees', -7.0),
        ('provider_npi', '12345'),
        ('provider_npi', '12345678901'),
        ('service_date', 'invalid_date'),
        ('submitted_procedure', 'X12345'),
    ],
)
def test_invalid_claim_model(field, value):
    data = _valid_claim_data({field: value})

    with pytest.raises(ValidationError) as error:
        ClaimModel(**data)

    assert field in str(error.value)


def _valid_claim_data(overrides=None):
    data = {
        'allowed_fees': 100.0,
        'id': 'some-unique-id',
        'member_coinsurance': 20.0,
        'member_copay': 15.0,
        'plan_group': 'ABC123',
        'provider_fees': 50.0,
        'provider_npi': 1497775530,
        'quadrant': 'Q1',
        'service_date': datetime.now(),
        'submitted_procedure': 'D12345',
        'subscriber_number': 'SUB123456',
    }
    if overrides:
        data.update(overrides)

    return data
