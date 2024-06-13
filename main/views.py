import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from lib.share import JR
from main.models import User, Notice, News, Paper, Config, Profile, Thumbup, GraduateDesign
from config.settings import UPLOAD_DIR
from datetime import datetime
from django.utils import timezone
from random import randint

# Create your views here.
class SignHandler:
    def handle(self, request):
        # parameters data called pd, it's a dict
        if request.method == "GET":
            return JsonResponse({"message": "This endpoint does not support GET requests."}, status=405)

        if request.method == "POST":
            try:
                if not request.body:
                    return JsonResponse({"error": "Empty request body"}, status=400)

                pd = json.loads(request.body)
                # Process the data as needed
                return JsonResponse({"message": "Data processed successfully."})
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        action = pd.get('action')
        
        # request是来一个请求处理一个，不存在用户冲突，所以把pd存到request对象里
        request.pd = pd
        
        if action == 'signin':
            return self.signin(request)
        elif action == 'signout':
            return self.signout(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'action 参数错误'})
        
    def signin(self, request):
        
        # 从 HTTP POST 请求中获取用户名、密码参数
        userName = request.pd.get('username')
        passWord = request.pd.get('password')

        # 使用 Django auth 库里面的 方法校验用户名、密码
        user = authenticate(username=userName, password=passWord)

        
        # 如果用户名、密码有误
        if user is None:
            return JR({'ret': 1, 'msg': '用户名或者密码错误'}, json_dumps_params={'ensure_ascii':False})
        
        # 如果能找到用户，并且密码正确
        
        if not user.is_active:
            return JR({'ret': 0, 'msg': '用户已经被禁用'})
        
        login(request, user)
        
        return JR(
            {
                "ret": 0,
                "usertype":user.usertype,
                "userid":user.id,
                "realname":user.realname
            }
        )

    # 登出处理
    def signout(self, request):
        # 使用登出方法
        logout(request)
        return JsonResponse({'ret': 0})

class AccountHandler:
    def handle(self, request):
        
        if not request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': '仅限管理员使用'})
        
        if request.method == 'GET':
            pd = request.GET
        else:
            pd = json.loads(request.body)
        
        # request是来一个请求处理一个，不存在用户冲突，所以把pd存到request对象里
        request.pd = pd
        
        # parameters data called pd, it's a dict
        action = pd.get('action')
        
        if action == 'listbypage':
            return self.listbypage(request)
        elif action == 'addone':
            return self.addone(request)
        elif action == 'modifyone':
            return self.modifyone(request)
        elif action == 'deleteone':
            return self.deleteone(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'action 参数错误'})
        
    # 添加用户
    def addone(self, request):
        
        data = request.pd.get('data')
        
        ret = User.addone(data)
        
        return JR(ret)

    # 列出用户
    def listbypage(self, request):
        
        pagenum = int(request.pd.get('pagenum'))
        pagesize = int(request.pd.get('pagesize'))
        keywords = str(request.pd.get('keywords'))
        
        ret = User.listbypage(pagenum, pagesize, keywords)
        
        return JR(ret)
    
    # 修改用户信息
    def modifyone(self, request):
        
        newdata = request.pd.get('newdata')
        oid = request.pd.get('id')
        
        ret = User.modifyone(oid, newdata)
        
        return JR(ret)
    
    # 删除用户信息
    def deleteone(self, request):
        
        
        oid = request.pd.get('id')
        
        ret = User.deleteone(oid)
        
        return JR(ret)
    
class UploadHandler:
    def handle(self, request):
        uploadFile = request.FILES['upload1']
        
        filetype = uploadFile.name.split('.')[-1]
        if filetype not in ['jpg', 'png']:
            return JR({'ret': 430, 'msg': '只能上传 jpg png 文件'})
        
        # 处理文件大于10M的情况
        if uploadFile.size > 10*1024*1024: 
            return JR({'ret': 431, 'msg':'文件太大, 不能大于10M'})
        
        suffix = datetime.now().strftime('%Y%m%d%H%M%S_') + str(randint(0,999999))
        filename = f'{request.user.id}_{suffix}.{filetype}' 
 
        # 写入文件到静态文件访问区
        with open(f'{UPLOAD_DIR}/{filename}', 'wb') as f:
            # 读取上传文件数据
            bytes = uploadFile.read()
            # 写入文件
            f.write(bytes)
            
        return JR({'ret': 0, 'url': f'/upload/{filename}'}) 
    
