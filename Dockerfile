FROM node:20-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    NODE_ENV=production \
    VIRTUAL_ENV=/opt/venv \
    PYTHON_EXECUTABLE=python3 \
    PORT=5000

ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN python3 -m venv "${VIRTUAL_ENV}" && \
    python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY role1-agent-graph/package*.json ./role1-agent-graph/
RUN npm ci --prefix role1-agent-graph

COPY . .

EXPOSE 5000

CMD ["node", "role1-agent-graph/api_server.js"]
