CI is red for workers resuming delayed jobs at the exact scheduled time.

Operators see a worker-level "no ready jobs" failure even though the queue contains
a due high-priority job. Fix the queue system. Preserve priority ordering, delayed
scheduling, worker leases, dead-letter behavior, and persistence. Do not modify tests.

Start with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The full verifier will run additional private tests.
