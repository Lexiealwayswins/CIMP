import json
from django.http import JsonResponse
from lib.share import JR
from main.models import GraduateDesign, GraduateDesignStep
import traceback

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
        