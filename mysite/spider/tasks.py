from mysite import celery_app
import time
from spider.models import Job
from spider.models import JobInfo
from spider.config import NotPerformed
from celery import shared_task

@shared_task(time_limit=60*30, soft_time_limit=60*30, max_retries=1)
def jobs_tasks():
    jobs = Job.objects.all()
    for job in jobs:
        if job.status == NotPerformed:
            print(job.name)
            job.spider_ctl.spide_data()

@celery_app.task(time_limit=60*30, soft_time_limit=60*30, max_retries=1)
def refresh_job_async(job_id):
    job = Job.objects(id=job_id)[0]
    job.delete_infos()
    job.spider_ctl.spide_data()