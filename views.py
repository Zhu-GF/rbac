from django.shortcuts import render
from rbac import models
# Create your views here.
from rbac.permission_session_process import init_permission_session

def login(request,*args,**kwargs):
    if request.method=='GET':
        return render(request,'login.html')
    else:
        user_name=request.POST.get('username')
        user_obj=models.User.objects.filter(username=user_name).first()
        init_permission_session(request,user_obj.id)   #初始化权限信息到session中
        return render(request,'login2.html')
