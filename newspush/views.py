from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from newspush.models import News, NewsComment, StudentInfo
from newspush.forms import CommentForm, LoginForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.decorators.http import require_GET
from django.db.utils import OperationalError
from django.core import serializers
#import requests
import json
import re
# Create your views here.

# 验证需要改进
def commit_comment(request, news_id, stu_id):
    try:
        news_ = News.objects.get(id=news_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error news id\n')
    try:
        student_ = StudentInfo.objects.get(studentID=stu_id)
    except ObjectDoesNotExist:
        # return redirect(login) # 如果检测到没有对应的学生记录，跳转到登录界面
        return HttpResponseForbidden('Student id not recorded.\n')
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            form.save(for_news=news_, for_stu_info=student_)
            html = "<html><body>Comment succeed.</body></html>"
            return HttpResponse(html)
        else:
            return HttpResponse('Form invalid\n')

@require_GET
def fetch_comments(request, news_id):
    try:
        news_ = News.objects.get(id=news_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error news id\n')
    returned_comments = NewsComment.objects.filter(news=news_)
    response_data = serializers.serialize('json', returned_comments,
                                        #   fields=(
                                        #     'studentInfo',
                                        #     'content',
                                        #     'time',
                                        #     'ip')
                                            )
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not form.is_valid():
            return HttpResponseNotFound('Post invalid.\n')
        form_data = form.data
        post_data = {
            'zjh': form_data['scu_id'],
            'mm': form_data['password'],
        }
        s = requests.Session()
        r = s.post('http://202.115.47.141/loginAction.do', data=post_data)
        if r.ok:
            r = s.get('http://202.115.47.141/menu/s_top.jsp')
            if r.ok:
                gbk_content = r.content.decode('GBK')
                pos = re.search('欢迎光临&nbsp;', gbk_content).end()
                name_ch = gbk_content[pos]
                stu_name = ''
                while name_ch != '&':
                    stu_name += name_ch
                    pos += 1
                    name_ch = gbk_content[pos]
                stu = None
                try:
                    stu = StudentInfo.objects.get(studentID=stu_id)
                except ObjectDoesNotExist:
                    stu = StudentInfo(studentID=form_data['scu_id'])
                stu.nickname = form_data['nickname']
                stu.name = stu_name
                stu.save()
                html = "<html><body>Login succeeds./nThis guy's name is %s.</body></html>" % stu_name
                return HttpResponse(html)
            else:
                raise HttpResponseNotFound('Unknown error.\n')
        else:
            raise HttpResponseForbidden('Wrong form.\n')

def fetch_news(request,aca_id,d):
    aca_id=request.GET['aca_id']
    d=request.GET['d']

    try:
        tmp=serializers.serialize(News.objects.filter(academy=aca_id))
        response_data=serializers.serialize("json",tmp.filter(data__gte=d))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps(response_data),content_type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum

def fetch_notice(request,aca_id,d):
    aca_id = request.GET['aca_id']
    d = request.GET['d']
    try:
        tmp=serializers.serialize(Notice.objects.filter(academy=aca_id))
        response_data=serializers.serialize("json",tmp.filter(data__gte=d))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps(response_data),content_type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum

def search_news(request,keyword,aca_id,d):
    keyword=request.GET['keyword']
    aca=request.GET['academy']
    d=request.GET['date']

    try:
        tmp=serializers.serialize(News.objects.filter(academy=aca_id))
        tmp1=serializers.serialize(tmp.filter(data__gte=d))
        response_data=serializers.serialize("json",tmp1.filter(content__contains=keyword))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps(response_data),content__type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum

def search_notice(request,keyword,aca_id,d):
    keyword=request.GET['keyword']
    aca=request.GET['academy']
    d=request.GET['date']

    try:
        tmp=serializers.serialize(Notice.objects.filter(academy=aca_id))
        tmp1=serializers.serialize(tmp.filter(data__gte=d))
        response_data=serializers.serialize("json",tmp1.filter(content__contains=keyword))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')
    return HttpResponse(json.dumps(response_data),content__type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum

# To-Do
# 1. 完成视图测试
# 2. 完成名字提取
# 3. 注意中文编码
