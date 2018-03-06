from django import template
from django.conf import settings
import re
from django.utils.safestring import mark_safe

register=template.Library()

def menu_generater(request):
    # 获取权限及菜单列表
    menu_permission_dict=request.session.get(settings.RBAC_MENU_PERMISSION_SESSION_KEY)
    permission_list = menu_permission_dict.get(settings.RBAC_MENU_PERMISSION_KEY)
    # 所有的菜单列表
    all_menu_list = menu_permission_dict.get(settings.RBAC_MENU_KEY)

    # ------------------------------开始结构化菜单列表----------------------
    # ---------初始化数据结构字典
    # 格式{1: {'id': 1, 'caption': '菜单1', 'parent_id': None, 'opened': False, 'status': False, 'child': []}}
    all_menu_dict = {}
    for row in all_menu_list:  # 将all_menu_list 加上字段 opened，status，child
        row['opened'] = False  # s是否默认展开
        row['status'] = False  # 是否显示菜单
        row['child'] = []
        all_menu_dict[row['id']] = row
    for permission in permission_list:
        if not permission['permission__menu_id']:  # 如果权限没有菜单，则继续，比如头像上传，就不会挂靠到菜单上
            continue
        temp_item = {
            'id': permission['permission_id'],
            'caption': permission['permission__caption'],
            'parent_id': permission['permission__menu_id'],
            'opened': False,
            'status': True,
            'url': permission['permission__url']
        }
        pid = temp_item['parent_id']
        all_menu_dict[pid]['child'].append(temp_item)  # 将权限挂靠到菜单上
        if re.match(temp_item['url'], request.path_info):  # 如果当前的URL匹配，则当前的URL默认打开
            temp_item['opened'] = True
        # if re.match(temp_item['url'],'/view_info/'):     #如果当前的URL匹配，则当前的URL默认打开
        #     temp_item['opened']=True      #测试一下
        temp = pid
        # 将当前权限的父级status设置为true
        while not all_menu_dict[temp]['status']:  # 如果父级已经是true则不再循环
            all_menu_dict[temp]['status'] = True
            temp = all_menu_dict[temp]['parent_id']  # 再找上一级父亲
            if not temp:
                break
        # 将当前权限的父辈的opened改为true
        if temp_item['opened']:
            temp1 = pid
            while not all_menu_dict[temp1]['opened']:
                all_menu_dict[temp1]['opened'] = True
                temp1 = all_menu_dict[temp1]['parent_id']
                if not temp1:
                    break
    # 处理菜单之间的等级关系
    result = []
    for row in all_menu_list:
        pid = row['parent_id']
        if pid:  # 如果有parent_id 那么将其添加到all_menu_dict child字段中
            all_menu_dict[pid]['child'].append(row)
        else:  # 否则此行数据是父级数据
            result.append(row)
    return result


def menu_tree(menu_list):
    '''
    菜单树的生成
    :param menu_list:
    :return:
    '''
    tpl1 = """
                <div class='menu-item'>
                    <div class='menu-header'>{0}</div>
                    <div class='menu-body {2}'>{1}</div>
                </div>
                """
    tpl2 = """
                <a href='{0}' class='{1}'>{2}</a>
                """
    menu_str = ''
    for menu in menu_list:
        if menu.get('url'):
            menu_str += tpl2.format(menu['url'], 'active' if menu['opened'] else '', menu['caption'])
        else:
            if menu['child']:
                child_html = menu_tree(menu['child'])
            else:
                child_html = ''
            menu_str += tpl1.format(menu['caption'], child_html, '' if menu['opened'] else 'hide')
    return menu_str

@register.simple_tag
def menu_html(request):
    menu_list=menu_generater(request)
    return mark_safe(menu_tree(menu_list))

# @register.simple_tag
# def rbac_css():
#     css_text='''
#     <style>
#         .hide{
#             display: none;
#         }
#         .active{
#             color: red;
#         }
#         .menu-body{
#             margin-left: 20px;
#         }
#         .menu-body a{
#             display: block;
#         }
#     </style>
#     '''
#     return mark_safe(css_text)

# @register.simple_tag
# def rbac_js():
#     js_text='''
#         <script>
#             $(function () {
#                 $('.menu-header').click(function () {
#                     $(this).next().removeClass('hide').parent().siblings('.menu-body').addClass('hide')
#                 })
#             })
#     </script>
#     '''
#     return mark_safe(js_text)


@register.simple_tag
def rbac_css():
    import os
    css_file_path=os.path.join('rbac','theme',settings.RBAC_THEME,'rbac.css')
    if os.path.exists(css_file_path):
        return mark_safe(open(css_file_path,'r',encoding='utf-8').read())
    else:
        raise Exception('主题css文件不存在！')

@register.simple_tag
def rbac_js():
    import os
    js_file_path = os.path.join('rbac', 'theme', settings.RBAC_THEME, 'rbac.js')
    if os.path.exists(js_file_path):
        return mark_safe(open(js_file_path, 'r', encoding='utf-8').read())
    else:
        raise Exception('主题js文件不存在！')