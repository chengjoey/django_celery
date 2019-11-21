import traceback


class ApiError(Exception):
	"""所有错误的基类"""
	msg = "Api Error"
	http_code = 500
	resource = "api"
	field = ""
	code = ""
	def __init__(self, msg=None, exc=None, resource=None, field=None, code=None):
		if resource != None:
			self.resource = resource
		if field != None:
			self.field = field
		if code != None:
			self.code = code
		if exc is None and isinstance(msg, Exception):
			msg, exc = repr(msg), msg
		self.orig_exc = exc if isinstance(exc, Exception) else None
		self.orig_traceback = traceback.format_exc()
		msg = "%s" % (msg) if msg is not None else self.msg
		self.errors = [{"resource": self.resource, "field": self.field, "code": self.code, "desc": msg}]
		super(ApiError, self).__init__(msg)

class RequiredParamterMissingError(ApiError):
	resource = "api"
	field = ""
	code = "required"
	msg = "miss required param"
	http_code = 400

class JobNotFoundError(ApiError):
	resource = "job"
	field = "job_id"
	code = "required"
	msg = "工作不存在"
	http_code = 404

class JobAlreadyPerforming(ApiError):
	resource = "job"
	field = "job_id"
	code = ""
	msg = "已在爬取数据,请勿重复提交"
	http_code = 400