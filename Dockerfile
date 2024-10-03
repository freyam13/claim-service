# use the slim version of Python 3.11
FROM python:3.11.0-slim

# set the working directory inside the container
WORKDIR /claim-service

# copy Pipfile and Pipfile.lock first to leverage Docker cache for dependency installation
COPY Pipfile Pipfile.lock ./

# install pipenv and project dependencies
RUN pip install pipenv && pipenv install --deploy --system

# copy the source code into the container
COPY common ./common
COPY src ./src

# expose port 8000 (FastAPI default)
EXPOSE 8000

# specify the default command to run Uvicorn with FastAPI
CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
