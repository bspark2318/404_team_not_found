FROM python:3.8

WORKDIR C:\Users\cvg11\Desktop\404_team_not_found\auction

COPY . .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]

CMD ["python3", "flask --app auction run"]