class NoticeHandler:
    def handle(self, request):
        if not request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': '仅限管理员使用'})
        
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
            return JsonResponse({'ret': 2, 'msg': 'action 参数错误'})
        
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
        
        # 获取当前登录用户信息
        current_user = request.user
        
        # 确认当前用户已登录
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
            return JsonResponse({'ret': 2, 'msg': '仅限管理员使用'})
        
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
            return JsonResponse({'ret': 2, 'msg': 'action 参数错误'})
        
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
        
        # 获取当前登录用户信息
        current_user = request.user
        
        # 确认当前用户已登录
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
            return JsonResponse({'ret': 2, 'msg': 'action 参数错误'})
        
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
            return JsonResponse({'ret': 2, 'msg': '仅限管理员查看'})
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
            return JsonResponse({'ret': 2, 'msg': '仅限管理员查看'})
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
            return JsonResponse({'ret': 2, 'msg': '仅限管理员封禁'})
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
    
class ConfigHandler:
    def handle(self, request):
        
        if not request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': '仅限管理员使用'})
            
        if request.method == 'GET':
            pd = request.GET
        else:
            pd = json.loads(request.body)
            
        request.pd = pd
        
        action = pd.get('action')
        if action == 'set':
            return self.set(request)
        elif action == 'get':
            return self.get(request)
        elif action == 'gethomepagebyconfig':
            return self.gethomepagebyconfig(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'action 参数错误'})
        
    def set(self, request):
        data = json.loads(request.body.decode('utf-8'))
        if data.get('name') == 'homepage':
            ret = Config.set(data)
            return JR(ret)
        else:
            return JR({'ret': 2, 'msg': '非主页设置'})
    
    def get(self, request):
        name = request.pd.get('name')
        if name == 'homepage':
            ret = Config.get(name)
            return JR(ret)
        else:
            return JR({'ret': 2, 'msg': '非主页设置'})
    
    def gethomepagebyconfig(self, request):
        config = Config()
        ret = config.gethomepagebyconfig()
        return JR(ret)


class ProfileHandler:
    def handle(self, request):
        
        if request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': '仅限老师、学生使用'})
            
        if request.method == 'GET':
            pd = request.GET
        else:
            pd = json.loads(request.body)
            
        request.pd = pd
        
        action = pd.get('action')
        if action == 'setmyprofile':
            return self.setmyprofile(request)
        elif action == 'getmyprofile':
            return self.getmyprofile(request)
        elif action == 'listteachers':
            return self.listteachers(request)
        elif action == 'thumbuporcancel':
            return self.thumbuporcancel(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'action 参数错误'})
        
    def getmyprofile(self, request):
        current_user = request.user
        ret = Profile.setmyprofile(current_user)
        
        return JR(ret)

    
    def setmyprofile(self, request):
        current_user = request.user
        data = request.pd.get('newdata')
        
        ret = Profile.setmyprofile(data, current_user)
        
        return JR(ret)
    
    def listteachers(self, request):
        current_user = request.user
        if current_user.usertype != 2000:
            return JsonResponse({'ret': 2, 'msg': '仅限学生操作'})
        keywords = request.pd.get('keywords')
        
        ret = Profile.listteachers(keywords)
        return JR(ret)
    
    def thumbuporcancel(self, request):
        current_user = request.user
        if current_user.usertype != 2000 and current_user.usertype != 3000:
            return JsonResponse({'ret': 2, 'msg': '仅限老师和学生操作'})
        paper_id = request.get('paperid')
        ret = Thumbup.listteachers(paper_id, current_user)
        return JR(ret)

class GraduateDesignHandler:
    def handle(self, request):
        if request.method == 'GET':
            pd = request.GET
        else:
            pd = json.loads(request.body)
        
        request.pd = pd
        
        action = pd.get('action')
        if action == 'listbypage':
            return self.listbypage(request)
        elif action == 'getone':
            return self.getone(request)
        elif action == 'stepaction':
            return self.stepaction(request)
        elif action == 'getstepactiondata':
            return self.getstepactiondata(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'action 参数错误'})
        
        
    def listbypage(self, request):
        pagenum = int(request.pd.get('pagenum'))
        pagesize = int(request.pd.get('pagesize'))
        keywords = str(request.pd.get('keywords'))
        
        ret = GraduateDesign.listbypage(pagenum, pagesize, keywords)
        return JR(ret)
    
    def getone(self, request):
        wf_id = request.pd.get('wf_id')
        withwhatcanido = request.pd.get('withwhatcanido')
        ret = GraduateDesign.getone(wf_id, withwhatcanido)
        return JR(ret)
    
    def stepaction(self, request):
        pass
    
    def getstepactiondata(self, request):
        pass