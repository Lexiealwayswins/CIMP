from django.db import models
import traceback
from django.db.models import Q
from .user import User
from .content import News, Notice
from .academic import Paper
import json
from django.contrib.auth.hashers import make_password

# Homepage Config
class Config(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField()

    class Meta:
        db_table = "cimp_config"
        app_label = "main"
           
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

