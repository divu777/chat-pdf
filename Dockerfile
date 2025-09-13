FROM python:3.9-slim

WORKDIR /app

ARG OPENAI_API_KEY

ENV OPENAI_API_KEY=${OPENAI_API_KEY}


RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .


EXPOSE 8501

ENTRYPOINT ["uv", "run", "streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]