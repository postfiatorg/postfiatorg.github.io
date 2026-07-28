from __future__ import annotations


class QueueCraftError(Exception):
    pass


class QueueEmpty(QueueCraftError):
    pass


class JobNotFound(QueueCraftError):
    pass


class LeaseError(QueueCraftError):
    pass


class PersistenceError(QueueCraftError):
    pass


class InvalidJob(QueueCraftError):
    pass
