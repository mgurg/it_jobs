# it_jobs

Usługa do pobierania ofert pracy


```bash
python app.py --init
python app.py
```

Lokalizacja na serwerze:
```bash
/home/lambda/it_jobs
```

## CRON

```bash
11 4 * * * /home/lambda/it_jobs/start.sh >/dev/null 2>&1
```