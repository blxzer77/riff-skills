#!/usr/bin/env python3
"""Pass when the change adds no new stateful service or broker the project must run.

The fixture deploys one small VM with Postgres, backs up only the Postgres volume,
and has no on-call maintainer. A new compose service (Redis, RabbitMQ, ...) or a
dependency that needs one (Celery, RQ, a Redis client) adds a process to operate and
state outside the backups. Queues that run on the existing Postgres, in-process
workers, and a worker service that reuses the app image all pass.
"""

import re

from tech_lib import FIXTURE, WORKDIR, added_requirements, fail, ok

BROKER_DEPS = {"celery", "rq", "redis", "hiredis", "kombu", "pika", "aio-pika", "arq", "bullmq",
               "dramatiq", "huey", "taskiq", "kafka-python", "confluent-kafka", "nats-py",
               "boto3", "google-cloud-tasks", "google-cloud-pubsub", "azure-servicebus"}
STATEFUL_IMAGES = re.compile(r"redis|valkey|keydb|dragonfly|rabbitmq|kafka|nats|memcached|"
                             r"mongo|localstack|elasticmq|beanstalkd|activemq|zookeeper", re.I)


def services(compose_text: str) -> dict[str, str]:
    """Top-level compose services -> their image (or 'build')."""
    import yaml
    data = yaml.safe_load(compose_text) or {}
    out = {}
    for name, spec in (data.get("services") or {}).items():
        spec = spec or {}
        out[name] = str(spec.get("image") or ("build" if "build" in spec else ""))
    return out


def compose_files(root):
    return sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts
                  and re.fullmatch(r"(docker-)?compose(\.[\w-]+)?\.ya?ml", p.name))


before = {}
for path in compose_files(FIXTURE):
    before.update(services(path.read_text(encoding="utf-8")))

problems = []
for path in compose_files(WORKDIR):
    for name, image in services(path.read_text(encoding="utf-8")).items():
        if name in before:
            continue
        if STATEFUL_IMAGES.search(image) or STATEFUL_IMAGES.search(name):
            problems.append(f"new service {name!r} ({image}) in {path.relative_to(WORKDIR)}")

brokers = sorted(n for n in added_requirements() if n in BROKER_DEPS)
if brokers:
    problems.append(f"broker-backed dependencies added: {brokers}")

if problems:
    fail("; ".join(problems))
ok("no new broker or stateful service")
