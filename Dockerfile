FROM python:3.9-slim
COPY . /app
WORKDIR /app
ENV PATH "$PATH:/app"
RUN pip install --no-cache-dir -r requirements.txt
CMD /bin/sh -c "while sleep 1000; do :; done"