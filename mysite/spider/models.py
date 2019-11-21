from django.db import models
from mongoengine import *
from bson.objectid import ObjectId
from datetime import datetime
from spider.basic_spider import LagouSpider
from spider.config import NotPerformed

# Create your models here.
class Job(Document):
    meta = {
		'collection': 'jobs',
		'allow_inheritance': False
	}
    _spider_cls = LagouSpider

    id = StringField(primary_key=True, default = lambda: str(ObjectId()))
    name = StringField(unique=True)
    created_at = DateTimeField(default= lambda : datetime.now())
    updated_at = DateTimeField(default= lambda : datetime.now())
    status = IntField(default= NotPerformed)
    total = IntField()

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.spider_ctl = self._spider_cls(self)
    
    def delete_infos(self):
        JobInfo.objects(job_id=self.id).delete()
        self.status = NotPerformed
        self.total = 0
        self.save()
    
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "total": self.total,
        }



class JobInfo(Document):
    meta = {
		'collection': 'job_info',
		'allow_inheritance': True
    }
    id = StringField(primary_key=True, default = lambda: str(ObjectId()))
    position_id = StringField()
    job_id = StringField(required=True)
    company_name = StringField()
    position_name = StringField()
    high_salary = IntField()
    low_salary = IntField()
    work_year = StringField()
    education = StringField()
    skill_lables = ListField()
    company_lables = ListField()
    company_size = StringField()
    linestaion = StringField()
    position_lables = ListField()
    district = StringField()
    position_advantage = StringField()
    created_at = DateTimeField(default=lambda: datetime.now())

    def as_dict(self):
        return {
            "position_name": self.position_name,
            "job_id": self.job_id,
            "company_name": self.company_name,
            "position_name": self.position_name,
            "high_salary": self.high_salary,
            "low_salary": self.low_salary,
            "work_year": self.work_year,
            "education": self.education,
            "skill_lables": self.skill_lables,
            "company_lables": self.company_lables,
            "company_size": self.company_size,
            "linestaion": self.linestaion,
            "position_lables": self.position_lables,
            "district": self.district,
            "position_advantage": self.position_advantage,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }