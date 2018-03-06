from rbac import models
from django.conf import settings
from django.db.models import Count

def init_permission_session(request,id):
    '''
    将权限及菜单信息写入到session中
    :param request:
    :param id: 用户id
    :return:
    '''
    # 目标数据结构
    '''
    {'/url正则':['操作方式','GET','DEL','POST','ADD']}
    '''
    # -----------------------------------用户登录成功，就将权限写入session中，将以下代码封装成函数，以便调取-------------

    # 获取用户角色列表
    roles_list=models.Role.objects.filter(users__user_id=id)
    # 获取用户权限id 和方法
    permission_dict_list = models.Permission2Action2Role.objects.filter(role__in=roles_list).values('permission__url',
                                                                                                    'action__code').all().distinct()  # 由于一个人可能有多个角色，故需要去重
    # 4将数据格式进行修改
    permission_dict = {}
    for item in permission_dict_list:
        permission_dict[item['permission__url']] = []
    for item in permission_dict_list:
        permission_dict[item['permission__url']].append(item['action__code'])
    # 将用户权限信息写入到session中，用户登录成功，则去获取用户的权限，然后放入session中，当用户去访问其他url时再进行验证
    request.session[settings.RBAC_PERMISSION_SESSION_KEY] = permission_dict
    # 获取权限及菜单列表
    permission_list = list(models.Permission2Action2Role.objects.filter(role__in=roles_list).values(
        'permission_id', 'permission__url', 'permission__caption', 'permission__menu_id').annotate(c=Count('id')))
    # 所有的菜单列表
    all_menu_list = list(models.Menu.objects.values('id', 'caption', 'parent_id'))
    # 初始化权限信息的时候，将permission_list及all_menu_list写入到session
    request.session[settings.RBAC_MENU_PERMISSION_SESSION_KEY] = {
        settings.RBAC_MENU_KEY: all_menu_list,
        settings.RBAC_MENU_PERMISSION_KEY: permission_list
    }