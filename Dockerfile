FROM mpcsfinal

WORKDIR /auctions

COPY . .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD ["echo", "You ran me, I'm here!"]
