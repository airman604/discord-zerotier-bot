FROM python:3.9-slim

WORKDIR /srv
RUN useradd --uid 1001 bot

COPY src/requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=bot src/ .

USER bot
CMD ["/srv/bot.py"]