from django.db import models
import traceback
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from .user import User

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
    
    class Meta:
        db_table = "cimp_notice"
        app_label = "main"
        
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

    class Meta:
        db_table = "cimp_news"
        app_label = "main"
        
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
        

