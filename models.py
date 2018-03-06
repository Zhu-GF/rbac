from django.db import models


# Create your models here.
# 总共七张表
class User(models.Model):
    '用户表'
    username = models.CharField(verbose_name='用户名', max_length=32)
    email = models.CharField(verbose_name='邮箱', max_length=128)
    password = models.CharField(verbose_name='密码', max_length=32)

    def __str__(self):
        return self.username


class Role(models.Model):
    '角色表'
    caption = models.CharField(verbose_name='角色表', max_length=32)

    def __str__(self):
        return self.caption


class User2Role(models.Model):
    '用户和角色关系表'
    user = models.ForeignKey(to='User', verbose_name='关联用户', related_name='users')
    role = models.ForeignKey(to='Role', verbose_name='关联角色', related_name='roles')

    def __str__(self):
        return '%s-%s' % (self.user.username, self.role.caption)


class Menu(models.Model):  # 此表主要显示菜单及菜单的层级关系
    '菜单表'
    caption = models.CharField(max_length=64, verbose_name='菜单名称')
    parent = models.ForeignKey(to='Menu', related_name='parents', verbose_name='父级菜单', null=True, blank=True)

    def __str__(self):
        prev = ''
        parent = self.parent
        while True:  # 循环获取父级的名称，加入到返回到admin后台管理中去
            if parent:
                prev = prev + '-' + str(parent.caption)
                parent = parent.parent
            else:
                break
        return '%s-%s' % (prev, self.caption)


class Permission(models.Model):
    '操作权限'
    caption = models.CharField(max_length=32, verbose_name='权限名称')
    url = models.CharField(max_length=128, verbose_name='操作的URL正则')
    menu = models.ForeignKey(to='Menu', verbose_name='关联到菜单', null=True, blank=True,
                             related_name='menus')  # 权限就是URL，让其挂靠在菜单上，可以为空

    def __str__(self):
        return '%s-%s' % (self.caption, self.url)


class Action(models.Model):
    '操作方式，如增删改查等操作'
    caption = models.CharField(max_length=32, verbose_name='操作方式的标题')
    code = models.CharField(max_length=32, verbose_name='操作的方式')  # del ,get ,post等

    def __str__(self):
        return '%s-%s' % (self.caption, self.code)


class Permission2Action2Role(models.Model):
    '权限 操作方式 角色 的关系表'
    permission = models.ForeignKey(to='Permission', related_name='permissions', verbose_name='权限URL')
    action = models.ForeignKey(to='Action', related_name='actions', verbose_name='方式')
    role = models.ForeignKey(to='Role', related_name='p2as', verbose_name='角色')

    class Meta:
        unique_together = (
            ('permission', 'action', 'role'),
        )

    def __str__(self):
        return '%s-%s-%s' % (self.permission, self.action, self.role)
