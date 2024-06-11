from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password,check_password
import traceback
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from django.utils import timezone
import json

# 可以通过 命令 python  manage.py createsuperuser 来创建超级管理员
# 就是在这User表中添加记录
class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)

    # 用户类型  
    # 1： 超管 | 1000： 普通管理员  | 2000：学生  |  3000： 老师 
    usertype = models.PositiveIntegerField()

    # 真实姓名
    realname = models.CharField(max_length=30, db_index=True)

    # 学号
    studentno = models.CharField(
        max_length=10,  
        db_index=True, 
        null=True, blank=True
        )

    # 备注描述
    desc = models.CharField(max_length=500, null=True, blank=True)

    REQUIRED_FIELDS = ['usertype', 'realname']

    class Meta:
        db_table = "cimp_user"
    
    
    @staticmethod # 静态方法不需要实例化就能调用  
    def addone(data):
        try:
            user = User.objects.create(
                username = data['username'],
                password = make_password(data['password']),
                usertype = data['usertype'],
                realname = data['realname'],
                studentno = data['studentno'],
                desc = data['desc']
            )
            
            return {'ret':0, 'id': user.id}
        
        except:
            err = traceback.format_exc()
            return {'ret':2, 'msg': err}
        
        
    @staticmethod 
    def listbypage(pagenum, pagesize, keywords):
        try:
            qs = User.objects.values('id', 
                                     'username', 
                                     'realname', 
                                     'studentno', 
                                     'desc', 
                                     'usertype')\
                .order_by('-id') # 这样排序最先添加的就在最前面
            # 查看是否有 关键字 搜索 参数
            if keywords:
                conditions = [Q(username__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)

            # 使用分页对象，设定每页多少条记录
            pgnt = Paginator(qs, pagesize)

            # 从数据库中读取数据，指定读取其中第几页
            page = pgnt.page(pagenum)

            # 将 QuerySet 对象 转化为 list 类型
            retlist = list(page)

            # total指定了 一共有多少数据
            return {'ret': 0, 'items': retlist,'total': pgnt.count, 'keywords': keywords}
        
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': keywords}
        
        except:
            err = traceback.format_exc()
            return {'ret':2, 'msg': err}
    
    @staticmethod 
    def modifyone(oid, newdata):
        try:
            user = User.objects.get(id=oid)
            
            if 'username' in newdata:
                username = newdata['username']
                if User.objects.filter(username=username).exists():
                    return {'ret':3, 'msg':f'登录名为{username}的用户已存在'}
            
            if 'password' in newdata:
                # 把密码从字典里删掉就不会在后面的循环里被覆盖了
                user.password = make_password(newdata.pop('password')) 
                
            for field, value in newdata.items():
                setattr(user, field, value)
            
            user.save()
            
            return {'ret':0}
        
        except User.DoesNotExist:
            return {'ret': 1, 'msg':f'id为{oid}的用户不存在'}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod # 静态方法不需要实例化就能调用  
    def deleteone(oid):
        try:
            user = User.objects.get(id=oid)
            
            user.delete()
            
            return {'ret': 0}
        
        except User.DoesNotExist:
            return {'ret': 1, 'msg':f'id为{oid}的用户不存在'}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

# 通知管理，用来 列出、添加、删除、封禁、发布系统中的通知       
class Notice(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    
    # 创建时间，为iso格式
    pubdate = models.DateTimeField(default=timezone.now)
    
    # 创建者的id，使用外键与 User 模型的 id 字段关联
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'notice')
    
    # 创建者的真实姓名，直接从关联的 User 模型中获取
    author_realname = models.CharField(max_length=30, db_index=True)
    
    title = models.CharField(max_length=1000)
    
    # 通知的内容，如果请求参数中withoutcontent值为true，则没有该字段
    content = models.TextField()
    
    # 通知的状态。 正常发布状态：1， 撤回状态：2，封禁状态：3
    status = models.PositiveIntegerField() 
    
    # 为了确保author_realname字段保持最新，可以使用save方法来更新它
    # def save(self, *args, **kwargs):
    #     if self.author:
    #         self.author_realname = self.author.realname
    #     super().save(self, *args, **kwargs)
    
    @staticmethod
    def addone(data, author):
        try:
            notice = Notice.objects.create(
                pubdate = data['pubdate'],
                author = author,
                author_realname = data['author_realname'],
                title = data["title"],
                content = data["content"],
                status = data['status']
            )
            
            return {'ret': 0, 'id': notice.id}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
            
    @staticmethod
    def listbypage(pagenum, pagesize, keywords, withoutcontent):
        try:
            qs = Notice.objects.values("id",
                                        "pubdate",
                                        "author",
                                        "author_realname",
                                        "title",
                                        "content",
                                        "status"
            )
            
            # 筛选发布状态为1的query set
            qs = qs.filter(status=1)
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            if withoutcontent:
                return {"ret": 0, "items": [], "total": pgnt.count, 'keywords': keywords}
            else:
                return {"ret": 0, "items": retlist, "total": pgnt.count, 'keywords': keywords}
           
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': ""}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err} 
        
    @staticmethod
    def listbypage_allstate(pagenum, pagesize, keywords, withoutcontent):
        try:
            qs = Notice.objects.values("id",
                                        "pubdate",
                                        "author",
                                        "author_realname",
                                        "title",
                                        "content",
                                        "status"
            )
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            if withoutcontent:
                return {"ret": 0, "items": [], "total": pgnt.count, 'keywords': keywords}
            else:
                return {"ret": 0, "items": retlist, "total": pgnt.count, 'keywords': keywords}
           
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': ""}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err} 
        
    @staticmethod
    def getone(notice_id):
        try:
            qs = Notice.objects.values("id",
                                        "pubdate",
                                        "author",
                                        "author_realname",
                                        "title",
                                        "content",
                                        "status"
            )
            
            # 返回查询集中的第一个对象，或者如果查询集为空，则返回 None。first是一个快捷方法，用于从查询集中获取单个对象，而无需进行完整的迭代。
            qs = qs.filter(id=notice_id).first()
            
            return {'ret': 0, 'rec': qs}
            
        except Notice.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{notice_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def modifyone(notice_id, new_data):
        try:
            notice = Notice.objects.get(id=notice_id)
            
            for field, value in new_data.items():
                setattr(notice, field, value)
                
            notice.save()
            
            return {'ret': 0}
            
        except Notice.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{notice_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def banone(notice_id):
        try:
            notice = Notice.objects.get(id=notice_id)
            
            notice.status = 3
                
            notice.save()
            
            return {'ret': 0, 'status': 3}
            
        except Notice.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{notice_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def publishone(notice_id):
        try:
            notice = Notice.objects.get(id=notice_id)
            
            if notice.status == 3:
                notice.status = 1
                
            notice.save()
            
            return {'ret': 0, 'status': 1}
            
        except Notice.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{notice_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def deleteone(notice_id):
        try:
            notice = Notice.objects.get(id=notice_id)
                
            notice.delete()
            
            return {'ret': 0}
            
        except Notice.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{notice_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
               
# 新闻管理，用来 列出、添加、删除、封禁、发布系统中的新闻      
class News(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    
    # 创建时间，为iso格式
    pubdate = models.DateTimeField(default=timezone.now)
    
    # 创建者的id，使用外键与 User 模型的 id 字段关联
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'news')
    
    # 创建者的真实姓名，直接从关联的 User 模型中获取
    author_realname = models.CharField(max_length=30, db_index=True)
    
    title = models.CharField(max_length=1000)
    
    # 新闻的内容，如果请求参数中withoutcontent值为true，则没有该字段
    content = models.TextField()
    
    # 新闻的状态。 正常发布状态：1， 撤回状态：2，封禁状态：3
    status = models.PositiveIntegerField()
    
    @staticmethod
    def addone(data, author):
        try:
            notice = News.objects.create(
                pubdate = data['pubdate'],
                author = author,
                author_realname = data['author_realname'],
                title = data["title"],
                content = data["content"],
                status = data['status']
            )
            
            return {'ret': 0, 'id': notice.id}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
            
    @staticmethod
    def listbypage(pagenum, pagesize, keywords, withoutcontent):
        try:
            qs = News.objects.values("id",
                                        "pubdate",
                                        "author",
                                        "author_realname",
                                        "title",
                                        "content",
                                        "status"
            )
            
            # 筛选发布状态为1的query set
            qs = qs.filter(status=1)
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            if withoutcontent:
                return {"ret": 0, "items": [], "total": pgnt.count, 'keywords': keywords}
            else:
                return {"ret": 0, "items": retlist, "total": pgnt.count, 'keywords': keywords}
           
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': ""}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err} 
        
    @staticmethod
    def listbypage_allstate(pagenum, pagesize, keywords, withoutcontent):
        try:
            qs = News.objects.values("id",
                                        "pubdate",
                                        "author",
                                        "author_realname",
                                        "title",
                                        "content",
                                        "status"
            )
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            if withoutcontent:
                return {"ret": 0, "items": [], "total": pgnt.count, 'keywords': keywords}
            else:
                return {"ret": 0, "items": retlist, "total": pgnt.count, 'keywords': keywords}
           
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': ""}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err} 
        
    @staticmethod
    def getone(news_id):
        try:
            qs = News.objects.values("id",
                                        "pubdate",
                                        "author",
                                        "author_realname",
                                        "title",
                                        "content",
                                        "status"
            )
            
            # 返回查询集中的第一个对象，或者如果查询集为空，则返回 None。first是一个快捷方法，用于从查询集中获取单个对象，而无需进行完整的迭代。
            qs = qs.filter(id=news_id).first()
            
            return {'ret': 0, 'rec': qs}
            
        except Notice.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{news_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def modifyone(news_id, new_data):
        try:
            news = News.objects.get(id=news_id)
            
            for field, value in new_data.items():
                setattr(news, field, value)
                
            news.save()
            
            return {'ret': 0}
            
        except News.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{news_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def banone(news_id):
        try:
            news = News.objects.get(id=news_id)
            
            news.status = 3
                
            news.save()
            
            return {'ret': 0, 'status': 3}
            
        except News.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{news_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def publishone(news_id):
        try:
            news = News.objects.get(id=news_id)
            
            if news.status == 3:
                news.status = 1
                
            news.save()
            
            return {'ret': 0, 'status': 1}
            
        except News.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{news_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def deleteone(news_id):
        try:
            news = News.objects.get(id=news_id)
            
            news.delete()
            
            return {'ret': 0}
            
        except News.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{news_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
# 论文管理，用来列出、添加、删除、封禁、发布、撤回系统中的论文。
class Paper(models.Model):
    id = models.BigAutoField(primary_key=True)
    pubdate = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paper')
    author_realname = models.CharField(max_length=30, db_index=True)
    title = models.CharField(max_length=1000)
    content = models.TextField()
    # 论文点赞数量
    thumbupcount = models.PositiveBigIntegerField(default=0)
    # 论文的状态。 正常发布状态：1， 撤回状态：2，封禁状态：3
    status = models.PositiveIntegerField()
    
    @staticmethod
    def addone(data, author):
        try:
            Paper.objects.create(
                                pubdate = data['pubdate'],
                                author = author,
                                author_realname = data['author_realname'],
                                title = data['title'],
                                content = data['content'],
                                status = data['status'])
            return {'ret': 0, 'id': author.id}
        except:
            err = traceback.format_exc
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def getone(paper_id):
        try:
            qs = Paper.objects.values("id",
                                        "pubdate",
                                        "author",
                                        "author_realname",
                                        "title",
                                        "content",
                                        "status"
            )
            
            # 返回查询集中的第一个对象，或者如果查询集为空，则返回 None。first是一个快捷方法，用于从查询集中获取单个对象，而无需进行完整的迭代。
            qs = qs.filter(id=paper_id).first()
            
            return {'ret': 0, 'rec': qs}
            
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{paper_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    
    @staticmethod
    def listbypage(pagesize, pagenum, keywords, withoutcontent):
        try:
            qs = Paper.objects.values("id",
                                      "pubdate",
                                      "author",
                                      "author_realname",
                                      "title",
                                      "content",
                                      "thumbupcount",
                                      "status"
                                      )
            
            qs = qs.filter(status=1)
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(" ") if one]
                query = Q()
                
                for condition in conditions:
                    query &= condition
                
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            if withoutcontent:
                return {'ret': 0, 'items': [], 'total': pgnt.count, 'keywords': ""}
                
            return {'ret': 0, 'items': retlist, 'total': pgnt.count, 'keywords': ""}
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': ""}
        except:
            err = traceback.format_exc
            return {'ret': 2, 'msg': err}

    @staticmethod
    def listbypage_allstate(pagesize, pagenum, keywords, withoutcontent):
        try:
            qs = Paper.objects.values("id",
                                      "pubdate",
                                      "author",
                                      "author_realname",
                                      "title",
                                      "content",
                                      "thumbupcount",
                                      "status"
                                      )
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(" ") if one]
                query = Q()
                
                for condition in conditions:
                    query &= condition
                
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            if withoutcontent:
                return {'ret': 0, 'items': [], 'total': pgnt.count, 'keywords': ""}
                
            return {'ret': 0, 'items': retlist, 'total': pgnt.count, 'keywords': ""}
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': ""}
        except:
            err = traceback.format_exc
            return {'ret': 2, 'msg': err}    
    
    @staticmethod
    def listminebypage(current_user, pagesize, pagenum, keywords, withoutcontent):
        try:
            qs = Paper.objects.values("id",
                                      "pubdate",
                                      "author",
                                      "author_realname",
                                      "title",
                                      "content",
                                      "thumbupcount",
                                      "status"
                                      )
            qs = qs.filter(author=current_user)
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(" ") if one]
                query = Q()
                
                for condition in conditions:
                    query &= condition
                
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            if withoutcontent:
                return {'ret': 0, 'items': [], 'total': pgnt.count, 'keywords': ""}
                
            return {'ret': 0, 'items': retlist, 'total': pgnt.count, 'keywords': ""}
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': ""}
        except:
            err = traceback.format_exc
            return {'ret': 2, 'msg': err}       
    
    
    @staticmethod
    def modifyone(paper_id, newdata, current_user):
        try:
            paper = Paper.objects.get(id=paper_id)
            
            if paper.author != current_user:
                return {'ret': 2, 'msg': '仅限论文作者修改'}
            
            for field, value in newdata:
                setattr(paper, field, value)
            
            paper.save()
            
            return {'ret': 0}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{paper_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def holdone(paper_id, current_user):
        try:
            paper = Paper.objects.get(id=paper_id)
            
            if paper.author != current_user:
                return {'ret': 2, 'msg': '仅限论文作者撤回'}
            
            paper.status = 2
            
            paper.save()
            
            return {'ret': 0, 'status': 2}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{paper_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def banone(paper_id):
        try:
            paper = Paper.objects.get(id=paper_id)
            
            paper.status = 3
            
            paper.save()
            
            return {'ret': 0, 'status': 3}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{paper_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def publishone(paper_id, current_user):
        try:
            paper = Paper.objects.get(id=paper_id)
            
            if paper.author != current_user and current_user.is_staff == False:
                return {'ret': 2, 'msg': '仅限管理员用户和论文作者解禁论文'}
            
            paper.status = 1
            
            paper.save()
            
            return {'ret': 0, 'status': 1}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{paper_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def deleteone(paper_id, current_user):
        try:
            paper = Paper.objects.get(id=paper_id)
            
            if paper.author != current_user and current_user.is_staff == False:
                return {'ret': 2, 'msg': '仅限管理员用户和论文作者删除论文'}
            
            paper.delete()
            
            return {'ret': 0}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'id为{paper_id}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
   
# 首页设置，用来获取、设置显示在网站首页的信息
class Config(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    
    @staticmethod
    def set(data):
        try:
            Config.objects.create(name=data['name'],
                                value=data['value']
            )
            return {'ret': 0}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def get(name):
        try:
            config = Config.objects.get(name=name)
            return {'ret': 0, 'value': config.value}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    def gethomepagebyconfig(self):
        try:
            config = Config.objects.get(name='homepage')
            value = json.loads(config.value)
            news_ids = value.get('news', [])
            notice_ids = value.get('notice', [])
            paper_ids = value.get('paper', [])
            
            news_list = list(News.objects.filter(id__in=news_ids, status=1).values("id",
                                                                            "pubdate",
                                                                            "author",
                                                                            "author_realname",
                                                                            "title",
                                                                            "status"))
            notice_list = list(Notice.objects.filter(id__in=notice_ids, status=1).values("id",
                                                                            "pubdate",
                                                                            "author",
                                                                            "author_realname",
                                                                            "title",
                                                                            "status"))
            paper_list = list(Paper.objects.filter(id__in=paper_ids, status=1).values("id",
                                                                            "pubdate",
                                                                            "author",
                                                                            "author_realname",
                                                                            "title",
                                                                            "status"))
            info = {'news': self.listbyid(news_list, news_ids), 'notice': self.listbyid(notice_list, notice_ids), 'paper': self.listbyid(paper_list, paper_ids)}
                       
            return {'ret': 0, 'info': info}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    def listbyid(self, items, ids):
        dic = {one['id']: one for one in items}
        return [dic[id] for id in ids if id in dic]

# 个人设置， 用来获取、设置个人信息
class Profile(models.Model):
    # 学生设置的老师
    teacherid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_profile')
    # 学生本人
    studentid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_profile')
    
    @staticmethod
    def setmyprofile(data, current_user):
        try:
            if 'password' in data:
                current_user.password = make_password(data['password'])
            if 'realname' in data:
                current_user.realname = data['realname']
            
            current_user.save()
            
            # 如果是老师登录
            if current_user.usertype == 3000:            
                return {'ret': 0}
            
            # 如果是学生登录
            if current_user.usertype == 2000:
                if 'tearcherid' in data:
                    Profile.objects.update_or_create(teacherid=data['teacherid'], 
                                            studentid=current_user.id)
                    
                return {'ret': 0}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
    
    @staticmethod
    def getmyprofile(current_user):
        try:
            profile_user = current_user.values("userid",
                                            "username",
                                            "usertype",
                                            "realname")
            # 如果是老师
            if current_user.usertype == 3000:
                return {'ret': 0, 'profile': profile_user}
                
            # 如果是学生
            elif current_user.usertype == 2000:
                profile = Profile.objects.get(studentid=current_user.id)
                if profile:
                    profile_user["teacher"] = {"id": profile.teacherid,
                                                "realname": current_user.realname}
                else:
                    profile_user["teacher"] = {
                                                    "id": -1,
                                                    "realname": "尚未设置"}
                return {'ret': 0, 'profile': profile_user}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def listteachers(keywords):
        try:
            qs = User.objects.filter(usertype=3000).values("id", "realname")
            
            if keywords:
                conditions = [Q(realname__contains=one) for one in keywords.split(" ") if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
            if qs.count() > 30:
                qs = qs[:30]
            retlist = list(qs)
            
            return {"ret": 0, "items":retlist, "total": qs.count(), "keyword": keywords}
                
            
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def thumbuporcancel(paperid):
        pass