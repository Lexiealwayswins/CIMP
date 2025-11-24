import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from lib.share import JR
from main.models import User, Notice, News, Paper, Config, Profile, Thumbup, GraduateDesign, GraduateDesignStep
from config.settings import UPLOAD_DIR
from datetime import datetime
from django.utils import timezone
from random import randint
import traceback

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
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        action = pd.get('action')
        
        # Request is handled one by one, no user conflict, so store pd in request object
        request.pd = pd
        
        if action == 'signin':
            return self.signin(request)
        elif action == 'signout':
            return self.signout(request)
        else:
            return JsonResponse({'ret': 2, 'msg': 'Action parameter error'}, status=400)
        
    def signin(self, request):
        
        # Get username and password from HTTP POST request
        userName = request.pd.get('username')
        passWord = request.pd.get('password')

        # Use Django auth library method to verify username and password
        user = authenticate(username=userName, password=passWord)

        # If username or password is incorrect
        if user is None:
            return JR({'ret': 1, 'msg': 'Incorrect username or password'}, json_dumps_params={'ensure_ascii': False})
        
        # If user is found and password is correct
        
        if not user.is_active:
            return JR({'ret': 0, 'msg': 'User has been disabled'}, status=403)
        
        login(request, user)
        # Trigger Django to write session
        request.session.modified = True
        
        return JR(
            {
                "ret": 0,
                "usertype": user.usertype,
                "userid": user.id,
                "realname": user.realname
            }
        )

    # Logout handling
    def signout(self, request):
        # Use logout method
        logout(request)
        return JsonResponse({'ret': 0})

class AccountHandler:
    def handle(self, request):
        
        if not request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': 'Admin access only'}, status=403)
        
        if request.method == 'GET':
            pd = request.GET
        else:
            pd = json.loads(request.body)
        
        # Request is handled one by one, no user conflict, so store pd in request object
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
            return JsonResponse({'ret': 2, 'msg': 'Action parameter error'}, status=400)
        
    # Add user
    def addone(self, request):
        
        data = request.pd.get('data')
        
        ret = User.addone(data)
        
        return JR(ret)

    # List users
    def listbypage(self, request):
        
        pagenum = int(request.pd.get('pagenum'))
        pagesize = int(request.pd.get('pagesize'))
        keywords = str(request.pd.get('keywords'))
        
        ret = User.listbypage(pagenum, pagesize, keywords)
        
        return JR(ret)
    
    # Modify user info
    def modifyone(self, request):
        
        newdata = request.pd.get('newdata')
        oid = request.pd.get('id')
        
        ret = User.modifyone(oid, newdata)
        
        return JR(ret)
    
    # Delete user info
    def deleteone(self, request):
        
        oid = request.pd.get('id')
        
        ret = User.deleteone(oid)
        
        return JR(ret)
    
class UploadHandler:
    def handle(self, request):
        uploadFile = request.FILES.get('upload1')
        if not uploadFile:
            return JR({'ret': 2, 'msg': 'No file received, ensure form field name is upload1'}, status=400)
        
        filetype = uploadFile.name.split('.')[-1]
        if filetype not in ['jpg', 'png']:
            return JR({'ret': 430, 'msg': 'Only jpg and png files are allowed'}, status=400)
        
        # Handle files larger than 10M
        if uploadFile.size > 10*1024*1024: 
            return JR({'ret': 431, 'msg': 'File too large, must be under 10M'})
        
        suffix = datetime.now().strftime('%Y%m%d%H%M%S_') + str(randint(0,999999))
        filename = f'{request.user.id}_{suffix}.{filetype}' 
 
        # Write file to static file access area
        with open(f'{UPLOAD_DIR}/{filename}', 'wb') as f:
            # Read uploaded file data
            bytes = uploadFile.read()
            # Write file
            f.write(bytes)
            
        return JR({'ret': 0, 'url': f'/upload/{filename}'}) 
    
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
    
class ConfigHandler:
    def handle(self, request):
        
        if not request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': 'Admin access only'})
            
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
            return JsonResponse({'ret': 2, 'msg': 'Action parameter error'})
        
    def set(self, request):
        data = json.loads(request.body.decode('utf-8'))
        if data.get('name') == 'homepage':
            ret = Config.set(data)
            return JR(ret)
        else:
            return JR({'ret': 2, 'msg': 'Not homepage setting'})
    
    def get(self, request):
        name = request.pd.get('name')
        if name == 'homepage':
            ret = Config.get(name)
            return JR(ret)
        else:
            return JR({'ret': 2, 'msg': 'Not homepage setting'})
    
    def gethomepagebyconfig(self, request):
        config = Config()
        ret = config.gethomepagebyconfig()
        return JR(ret)

