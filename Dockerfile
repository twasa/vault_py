FROM python:3.12.1-alpine3.19
ENV APP_HOME=/vault_py
ADD ./src /vault_py/
ADD requirements.txt $APP_HOME
WORKDIR $APP_HOME
RUN pip install -r requirements.txt
RUN chown --recursive 10000:10000 $APP_HOME
USER 10000
