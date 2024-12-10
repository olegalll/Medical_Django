FROM python:3.12-slim
WORKDIR /app
COPY ./wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh
COPY .flake8 /app/.flake8
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY medical /app/medical
EXPOSE 8000
CMD ["/app/wait-for-it.sh", "db:5432", "--", "python", "/app/medical/manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]