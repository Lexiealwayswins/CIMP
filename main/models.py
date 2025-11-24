from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
import traceback
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from django.utils import timezone
import json

# You can create a superuser via command: python manage.py createsuperuser
# This adds a record to this User table
class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)

    # User Type
    # 1: Super Admin | 1000: Admin | 2000: Student | 3000: Teacher
    usertype = models.PositiveIntegerField()

    # Real Name
    realname = models.CharField(max_length=30, db_index=True)

    # Student Number
    studentno = models.CharField(
        max_length=10,  
        db_index=True, 
        null=True, blank=True
        )

    # Description / Remarks
    desc = models.CharField(max_length=500, null=True, blank=True)

    REQUIRED_FIELDS = ['usertype', 'realname']

    class Meta:
        db_table = "cimp_user"
    
    
    @staticmethod 
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
            
            return {'ret': 0, 'id': user.id}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
        
    @staticmethod 
    def listbypage(pagenum, pagesize, keywords):
        try:
            qs = User.objects.values('id', 
                                     'username', 
                                     'realname', 
                                     'studentno', 
                                     'desc', 
                                     'usertype')\
                .order_by('-id') # Order by ID descending (newest first)
            
            # Check for keyword search parameters
            if keywords:
                conditions = [Q(username__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)

            # Use Paginator
            pgnt = Paginator(qs, pagesize)

            # Read specific page from database
            page = pgnt.page(pagenum)

            # Convert QuerySet to list
            retlist = list(page)

            return {'ret': 0, 'items': retlist,'total': pgnt.count, 'keywords': keywords}
        
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': keywords}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
    
    @staticmethod 
    def modifyone(oid, newdata):
        try:
            user = User.objects.get(id=oid)
            
            if 'username' in newdata:
                username = newdata['username']
                if User.objects.filter(username=username).exists():
                    return {'ret': 3, 'msg': f'Username {username} already exists'}
            
            if 'password' in newdata:
                # Pop password to prevent overwriting in the loop below
                user.password = make_password(newdata.pop('password')) 
                
            for field, value in newdata.items():
                setattr(user, field, value)
            
            user.save()
            
            return {'ret': 0}
        
        except User.DoesNotExist:
            return {'ret': 1, 'msg': f'User with id {oid} does not exist'}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod 
    def deleteone(oid):
        try:
            user = User.objects.get(id=oid)
            
            user.delete()
            
            return {'ret': 0}
        
        except User.DoesNotExist:
            return {'ret': 1, 'msg': f'User with id {oid} does not exist'}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

# Notice Management: List, Add, Delete, Ban, Publish notices
class Notice(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    
    # Creation time, ISO format
    pubdate = models.DateTimeField(default=timezone.now)
    
    # Author ID, ForeignKey to User
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notice')
    
    # Author Real Name
    author_realname = models.CharField(max_length=30, db_index=True)
    
    title = models.CharField(max_length=1000)
    
    # Content. If 'withoutcontent' is true in request, this field is omitted
    content = models.TextField()
    
    # Status: 1: Published, 2: Withdrawn, 3: Banned
    status = models.PositiveIntegerField() 
    
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
            
            # Filter for published status (1)
            qs = qs.filter(status=1)
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
            
            # Order by ID descending
            qs = qs.order_by('-id')

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
                
            qs = qs.order_by('-id')
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
            
            qs = qs.filter(id=notice_id).first()
            
            return {'ret': 0, 'rec': qs}
            
        except Notice.DoesNotExist:
            return {'ret': 1, 'msg': f'Notice with id {notice_id} does not exist'}
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
            return {'ret': 1, 'msg': f'Notice with id {notice_id} does not exist'}
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
            return {'ret': 1, 'msg': f'Notice with id {notice_id} does not exist'}
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
            return {'ret': 1, 'msg': f'Notice with id {notice_id} does not exist'}
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
            return {'ret': 1, 'msg': f'Notice with id {notice_id} does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
               
# News Management: List, Add, Delete, Ban, Publish news
class News(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    pubdate = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')
    author_realname = models.CharField(max_length=30, db_index=True)
    title = models.CharField(max_length=1000)
    content = models.TextField()
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
            
            qs = qs.filter(status=1)
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
            
            qs = qs.order_by('-id')
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
            
            qs = qs.order_by('-id')
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
            
            qs = qs.filter(id=news_id).first()
            
            return {'ret': 0, 'rec': qs}
            
        except Notice.DoesNotExist:
            return {'ret': 1, 'msg': f'News with id {news_id} does not exist'}
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
            return {'ret': 1, 'msg': f'News with id {news_id} does not exist'}
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
            return {'ret': 1, 'msg': f'News with id {news_id} does not exist'}
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
            return {'ret': 1, 'msg': f'News with id {news_id} does not exist'}
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
            return {'ret': 1, 'msg': f'News with id {news_id} does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
# Paper Management: List, Add, Delete, Ban, Publish, Withdraw papers
class Paper(models.Model):
    id = models.BigAutoField(primary_key=True)
    pubdate = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paper')
    author_realname = models.CharField(max_length=30, db_index=True)
    title = models.CharField(max_length=1000)
    content = models.TextField()
    # Thumb up count
    thumbupcount = models.PositiveBigIntegerField(default=0)
    # Status: 1: Published, 2: Withdrawn, 3: Banned
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
            
            qs = qs.filter(id=paper_id).first()
            
            return {'ret': 0, 'rec': qs}
            
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'Paper with id {paper_id} does not exist'}
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
            
            qs = qs.order_by('-id')
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
            
            qs = qs.order_by('-id')
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
            
            qs = qs.order_by('-id')
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
                return {'ret': 2, 'msg': 'Only the author can modify the paper'}
            
            for field, value in newdata:
                setattr(paper, field, value)
            
            paper.save()
            
            return {'ret': 0}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'Paper with id {paper_id} does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def holdone(paper_id, current_user):
        try:
            paper = Paper.objects.get(id=paper_id)
            
            if paper.author != current_user:
                return {'ret': 2, 'msg': 'Only the author can withdraw the paper'}
            
            paper.status = 2
            
            paper.save()
            
            return {'ret': 0, 'status': 2}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'Paper with id {paper_id} does not exist'}
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
            return {'ret': 1, 'msg': f'Paper with id {paper_id} does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def publishone(paper_id, current_user):
        try:
            paper = Paper.objects.get(id=paper_id)
            
            if paper.author != current_user and current_user.is_staff == False:
                return {'ret': 2, 'msg': 'Only Admin and Author can publish the paper'}
            
            paper.status = 1
            
            paper.save()
            
            return {'ret': 0, 'status': 1}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'Paper with id {paper_id} does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def deleteone(paper_id, current_user):
        try:
            paper = Paper.objects.get(id=paper_id)
            
            if paper.author != current_user and current_user.is_staff == False:
                return {'ret': 2, 'msg': 'Only Admin and Author can delete the paper'}
            
            paper.delete()
            
            return {'ret': 0}
    
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'Paper with id {paper_id} does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
   
# Homepage Config
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

# Personal Profile Settings
class Profile(models.Model):
    # Teacher set by student
    teacherid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_profile')
    # Student
    studentid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_profile')
    
    @staticmethod
    def setmyprofile(data, current_user):
        try:
            if 'password' in data:
                current_user.password = make_password(data['password'])
            if 'realname' in data:
                current_user.realname = data['realname']
            
            current_user.save()
            
            # If teacher
            if current_user.usertype == 3000:            
                return {'ret': 0}
            
            # If student
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
            # If teacher
            if current_user.usertype == 3000:
                return {'ret': 0, 'profile': profile_user}
                
            # If student
            elif current_user.usertype == 2000:
                profile = Profile.objects.get(studentid=current_user.id)
                if profile:
                    profile_user["teacher"] = {"id": profile.teacherid,
                                                "realname": current_user.realname}
                else:
                    profile_user["teacher"] = {
                                                    "id": -1,
                                                    "realname": "Not Set"}
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
            
            return {"ret": 0, "items": retlist, "total": qs.count(), "keyword": keywords}
                
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

        
class Thumbup(models.Model):
    paper_id = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name = 'thumbup')
    thumbuper = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'thumbuper')
    thumbup = models.BooleanField(default=False)
    
    @staticmethod
    def thumbuporcancel(paper_id, current_user):
        try:
            thumbup = Thumbup.objects.get(id=paper_id, thumbuper=current_user)
            paper = Paper.objects.get(id=paper_id)
            if thumbup.thumbup == True:
                thumbup.thumbup = False
                paper.thumbupcount -= 1
            else:
                thumbup.thumbup = True
                paper.thumbupcount += 1               
            
            thumbup.save()
            paper.save()
        
            return {"ret": 0, "thumbupcount": paper.thumbupcount}
        except Paper.DoesNotExist:
            return {'ret': 1, 'msg': f'Paper with id {paper_id} does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
        
class GraduateDesign(models.Model):
    
    id = models.BigAutoField(primary_key=True)

    # Creator (Student), ForeignKey to User
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'GraduateDesign')
    
    # Creator's real name
    creator_realname = models.CharField(max_length=30, db_index=True)
    
    title = models.CharField(max_length=1000)
    
    # Current State (Default: Topic Created)
    currentstate = models.CharField(max_length=200, default='Topic Created')
    
    # Creation date
    createdate = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = "cimp_graduatedesign"
        
    # =========================================================
    #               Workflow Configuration (Core Logic)
    # =========================================================
    
    # Permission Constants
    PERMISSION_STUDENT = 1              # Any student (usertype=2000)
    PERMISSION_CREATOR = 2              # Creator only
    PERMISSION_TEACHER_OF_CREATOR = 3   # Creator's teacher only (usertype=3000)
    PERMISSION_ADMIN = 4                # Admin

    # State Machine Rules
    WF_RULE = {
        "Start": {
            "actions": {
                "create_topic": {
                    "name": "Create Topic",
                    "submitdata": [
                        {"name": "Graduate Design Title", "type": "text", "check_string_len": [1, 50]},
                        {"name": "Topic Description", "type": "richtext", "check_string_len": [10, 10000]},
                    ],
                    "whocan": PERMISSION_STUDENT,
                    "next": "Topic Created"
                }
            }
        },
        "Topic Created": {
            "actions": {
                "reject_topic": {
                    "name": "Reject Topic",
                    "submitdata": [
                        {"name": "Rejection Reason", "type": "textarea", "check_string_len": [0, 10000]}
                    ],
                    "whocan": PERMISSION_TEACHER_OF_CREATOR,
                    "next": "Topic Rejected"
                },
                "approve_topic": {
                    "name": "Approve Topic",
                    "submitdata": [
                        {"name": "Comments", "type": "richtext"}
                    ],
                    "whocan": PERMISSION_TEACHER_OF_CREATOR,
                    "next": "Topic Approved"
                }
            }
        },
        "Topic Rejected": {
            "actions": {
                "modify_topic": {
                    "name": "Modify Topic",
                    "submitdata": [
                        {"name": "Graduate Design Title", "type": "text", "check_string_len": [2, 100]},
                        {"name": "Topic Description", "type": "richtext", "check_string_len": [20, 10000]}
                    ],
                    "whocan": PERMISSION_CREATOR,
                    "next": "Topic Created"
                }
            }
        },
        "Topic Approved": {
            "actions": {
                "submit_design": {
                    "name": "Submit Design",
                    "submitdata": [
                         {"name": "Design Content", "type": "richtext", "check_string_len": [10, 20000]},
                         {"name": "Attachment Link", "type": "text", "check_string_len": [0, 200]}
                    ],
                    "whocan": PERMISSION_CREATOR,
                    "next": "Design Submitted"
                }
            }
        },
        "Design Submitted": {
             "actions": {
                "score_design": {
                    "name": "Grading Complete",
                    "submitdata": [
                        {"name": "Score", "type": "int", "check_int_range": [0, 100]},
                        {"name": "Comments", "type": "textarea", "check_string_len": [0, 2000]}
                    ],
                    "whocan": PERMISSION_TEACHER_OF_CREATOR,
                    "next": "Grading Complete"
                },
                "return_design": {
                    "name": "Return for Revision",
                    "submitdata": [
                        {"name": "Return Reason", "type": "textarea"}
                    ],
                    "whocan": PERMISSION_TEACHER_OF_CREATOR,
                    "next": "Topic Approved"
                }
            }
        },
        "Grading Complete": {
            "actions": {} # Workflow ended, no operations
        }
    }
 
    # =========================================================
    #               Core Logic Methods
    # =========================================================

    @staticmethod
    def check_permission(whocan, user, gd_obj=None):
        """
        Check if the user has permission to execute the action
        """
        if user.is_staff: return True # Admin has all permissions
        
        # 1. Student required
        if whocan == GraduateDesign.PERMISSION_STUDENT:
            return user.usertype == 2000

        # 2. Creator required
        if whocan == GraduateDesign.PERMISSION_CREATOR:
            if not gd_obj: return False
            return gd_obj.creator_id == user.id

        # 3. Teacher required
        if whocan == GraduateDesign.PERMISSION_TEACHER_OF_CREATOR:
            if user.usertype == 3000:
                # Simplified: any teacher can operate.
                # Full version: query Profile table to check student-teacher relationship
                return True 
            return False

        return False
       
    @staticmethod
    def listbypage(pagenum, pagesize, keywords, current_user):
        try:
            qs = GraduateDesign.objects.values("id",
                                        "creator",
                                        "creator_realname",
                                        "title",
                                        "currentstate",
                                        "createdate"
            ).order_by('-id')
            
            # Permission filter: Students can only see their own
            if current_user.usertype == 2000:
                qs = qs.filter(creator=current_user)
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            return {"ret": 0, "items": retlist, "total": pgnt.count, 'keywords': keywords}
            
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': keywords}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err} 
    
    # Get workflow info
    @staticmethod
    def getone(wf_id, withwhatcanido, current_user):
        try:
            # Case 1: Request new creation UI (id = -1)
            if wf_id == -1:
                ret_data = {
                    'ret': 0, 
                    'rec': {
                        "id": -1, "creatorname": "", "title": "", 
                        "currentstate": "Start", "createdate": ""
                    }
                }
                if withwhatcanido:
                    # Get actions for "Start" state
                    ret_data['whaticando'] = GraduateDesign.get_what_i_can_do(None, current_user)
                return ret_data

            # Case 2: Request existing record
            gd = GraduateDesign.objects.get(id=wf_id)
            
            # Get step history
            steps = list(GraduateDesignStep.objects.filter(design=gd).values(
                'id', 'operator__realname', 'actiondate', 'actionname', 'nextstate'
            ).order_by('id')) 
            
            rec = {
                "id": gd.id,
                "creatorname": gd.creator_realname,
                "title": gd.title,
                "currentstate": gd.currentstate,
                "createdate": gd.createdate,
                "steps": steps
            }
            
            ret_data = {'ret': 0, 'rec': rec}
            
            if withwhatcanido:
                ret_data['whaticando'] = GraduateDesign.get_what_i_can_do(gd, current_user)
                
            return ret_data

        except GraduateDesign.DoesNotExist:
             return {'ret': 1, 'msg': f'Record does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

    @staticmethod
    def get_what_i_can_do(gd_obj, user):
        """
        Return list of executable actions based on current state and user identity
        """
        ret_actions = []
        
        # Determine current state name
        current_state_name = "Start" if gd_obj is None else gd_obj.currentstate
            
        # Check configuration
        state_rule = GraduateDesign.WF_RULE.get(current_state_name)
        if not state_rule:
            return []
            
        actions_map = state_rule.get('actions', {})
        
        for key, action_def in actions_map.items():
            whocan = action_def.get('whocan')
            # Check permission
            if GraduateDesign.check_permission(whocan, user, gd_obj):
                # Construct data for frontend
                action_info = action_def.copy()
                action_info['key'] = key
                # If modify operation, pre-fill old values
                if key == 'modify_topic' and gd_obj:
                    for field in action_info['submitdata']:
                        if field['name'] == 'Graduate Design Title':
                            field['value'] = gd_obj.title
                ret_actions.append(action_info)
                
        return ret_actions

# Step Record Table
class GraduateDesignStep(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    design = models.ForeignKey(GraduateDesign, on_delete=models.CASCADE, related_name='steps')
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    operator_realname = models.CharField(max_length=30)
    actiondate = models.DateTimeField(default=timezone.now)
    actionname = models.CharField(max_length=50)
    nextstate = models.CharField(max_length=50)
    submitdata = models.TextField() # Stores JSON string

    class Meta:
        db_table = "cimp_graduatedesign_step"

    @staticmethod
    def getstepactiondata(step_id):
        try:
            step = GraduateDesignStep.objects.get(id=step_id)
            # String to Object
            data = json.loads(step.submitdata)
            return {'ret': 0, 'data': data}
        except GraduateDesignStep.DoesNotExist:
             return {'ret': 1, 'msg': 'Step does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}