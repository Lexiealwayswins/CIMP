import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from lib.share import JR
from main.models import User, Profile, Thumbup

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