class ProfileHandler:
    def handle(self, request):
        
        if request.user.is_staff:
            return JsonResponse({'ret': 2, 'msg': 'Teachers and Students only'})
            
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
            return JsonResponse({'ret': 2, 'msg': 'Action parameter error'})
        
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
            return JsonResponse({'ret': 2, 'msg': 'Student operation only'})
        keywords = request.pd.get('keywords')
        
        ret = Profile.listteachers(keywords)
        return JR(ret)
    
    def thumbuporcancel(self, request):
        current_user = request.user
        if current_user.usertype != 2000 and current_user.usertype != 3000:
            return JsonResponse({'ret': 2, 'msg': 'Teacher and Student operation only'})
        paper_id = request.get('paperid')
        ret = Thumbup.listteachers(paper_id, current_user)
        return JR(ret)

class GraduateDesignHandler:
    def handle(self, request):
        # Global login check
        if not request.user.is_authenticated:
            return JsonResponse({'ret': 1, 'msg': 'Please login first'})
        
        # Parse parameters
        if request.method == 'GET':
            pd = request.GET
        else:
            try:
                pd = json.loads(request.body)
            except:
                pd = {}
        
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
            return JsonResponse({'ret': 2, 'msg': 'Action parameter error'}, status=400)
        
        
    def listbypage(self, request):
        pagenum = int(request.pd.get('pagenum', 1))
        pagesize = int(request.pd.get('pagesize', 10))
        keywords = str(request.pd.get('keywords', ''))
        
        ret = GraduateDesign.listbypage(pagenum, pagesize, keywords, request.user)
        return JR(ret)
    
    def getone(self, request):
        try:
            wf_id = int(request.pd.get('wf_id'))
            # Handle "true"/"false" strings or boolean
            withwhatcanido_param = request.pd.get('withwhatcanido')
            withwhatcanido = str(withwhatcanido_param).lower() == 'true'
            ret = GraduateDesign.getone(wf_id, withwhatcanido, request.user)
            return JR(ret)
        except ValueError:
            return JsonResponse({'ret': 2, 'msg': 'Parameter format error'}, status=400)
    
    def getstepactiondata(self, request):
        step_id = request.pd.get('step_id')
        ret = GraduateDesignStep.getstepactiondata(step_id)
        return JR(ret)

    def stepaction(self, request):
        try:
            key = request.pd.get('key')
            # wf_id can be -1 (New) or a normal ID
            wf_id = int(request.pd.get('wf_id', -1)) 
            submitdata_list = request.pd.get('submitdata')
            user = request.user
            
            # --- 1. Determine target object and current state ---
            gd_obj = None
            current_state = "Start" # Translated from "开始"
            
            if wf_id > 0:
                gd_obj = GraduateDesign.objects.get(id=wf_id)
                current_state = gd_obj.currentstate
            
            # --- 2. Check config: Does this state support this action? ---
            state_rule = GraduateDesign.WF_RULE.get(current_state)
            if not state_rule:
                return JR({'ret': 2, 'msg': f'System config error: Unknown state {current_state}'})
                
            actions_map = state_rule.get('actions', {})
            action_def = actions_map.get(key)
            
            if not action_def:
                return JR({'ret': 2, 'msg': 'Operation not supported in current state or Key error'})
                
            # --- 3. Check permission: Double check to prevent forced calls ---
            whocan = action_def['whocan']
            if not GraduateDesign.check_permission(whocan, user, gd_obj):
                return JR({'ret': 2, 'msg': 'You do not have permission to execute this operation'})
                
            # --- 4. Execute business logic ---
            next_state = action_def['next']
            action_name = action_def['name']
            
            # Scenario A: Create new workflow
            if current_state == "Start": # Translated from "开始"
                title = "Untitled"
                # Find title from submitted data
                for item in submitdata_list:
                    # Translated from "毕业设计标题"
                    if item['name'] == 'Graduate Design Title': 
                        title = item['value']
                        break
                        
                gd_obj = GraduateDesign.objects.create(
                    creator=user,
                    creator_realname=user.realname,
                    title=title,
                    currentstate=next_state
                )
            
            # Scenario B: Update existing workflow
            else:
                # Special handling: If modifying topic, update the main table title
                if key == 'modify_topic': 
                     for item in submitdata_list:
                        # Translated from "毕业设计标题"
                        if item['name'] == 'Graduate Design Title':
                            gd_obj.title = item['value']
                            break
                
                # Update state
                gd_obj.currentstate = next_state
                gd_obj.save()
            
            # --- 5. Record step log ---
            GraduateDesignStep.objects.create(
                design=gd_obj,
                operator=user,
                operator_realname=user.realname,
                actionname=action_name,
                nextstate=next_state,
                submitdata=json.dumps(submitdata_list, ensure_ascii=False)
            )
            
            return JR({'ret': 0, 'wf_id': gd_obj.id})

        except GraduateDesign.DoesNotExist:
             return JR({'ret': 1, 'msg': 'Workflow record does not exist'})
        except Exception:
            err = traceback.format_exc()
            return JR({'ret': 2, 'msg': err})