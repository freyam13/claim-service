import logging
import os
import uuid
from typing import Dict, Any, List

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Query
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import func, desc

from common.utilities import parse_csv_file_to_json
from src import repo
from src.db import init_db, db_dependency
from src.models import ClaimModel, ProviderQuery
from src.repo import Claim

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()


@app.on_event('startup')
async def on_startup():
    init_db()
    redis_connection = redis.from_url(
        os.environ['REDIS_URL'], encoding='utf-8', decode_responses=True
    )
    await FastAPILimiter.init(redis_connection)


@app.get('/claims/{claim_id}')
async def get_claims(claim_id: str, db: db_dependency) -> List[dict]:
    """
    Retrieve a claim by its unique identifier.

    Arguments:
        claim_id (str): the unique identifier of the claim to retrieve
        db (Session): the database session used to query the claims

    Raises:
        HTTPException:
            - 404: if no claims are found with the given claim_id

    Returns:
        List[dict]: a list of dictionaries representing the claim(s) found
        with the specified claim_id
    """
    logging.info(f'Received GET claims request; claim_id: {claim_id}')
    result = db.query(repo.Claim).filter(repo.Claim.id == claim_id).all()
    result_dict = [claim.dict() for claim in result]

    if not result:
        raise HTTPException(status_code=404, detail='Claims not found.')

    logging.info(f'GET claims results: {result_dict}')

    return result_dict


