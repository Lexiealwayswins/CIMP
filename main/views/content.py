import json
from django.http import JsonResponse
from lib.share import JR
from main.models import Notice, News
from django.utils import timezone

class NoticeHandler:
    def handle(self, request):
        if not request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': 'Admin access only'})
        
        if request.method == 'GET':
            pd = request.GET
        else:
            pd = json.loads(request.body)
        
        request.pd = pd
        
        action = pd.get('action')
        if action == 'listbypage':
            return self.listbypage(request)
        elif action == 'listbypage_allstate':
            return self.listbypage_allstate(request)
        elif action == 'getone':
            return self.getone(request)
        elif action == 'addone':
            return self.addone(request)
        elif action == 'modifyone':
            return self.modifyone(request)
        elif action == 'banone':
            return self.banone(request)
        elif action == 'publishone':
            return self.publishone(request)
        elif action == 'deleteone':
            return self.deleteone(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'Action parameter error'}, status=400)
        
    def listbypage(self, request):
        pagenum = int(request.pd.get('pagenum'))
        pagesize = int(request.pd.get('pagesize'))
        keywords = str(request.pd.get('keywords'))
        withoutcontent = bool(request.pd.get('withoutcontent', False))
        
        ret = Notice.listbypage(pagenum, pagesize, keywords, withoutcontent)
        return JR(ret)
    
    def listbypage_allstate(self, request):
        pagenum = int(request.pd.get('pagenum'))
        pagesize = int(request.pd.get('pagesize'))
        keywords = str(request.pd.get('keywords'))
        withoutcontent = bool(request.pd.get('withoutcontent', False))
        
        ret = Notice.listbypage_allstate(pagenum, pagesize, keywords, withoutcontent)
        return JR(ret)
    
    def getone(self, request):
        notice_id = request.pd.get('id')
        ret = Notice.getone(notice_id)
        return JR(ret)

    def addone(self, request):
        
        data = request.pd.get('data')
        
        # Get current logged-in user info
        current_user = request.user
        
        # Confirm current user is logged in
        if current_user.is_authenticated:
            author = current_user
            data['author_realname'] = current_user.realname
        
        data['pubdate'] = timezone.now()
        data['status'] = 1
        
        ret = Notice.addone(data, author)
        return JR(ret)
    
    def modifyone(self, request):
        notice_id = request.pd.get("id")
        new_data = request.pd.get("newdata")
        ret = Notice.modifyone(notice_id, new_data)
        return JR(ret)
    
    def banone(self, request):
        notice_id = request.pd.get("id")
        ret = Notice.banone(notice_id)
        return JR(ret)

    def publishone(self, request):
        notice_id = request.pd.get("id")
        ret = Notice.publishone(notice_id)
        return JR(ret)
    
    def deleteone(self, request):
        notice_id = request.pd.get("id")
        ret = Notice.deleteone(notice_id)
        return JR(ret)
    
class NewsHandler:
    def handle(self, request):
        if not request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': 'Admin access only'})
        
        if request.method == 'GET':
            pd = request.GET
        else:
            pd = json.loads(request.body)
        
        request.pd = pd
        
        action = pd.get('action')
        if action == 'listbypage':
            return self.listbypage(request)
        elif action == 'listbypage_allstate':
            return self.listbypage_allstate(request)
        elif action == 'getone':
            return self.getone(request)
        elif action == 'addone':
            return self.addone(request)
        elif action == 'modifyone':
            return self.modifyone(request)
        elif action == 'banone':
            return self.banone(request)
        elif action == 'publishone':
            return self.publishone(request)
        elif action == 'deleteone':
            return self.deleteone(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'Action parameter error'})
        
    def listbypage(self, request):
        pagenum = int(request.pd.get('pagenum'))
        pagesize = int(request.pd.get('pagesize'))
        keywords = str(request.pd.get('keywords'))
        withoutcontent = bool(request.pd.get('withoutcontent', False))
        
        ret = News.listbypage(pagenum, pagesize, keywords, withoutcontent)
        return JR(ret)
    
    def listbypage_allstate(self, request):
        pagenum = int(request.pd.get('pagenum'))
        pagesize = int(request.pd.get('pagesize'))
        keywords = str(request.pd.get('keywords'))
        withoutcontent = bool(request.pd.get('withoutcontent', False))
        
        ret = News.listbypage_allstate(pagenum, pagesize, keywords, withoutcontent)
        return JR(ret)
    
    def getone(self, request):
        news_id = request.pd.get('id')
        ret = News.getone(news_id)
        return JR(ret)

    def addone(self, request):
        
        data = request.pd.get('data')
        
        # Get current logged-in user info
        current_user = request.user
        
        # Confirm current user is logged in
        if current_user.is_authenticated:
            author = current_user
            data['author_realname'] = current_user.realname
        
        data['pubdate'] = timezone.now()
        data['status'] = 1
        
        ret = News.addone(data, author)
        return JR(ret)
    
    def modifyone(self, request):
        news_id = request.pd.get("id")
        new_data = request.pd.get("newdata")
        ret = News.modifyone(news_id, new_data)
        return JR(ret)
    
    def banone(self, request):
        news_id = request.pd.get("id")
        ret = News.banone(news_id)
        return JR(ret)

    def publishone(self, request):
        news_id = request.pd.get("id")
        ret = News.publishone(news_id)
        return JR(ret)
    
    def deleteone(self, request):
        news_id = request.pd.get("id")
        ret = News.deleteone(news_id)
        return JR(ret)
 