from django.db import models
import traceback
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from .user import User

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

    class Meta:
        db_table = "cimp_paper"
        app_label = "main"
         
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
        


class Thumbup(models.Model):
    paper_id = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name = 'thumbup')
    thumbuper = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'thumbuper')
    thumbup = models.BooleanField(default=False)

    class Meta:
        db_table = "cimp_thumbup"
        app_label = "main"
           
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
        

