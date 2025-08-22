FROM python:3.9-slim

RUN pip install bottle requests

COPY dirigera-exporter.py .
RUN chmod +x ./dirigera-exporter.py

ENTRYPOINT ["python"]
CMD ["dirigera-exporter.py"]
