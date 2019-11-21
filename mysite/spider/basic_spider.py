import requests
import urllib.parse
from datetime import datetime
from spider.config import Performed, Performing, NotPerformed
import json

class Spider:
    base_url = ""
    headers = {}

    def __init__(self):
        pass
    
    def get_cookie(self):
        pass

    def spide_data(self):
        pass

class LagouSpider(Spider):
    session_url = "https://www.lagou.com/jobs/list_{0}?city=%E6%9D%AD%E5%B7%9E"
    base_url = "https://www.lagou.com/jobs/positionAjax.json?city=%E6%9D%AD%E5%B7%9E&needAddtionalResult=false"
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "DNT": "1",
            "Host": "www.lagou.com",
            "Origin": "https://www.lagou.com",
            "Referer": "https://www.lagou.com/jobs/list_{0}?labelWords=&fromSearch=true&suginput=",  
            "X-Anit-Forge-Code": "0",
            "X-Anit-Forge-Token": None,
            "X-Requested-With": "XMLHttpRequest" # 请求方式XHR
        }
    post_data = {
        "first": 'true',
        'pn': '1',
        'kd': ''
    }
    
    def __init__(self, job):
        self.job = job
        self.cookie = None
        self.query_job = urllib.parse.quote_plus(self.job.name)
        self.session_url = self.session_url.format(self.query_job)
        self.headers["Referer"] = self.headers["Referer"].format(self.query_job)
        self.post_data['kd'] = self.job.name
    
    def get_cookie(self):
        query_job = urllib.parse.quote_plus(self.job.name)
        s = requests.Session()
        s.get(self.session_url, headers=self.headers)
        cookie = s.cookies
        self.cookie = cookie
    
    def request_data(self):
        res = requests.post(self.base_url, data=self.post_data, headers=self.headers, cookies=self.cookie)
        res.raise_for_status()
        return res.json()
    
    def spide_data(self):
        try:
            self.job.status = Performing
            self.job.save()
            self.get_cookie()
            origin_data = self.request_data()
            total = origin_data["content"]["positionResult"]["totalCount"]
            self.job.total = total
            self.job.save()
            page = total // 15
            if (total % 15) > 0:
                page += 1
            print(page)
            i = 1
            while i <= page:
                try:
                    self.post_data['pn'] = i
                    res_data = self.request_data()
                    result_data = res_data["content"]["positionResult"]["result"]
                    self.batch_write_data_to_db(result_data)
                    i += 1
                except KeyError:
                    self.get_cookie()
            self.job.status = Performed
            self.job.updated_at = datetime.now()
            self.job.save()
        except Exception as e:
            print(e)
            self.job.status = NotPerformed
            self.job.save()
    
    def batch_write_data_to_db(self, datas):
        from spider.models import JobInfo
        for i in datas:
            info = JobInfo(position_id=str(i['positionId']), job_id=self.job.id, company_name=i['companyFullName'], position_name=i['positionName'],
            high_salary=int(i["salary"].split('-')[1].replace('k', '').replace('K', '')), low_salary=int(i["salary"].split('-')[0].replace('k', '').replace('K', '')), education=i["education"],
            skill_lables=i["skillLables"], company_lables=i["companyLabelList"], company_size=i["companySize"], linestaion=i["linestaion"],
            position_lables=i['positionLables'], district=i['district'], position_advantage=i['positionAdvantage'], work_year=i['workYear'])
            info.save()


# JobInfo.objects(position_id=str(i['positionId']), job_id=self.job.id).update_one(set__company_name=i['companyFullName'], set__position_name=i['positionName'],
#             set__high_salary=int(i["salary"].split('-')[1].replace('k', '').replace('K', '')), set__low_salary=int(i["salary"].split('-')[0].replace('k', '').replace('K', '')), set__education=i["education"],
#             set__skill_lables=i["skillLables"], set__company_lables=i["companyLabelList"], set__company_size=i["companySize"], set__linestaion=i["linestaion"],
#             set__position_lables=i['positionLables'], set__district=i['district'], set__position_advantage=i['positionAdvantage'], upsert=True)