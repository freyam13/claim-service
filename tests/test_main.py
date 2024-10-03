import os

import freezegun
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


@freezegun.freeze_time('2018-03-28T00:00:00+00:00')
def test_post_claims(mock_db, valid_claim_data):
    with open('./resources/claim_1234.csv', 'rb') as f:
        response = client.post(
            '/claims',
            files={
                'csv_file': (
                    os.path.basename('./resources/claim_1234.csv'),
                    f,
                    'text/csv',
                )
            },
        )

    assert response.status_code == 200
    assert response.json() == valid_claim_data


@pytest.fixture
def valid_claim_data():
    return {
        'claims': [
            {
                'allowed_fees': 100.0,
                'id': 'ccf696f7-dcdd-4e4a-a79e-37360507211a',
                'member_coinsurance': 0.0,
                'member_copay': 0.0,
                'plan_group': 'GRP-1000',
                'provider_fees': 100.0,
                'provider_npi': 1497775530,
                'quadrant': '',
                'service_date': '2018-03-28T00:00:00',
                'submitted_procedure': 'D0180',
                'subscriber_number': '3730189502',
                'net_fee': 0.0,
            },
            {
                'allowed_fees': 108.0,
                'id': 'af487174-b85c-4ffc-8127-5dc035fb8f2f',
                'member_coinsurance': 0.0,
                'member_copay': 0.0,
                'plan_group': 'GRP-1000',
                'provider_fees': 108.0,
                'provider_npi': 1497775530,
                'quadrant': '',
                'service_date': '2018-03-28T00:00:00',
                'submitted_procedure': 'D0210',
                'subscriber_number': '3730189502',
                'net_fee': 0.0,
            },
            {
                'allowed_fees': 65.0,
                'id': 'abb64fc8-cc5f-40d2-9a04-6116a4820b2e',
                'member_coinsurance': 16.25,
                'member_copay': 0.0,
                'plan_group': 'GRP-1000',
                'provider_fees': 130.0,
                'provider_npi': 1497775530,
                'quadrant': '',
                'service_date': '2018-03-28T00:00:00',
                'submitted_procedure': 'D4346',
                'subscriber_number': '3730189502',
                'net_fee': 81.25,
            },
            {
                'allowed_fees': 178.0,
                'id': 'd40267d6-132c-4d55-a070-f4a5f00645df',
                'member_coinsurance': 35.6,
                'member_copay': 0.0,
                'plan_group': 'GRP-1000',
                'provider_fees': 178.0,
                'provider_npi': 1497775530,
                'quadrant': 'UR',
                'service_date': '2018-03-28T00:00:00',
                'submitted_procedure': 'D4211',
                'subscriber_number': '3730189502',
                'net_fee': 35.599999999999994,
            },
        ]
    }
