from django.shortcuts import render, redirect
from django.http import (
    HttpResponse, HttpResponseNotFound, HttpResponseForbidden, JsonResponse
)
from newspush.models import News, NewsComment, StudentInfo, Notice
from newspush.forms import CommentForm, LoginForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.decorators.http import require_GET
from django.db.utils import OperationalError
from django.core import serializers
import requests
import json
import re
import datetime
import urllib
import os
# Create your views here.

from django.shortcuts import render_to_response
from django.template import RequestContext

def my_serialize(_from_models):
    a = []
    for k in _from_models:
        a.append(k)
    return a

def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


# def handler500(request):
#     response = render_to_response('500.html', {},
#                                   context_instance=RequestContext(request))
#     response.status_code = 500
#     return response


# 验证需要改进
def commit_comment(request, news_id, stu_id):
    try:
        news_ = News.objects.get(id=news_id)
    except ObjectDoesNotExist:
        # return HttpResponseNotFound('Error news id\n')
        return handler404(request)
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
    else:
        return handler404(request)


@require_GET
def fetch_comments(request, news_id):
    try:
        news_ = News.objects.get(id=news_id)
    except ObjectDoesNotExist:
        # return HttpResponseNotFound('Error news id\n')
        return handler404(request)
    returned_comments = NewsComment.objects.filter(news=news_)
    returned_data = returned_comments.values('studentInfo_id', 'content', 'time', 'ip')
    # return HttpResponse(json.dumps(returned_data), content_type="application/json")
    return JsonResponse(my_serialize(returned_data), safe=False)
    # return JsonResponse(serializers.serialize('json', returned_comments), safe=False)
    # response = JsonResponse(dict(genres=list(Genre.objects.values('name', 'color'))))

def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if not form.is_valid():
            print(form)
            print(form.errors)
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
                scu_id = form_data['scu_id']
                try:
                    stu = StudentInfo.objects.get(studentID=scu_id)
                except ObjectDoesNotExist:
                    stu = StudentInfo(studentID=scu_id)
                stu.nickname = form_data['nickname']
                stu.name = stu_name
                stu.save()
                html = "<html><body>Login succeeds./nThis guy's name is %s.</body></html>" % stu_name
                return HttpResponse(html)
            else:
                return HttpResponseNotFound('Unknown error.\n')
        else:
            return HttpResponseForbidden('Wrong id with password.\n')
    else:
        # return HttpResponseNotFound('What are you doing?\n')
        return handler404(request)

def logout(request, scu_id):
    try:
        StudentInfo.objects.get(studentID=scu_id).delete()
        return HttpResponse('Logout succeeds.')
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Not recoreded student.\n')
def fetch_news(request,aca_id,d):
    try:
        y=int(d[0:4])
        m=int(d[4:6])
        da=int(d[6:8])
        response_tmp=News.objects.filter(academy__id=aca_id)
        if d!='00000000':
            response_tmp=response_tmp.filter(time__year=y)
            response_tmp=response_tmp.filter(time__month=m)
            response_tmp=response_tmp.filter(time__day=da)
        if len(response_tmp)==0:
           return HttpResponseNotFound('there is no such information\n')
        url=response_tmp[0].sourceURL+"/"
        l=len(response_tmp)
        response_data=[]
        for index in range(l):
           tmp="%s%d"%(url,response_tmp[index].id)+".json"
           li = open(tmp)
           response_data.append(json.load(li))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps
	(response_data),content_type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum

def fetch_notice(request,aca_id,d):
    try:
        y=int(d[0:4])
        m=int(d[4:6])
        da=int(d[6:8])
        response_tmp=Notice.objects.filter(academy__id=aca_id)
        if d!='00000000':
            response_tmp=response_tmp.filter(time__year=y)
            response_tmp=response_tmp.filter(time__month=m)
            response_tmp=response_tmp.filter(time__day=da)
        if len(response_tmp)==0:
           return HttpResponseNotFound('there is no such information\n')
        url=response_tmp[0].sourceURL+"/"
        l=len(response_tmp)
        response_data=[]
        for index in range(l):
           tmp="%s%d"%(url,response_tmp[index].id)+".json"
           li = open(tmp)
           response_data.append(json.load(li))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps
	(response_data),content_type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum

def search_news(request,aca_id,keyword):
    try:
        response_tmp=News.objects.filter(title__contains=keyword)
        if aca_id!='0':
            response_tmp=response_tmp.filter(academy__id=aca_id)
        if len(response_tmp)==0:
           return HttpResponseNotFound('there is no such information\n')
        url=response_tmp[0].sourceURL+"/"
        l=len(response_tmp)
        response_data=[]
        for index in range(1):
           tmp="%s%d"%(url,response_tmp[index].id)+".json"
           li = open(tmp)
           response_data.append(json.load(li))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps
	(response_data),content_type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum

def search_notice(request,aca_id,keyword):
    try:
        response_tmp=Notice.objects.filter(title__contains=keyword)
        if aca_id!='0':
            response_tmp=response_tmp.filter(academy__id=aca_id)
        if len(response_tmp)==0:
           return HttpResponseNotFound('there is no such information\n')
        url=response_tmp[0].sourceURL+"/"
        l=len(response_tmp)
        response_data=[]
        for index in range(l):
           response_data.append(json.load(li))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps
	(response_data),content_type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum
def fetch_new_news(request,aca_id,notice_id):
    try:
        response_tmp1=News.objects.filter(academy__id=aca_id)
        response_tmp1=response_tmp1.filter(id__lt=notice_id)
        response_tmp1=sorted(response_tmp1,key=lambda Notice:Notice.time)
        response_tmp=[]
        length=len(response_tmp1)
        flag=0
        while(flag<10 and (length-flag>0)):
            response_tmp.append(response_tmp1[length-flag-1])
            flag=flag+1
        #response_tmp1=response_tmp1.filter(id__let=notice_id)
        if len(response_tmp)==0:
           return HttpResponseNotFound('there is no such information\n')
        url=response_tmp[0].sourceURL+"/"
        l=len(response_tmp)
        response_data=[]
        for index in range(l):
           tmp="%s%d"%(url,response_tmp[index].id)+".json"
           li = open(tmp)
           response_data.append(json.load(li))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps
	(response_data),content_type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum
def fetch_new_notice(request,aca_id,notice_id):
    try:
        response_tmp1=Notice.objects.filter(academy__id=aca_id)
        response_tmp1=response_tmp1.filter(id__lt=notice_id)
        response_tmp1=sorted(response_tmp1,key=lambda Notice:Notice.time)
        response_tmp=[]
        length=len(response_tmp1)
        flag=0
        while(flag<10 and (length-flag>0)):
            response_tmp.append(response_tmp1[length-flag-1])
            flag=flag+1
        #response_tmp1=response_tmp1.filter(id__let=notice_id)
        if len(response_tmp)==0:
           return HttpResponseNotFound('there is no such information\n')
        url=response_tmp[0].sourceURL+"/"
        l=len(response_tmp)
        response_data=[]
        for index in range(l):
           tmp="%s%d"%(url,response_tmp[index].id)+".json"
           li = open(tmp)
           response_data.append(json.load(li))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('Error, object does not exsit\n')

    return HttpResponse(json.dumps
	(response_data),content_type="application/json")
	#academy title time sourceURL picURL_Path originURL accessNum

# To-Do
# 1. 完成视图测试
# 2. 完成名字提取[完成]
# 3. 注意中文编码
# 4. 潜在安全问题，考虑加密用户名传输
