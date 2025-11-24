import json
from django.http import JsonResponse
from lib.share import JR
from main.models import Paper
from django.utils import timezone

class PaperHandler:
    def handle(self, request):
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
        elif action == 'listminebypage':
            return self.listminebypage(request)
        elif action == 'addone':
            return self.addone(request)
        elif action == 'getone':
            return self.getone(request)
        elif action == 'modifyone':
            return self.modifyone(request)
        elif action == 'holdone':
            return self.holdone(request)
        elif action == 'banone':
            return self.banone(request)
        elif action == 'publishone':
            return self.publishone(request)
        elif action == 'deleteone':
            return self.deleteone(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'Action parameter error'})
        
    def listbypage(self, request):
        pagesize = int(request.pd.get('pagesize'))
        pagenum = int(request.pd.get('pagenum'))
        keywords = str(request.pd.get('keywords'))
        withoutcontent = bool(request.pd.get('withoutcontent', False))
        
        ret = Paper.listbypage(pagesize, pagenum, keywords, withoutcontent)
        
        return JR(ret)
    
    def listbypage_allstate(self, request):
        pagesize = int(request.pd.get('pagesize'))
        pagenum = int(request.pd.get('pagenum'))
        keywords = str(request.pd.get('keywords'))
        withoutcontent = bool(request.pd.get('withoutcontent', False))
        
        current_user = request.user
        if current_user.is_authenticated and current_user.is_staff: 
            ret = Paper.listbypage_allstate(pagesize, pagenum, keywords, withoutcontent)
        else:
            return JsonResponse({'ret': 2, 'msg': 'Admin view only'})
        return JR(ret)
    
    def listminebypage(self, request):
        pagesize = int(request.pd.get('pagesize'))
        pagenum = int(request.pd.get('pagenum'))
        keywords = str(request.pd.get('keywords'))
        withoutcontent = bool(request.pd.get('withoutcontent', False))
        
        current_user = request.user
        if current_user.is_authenticated: 
            ret = Paper.listminebypage(current_user, pagesize, pagenum, keywords, withoutcontent)
        else:
            return JsonResponse({'ret': 2, 'msg': 'Admin view only'})
        return JR(ret)
    
    def addone(self, request):
        data = request.pd.get('data')
        current_user = request.user
        if current_user.is_authenticated:
            author = current_user
            data['author_realname'] = author.realname
        data['pubdate'] = timezone.now()
        data['status'] = 1
        ret = Paper.addone(data, author)
        
        return JR(ret)
    
    def getone(self, request):
        paper_id = request.pd.get('id')
        ret = Paper.getone(paper_id)
        return JR(ret)
    
    def modifyone(self, request):
        paper_id = request.pd.get('id')
        newdata = request.pd.get('newdata')
        current_user = request.user
        ret = Paper.modifyone(paper_id, newdata, current_user)
        return JR(ret)
    
    def holdone(self, request):
        paper_id = request.pd.get('id')
        current_user = request.user
        ret = Paper.holdone(paper_id, current_user)
        return JR(ret)

    def banone(self, request):
        paper_id = request.pd.get('id')
        current_user = request.user
        if current_user.is_authenticated and current_user.is_staff: 
            ret = Paper.banone(paper_id)
        else:
            return JsonResponse({'ret': 2, 'msg': 'Admin ban only'}, status=403)
        return JR(ret)
    
    def publishone(self, request):
        paper_id = request.pd.get('id')
        current_user = request.user
        ret = Paper.publishone(paper_id, current_user)
        return JR(ret)
    
    def deleteone(self, request):
        paper_id = request.pd.get('id')
        current_user = request.user
        ret = Paper.deleteone(paper_id, current_user)
        return JR(ret)
  