@app.post('/claims')
async def post_claims(
    db: db_dependency, csv_file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Process and store Claims from a CSV file.

    Arguments:
        db (Session): the database session used to persist the claims
        csv_file (UploadFile): the uploaded CSV file containing claims data

    Raises:
        HTTPException:
            - 400: if the uploaded file is not of type CSV
            - 400: if an error occurs while processing the file

    Returns:
        Dict[str, Any]: a dictionary containing a list of the processed claims data
    """
    logging.info(f'Received POST claims request: {csv_file}')

    if csv_file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail='File type must be CSV.')

    # normalize and validate Claim input
    try:
        claims = [
            ClaimModel(**{**claim, 'id': str(uuid.uuid4())})
            for claim in parse_csv_file_to_json(csv_file.file)
        ]
        claim_dict = [claim.dict() for claim in claims]

    except Exception as error:
        raise HTTPException(status_code=400, detail=f'Error processing file: {error}')

    # persist Claims to database
    db_claims = []
    for claim in claims:
        # TODO: add class methods to Pydantic models to convert to persisted models
        db_claim = Claim(
            allowed_fees=claim.allowed_fees,
            id=claim.id,
            member_coinsurance=claim.member_coinsurance,
            member_copay=claim.member_copay,
            net_fee=claim.net_fee,
            plan_group=claim.plan_group,
            provider_fees=claim.provider_fees,
            provider_npi=claim.provider_npi,
            quadrant=claim.quadrant,
            service_date=claim.service_date,
            submitted_procedure=claim.submitted_procedure,
            subscriber_number=claim.subscriber_number,
        )
        db_claims.append(db_claim)

    # TODO: check for duplicate claims? Same date, procedure, provide, etc?
    db.add_all(db_claims)
    db.commit()

    # PSEUDO CODE: I would consider an event driven approach for transferring Claim information
    # to a downstream "Payments" service. GCP appears to have an equivalent to AWS' EventBridge + SQS which I've used
    # extensively for use cases like this. The producer, in this case the Claims Service, need not care which or how
    # many authorized downstream services consume this data. Also, the consumers only need to know the basic schema in
    # which events are emitted in order to parse what is relevant to them. In my experience this scales better than
    # orchestrating everything via API requests for non-client based services.
    #
    # This example would be a common utility to be used throughout the service,
    # based on what I found here: https://cloud.google.com/pubsub/docs/publisher#python
    #
    # ```
    # publisher = pubsub_v1.PublisherClient()
    # topic_path = publisher.topic_path(project_id, topic_id)
    # publish_futures = []
    #
    # def get_callback(
    #         publish_future: pubsub_v1.publisher.futures.Future, data: str
    # ) -> Callable[[pubsub_v1.publisher.futures.Future], None]:
    #     def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
    #         try:
    #             # Wait 60 seconds for the publish call to succeed.
    #             print(f"Published message ID: {publish_future.result(timeout=60)} for data: {data}")
    #         except futures.TimeoutError:
    #             print(f"Publishing {data} timed out.")
    #
    #     return callback
    #
    # for claim in claims_data:
    #     data = json.dumps(claim).encode("utf-8")
    #
    #     publish_future = publisher.publish(topic_path, data)
    #
    #     publish_future.add_done_callback(get_callback(publish_future, data))
    #     publish_futures.append(publish_future)
    #
    # futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)
    # ```
    #
    # CONSIDERATIONS
    #
    # Q: "What needs to be done if there is a failure in either service and steps need to be unwinded?"
    #
    # A: GCP appears to offer similar solution to AWS's DLQ called "Dead-letter topic" in this case. Assuring that the
    #    event/message is published is handled by the producer as shown in Google's example slightly modified above.
    #    In the event that a service outage occurred and events/messages somehow were not emitted, in the past I've
    #    written utility scripts or endpoints that can emit the events received for a given time or criteria which
    #    allows us to essentially replay any missing data.
    #
    #    As far as the consumers go, they would want to implement the DLTs in this case and write to them if an
    #    Exception has occurred. In a similar fashion to the above scenario, the consumers would have the ability to
    #    replay the events/messages from the DLT after the underlying issue was addressed.
    #
    # Q: "Multiple instances of either service are running concurrently to handle a large volume of claims."
    #
    # A: consider using GCP's Cloud Functions as opposed to running containerized applications on dedicated instances
    #    for the following reasons:
    #      - automatically and infinitely scales
    #      - pay only for what you use while volume is still building
    #      - less time spent deploying, maintaining, and troubleshooting infrastructure
    #      - if volume of requests reaches critical mass where it is more affordable to run a cluster of dedicated
    #        instances with no impact to latency then we could always do that


    logging.info(f'Processed {len(claims)} claims: {claim_dict}')

    return {'claims': claim_dict}


@app.get('/providers', dependencies=[Depends(RateLimiter(times=6, seconds=60))])
async def providers_by_net_fee(
    db: db_dependency, limit: int = Query(10, description='Number of top providers')
) -> List[dict]:
    """
    Retrieve the top providers by total net fee.

    Arguments:
        db (Session): the database dependency used to access the provider data
        limit (int): the maximum number of top providers to return (default is 10)

    Raises:
        HTTPException: if no providers are found, a 404 error is raised

    Returns:
        List[dict]: a list of dictionaries containing provider information, including
        provider NPI, total net fee, claim count, and average net fee
    """
    logging.info(f'Querying top {limit} providers by net fee ...')

    # TODO: add pagination support
    top_providers = (
        db.query(
            repo.Claim.provider_npi,
            func.sum(repo.Claim.net_fee).label('total_net_fee'),
            func.count(repo.Claim.id).label('claim_count'),
            func.avg(repo.Claim.net_fee).label('avg_net_fee'),
        )
        .group_by(repo.Claim.provider_npi)
        .order_by(desc('total_net_fee'))
        .limit(limit)
        .all()
    )
    # TODO: figure out rate limiting FastAPI w/o starlette dependency
    top_provider_dict = [
        ProviderQuery(
            provider_npi=provider[0],
            total_net_fee=provider[1],
            claim_count=provider[2],
            average_net_fee=provider[3],
        ).dict()
        for provider in top_providers
    ]

    if not top_providers:
        raise HTTPException(status_code=404, detail='No providers found')

    logging.info(f'Query returned {len(top_provider_dict)} provider(s): {top_provider_dict}')

    return top_provider_dict


