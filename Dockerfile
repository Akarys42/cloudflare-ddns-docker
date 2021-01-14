FROM python:3.9-slim

WORKDIR /app

ENTRYPOINT ["python3", "-m", "cloudflare_ddns"]
CMD []

# Install requirements in a separate step to not rebuild everything when the requirements are updated.
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
