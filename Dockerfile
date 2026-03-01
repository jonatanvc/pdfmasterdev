FROM python:3.12-slim AS build

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends g++ gcc git libcairo2-dev \
    libpq-dev pkg-config python3-dev

RUN pip install -U pip && pip install poetry Babel

COPY pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry lock --no-interaction
RUN poetry install --only main --no-root --no-interaction
RUN pip freeze > /tmp/requirements.txt

COPY locale locale/
RUN pybabel compile -D pdf_bot -d locale \
    && find locale -type f -name '*.po' -delete

FROM python:3.12-slim AS deploy

RUN apt-get update \
    && apt-get install -y --no-install-recommends ghostscript libpango-1.0-0 \
    libpangoft2-1.0-0 libpq5 ocrmypdf poppler-utils \
    libreoffice-writer libreoffice-impress libreoffice-calc \
    g++ gcc git libcairo2-dev libpq-dev pkg-config python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /tmp/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

WORKDIR /app

COPY --from=build /build/locale /app/locale/
COPY pdf_bot pdf_bot/

CMD ["python", "-m", "pdf_bot"]
