FROM python:3.7

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get -y install msodbcsql17
RUN apt-get -y install unixodbc-dev

RUN echo "[ODBC Driver 17 for SQL Server]\n\
Description = Microsoft ODBC Driver 17 for SQL Server\n\
Driver = /opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.2.so.0.1\n\
UsageCount=1" >> /etc/odbcinst.ini


COPY ./requirements.txt /tmp/

WORKDIR /ogwforecast

RUN pip3 install -r /tmp/requirements.txt

COPY . /ogwforecast

ENV PYTHONPATH="${PYTHONPATH}:/ogw-forecast"
ENV SQL_DRIVER="ODBC Driver 17 for SQL Server"
ENV SQL_HOST="10.0.10.160"
ENV SQL_SCHEMA="OGW_Forecast"
ENV SQL_USER="sparky_sa"
ENV SQL_PWD="CQelectrical0!"
ENV SQL_TRUSTED="no"

EXPOSE 5000

CMD ["gunicorn"  , "-w", "4", "--bind", "0.0.0.0:5000", "app:server"]