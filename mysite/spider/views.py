#coding:utf-8
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import json
from mysite.exceptions import RequiredParamterMissingError
from mysite.exceptions import JobNotFoundError
from mysite.exceptions import JobAlreadyPerforming
from spider.models import Job
from spider.models import JobInfo
from spider.tasks import refresh_job_async
import unicodecsv as csv
from urllib.parse import quote
from spider.config import Performing


@require_http_methods(["POST"])
def upload_job(request):
    req = json.loads(request.body)
    if "name" not in req:
        raise RequiredParamterMissingError(msg="缺少必要参数name")
    job_name = req.get("name")
    job = Job(name=job_name)
    job.save()
    return JsonResponse({"value": [], "msg":f"添加工作查询: {job_name}成功"})

@require_http_methods(["GET"])
def refresh_job(request, job_id):
    job = Job.objects.filter(id=job_id).first()
    if not job:
        raise JobNotFoundError()
    if job.status == Performing:
        raise JobAlreadyPerforming()
    refresh_job_async.delay(job_id)
    return JsonResponse({"value": [], "msg": "后台正在刷新, 请等待"}, status=202)

@require_http_methods(["GET"])
def get_all_jobs(request):
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 20))
    offset = (page - 1) * size
    res = Job.objects.all()
    jobs = res.skip(offset).limit(size)
    total = res.count()
    return JsonResponse({"value": [each.as_dict() for each in jobs], "total": total, "msg": "获取所有成功"})

@require_http_methods(["GET"])
def get_all_infos(request):
    job_id = request.GET.get("job_id", None)
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 20))
    offset = (page - 1) * size
    query = ""
    if job_id != None:
        query =  f"job_id=job_id"
    res = eval(f"JobInfo.objects({query})").all()
    infos = res.skip(offset).limit(size)
    total = res.count()
    return JsonResponse({"value": [each.as_dict() for each in infos],"total": total, "msg": "获取所有成功"})

@require_http_methods(["GET"])
def download_job_csv(request, job_id):
    job = Job.objects.filter(id=job_id).first()
    if not job:
        raise JobNotFoundError
    infos = JobInfo.objects(job_id=job_id).all()
    response = HttpResponse(content_type='text/csv;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename={}.csv".format(quote(job.name))
    writer = csv.writer(response, encoding='utf_8_sig')
    writer.writerow(["公司名称", "职位名称", "低薪水(k)", "高薪水(k)", "学历要求", "技能要求", "职位标签", "公司福利", "公司环境", "公司规模", "区域", "详细地址"])
    for each in infos:
        row = [each.company_name, each.position_name, each.low_salary, each.high_salary, each.education, "|".join(each.skill_lables), "|".join(each.position_lables), "|".join(each.company_lables), each.position_advantage, each.company_size, each.district, each.linestaion]
        writer.writerow(row)
    return response