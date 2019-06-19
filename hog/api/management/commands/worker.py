import os

from django.core.management.base import BaseCommand, CommandError

import redis
from rq import Worker, Queue, Connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        listen = ["high", "default", "low"]
        redis_url = os.getenv("REDISTOGO_URL", "redis://localhost:6379")
        conn = redis.from_url(redis_url)
        with Connection(conn):
            worker = Worker(map(Queue, listen))
            worker.work()
