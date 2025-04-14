FROM python:3.12-alpine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py /opt/
COPY templates /opt/templates

EXPOSE 8080

WORKDIR /opt

# Default command is overridden in development environments
CMD ["python", "app.py"]
