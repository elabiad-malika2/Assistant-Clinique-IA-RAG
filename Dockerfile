FROM python:
WORKDIR app
COPY requirements.text
RUN pip install
COPY ..
CMD []