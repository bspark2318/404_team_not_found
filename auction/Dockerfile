FROM python:3.8

WORKDIR C:/Users/cvg11/Desktop/404_team_not_found/auction

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "--app", "__init__.py", "run", "--host", "0.0.0.0"]