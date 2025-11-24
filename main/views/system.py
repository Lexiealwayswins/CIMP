import json
from django.http import JsonResponse
from lib.share import JR
from main.models import Config
from config.settings import UPLOAD_DIR
from datetime import datetime
from random import randint

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
