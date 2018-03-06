from django.middleware.security import MiddlewareMixin
from django.shortcuts import HttpResponse
import re
from django.conf import settings
class RbacMiddleware(MiddlewareMixin):
    def process_request(self, request,*args,**kwargs):
        '用户访问本URL，则进行验证该用户的session中有没权限（URL，方法）'
        # 用户进入访问的格式为  http://127.0.0.1:8000/test/?md=GET
        # ------------------------------------封装成中间件，每次访问时必须经过此处进行验证--------------------
        for pattern in settings.RBAC_NO_AUTH_URL:       #如果匹配成功，则不需要验证，
            if re.match(pattern,request.path_info):
                return None
        #获取当前用户的session中的权限信息
        permission_dict = request.session.get(settings.RBAC_PERMISSION_SESSION_KEY)
        if not permission_dict:  #如果没有权限信息，则返回提示信息
            return HttpResponse(settings.RBAC_PERMISSION_MSG)
        #当前的url与session中的权限信息进行比对
        flag=False
        for key, value in permission_dict.items():
            upper_code_list=[item.upper() for item in value]
            if re.match(key, request.path_info):
                request_permission_code = request.GET.get(settings.RBAC_QUERY_KEY,settings.RBAC_DEFAULT_QUERY_KEY_VALUE).upper()  # 获取当前用户访问url时get传参数的方法，GET，DEL，POST，ADD，EDIT等自己定义的访问方法
                if request_permission_code in upper_code_list:
                    request.request_permission_code=request_permission_code
                    #匹配成功将权限操作方式写入到request中即request.request_permission_code="GET
                    request.permission_code_list=upper_code_list             #匹配成功将权限操作列表也写入到request中
                    flag = True
                    break
        if not flag:
            return HttpResponse(settings.RBAC_PERMISSION_MSG)



        # url_visiting = request.path_info  # 当前用户访问的url
        # print(request.path_info, '当前用户访问的url')
        # print(request.GET.get('md'))
        # # 权限验证
        # valid = ['/login', '/index']  # 设置一个列表，内容为不需要进行权限验证的url
        # if url_visiting not in valid:
        #     md = request.GET.get('md')  # 获取当前用户访问url时get传参数的方法，GET，DEL，POST，ADD，EDIT等自己定义的访问方法
        #     permission_dict = request.session.get('permission_dict')
        #     if not permission_dict:
        #         return HttpResponse('无权限访问-------------')
        #     flag = False
        #     for key, value in permission_dict.items():
        #         if re.match(key, url_visiting):
        #             if md in value:
        #                 flag = True
        #                 break
        #     if not flag:
        #         return HttpResponse('无权限访问-------------')