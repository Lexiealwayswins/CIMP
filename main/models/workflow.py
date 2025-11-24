from django.db import models
import traceback
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from .user import User
import json

class GraduateDesign(models.Model):
    
    id = models.BigAutoField(primary_key=True)

    # Creator (Student), ForeignKey to User
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'GraduateDesign')
    
    # Creator's real name
    creator_realname = models.CharField(max_length=30, db_index=True)
    
    title = models.CharField(max_length=1000)
    
    # Current State (Default: Topic Created)
    currentstate = models.CharField(max_length=200, default='Topic Created')
    
    # Creation date
    createdate = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = "cimp_graduatedesign"
        app_label = "main"
        
    # =========================================================
    #               Workflow Configuration (Core Logic)
    # =========================================================
    
    # Permission Constants
    PERMISSION_STUDENT = 1              # Any student (usertype=2000)
    PERMISSION_CREATOR = 2              # Creator only
    PERMISSION_TEACHER_OF_CREATOR = 3   # Creator's teacher only (usertype=3000)
    PERMISSION_ADMIN = 4                # Admin

    # State Machine Rules
    WF_RULE = {
        "Start": {
            "actions": {
                "create_topic": {
                    "name": "Create Topic",
                    "submitdata": [
                        {"name": "Graduate Design Title", "type": "text", "check_string_len": [1, 50]},
                        {"name": "Topic Description", "type": "richtext", "check_string_len": [10, 10000]},
                    ],
                    "whocan": PERMISSION_STUDENT,
                    "next": "Topic Created"
                }
            }
        },
        "Topic Created": {
            "actions": {
                "reject_topic": {
                    "name": "Reject Topic",
                    "submitdata": [
                        {"name": "Rejection Reason", "type": "textarea", "check_string_len": [0, 10000]}
                    ],
                    "whocan": PERMISSION_TEACHER_OF_CREATOR,
                    "next": "Topic Rejected"
                },
                "approve_topic": {
                    "name": "Approve Topic",
                    "submitdata": [
                        {"name": "Comments", "type": "richtext"}
                    ],
                    "whocan": PERMISSION_TEACHER_OF_CREATOR,
                    "next": "Topic Approved"
                }
            }
        },
        "Topic Rejected": {
            "actions": {
                "modify_topic": {
                    "name": "Modify Topic",
                    "submitdata": [
                        {"name": "Graduate Design Title", "type": "text", "check_string_len": [2, 100]},
                        {"name": "Topic Description", "type": "richtext", "check_string_len": [20, 10000]}
                    ],
                    "whocan": PERMISSION_CREATOR,
                    "next": "Topic Created"
                }
            }
        },
        "Topic Approved": {
            "actions": {
                "submit_design": {
                    "name": "Submit Design",
                    "submitdata": [
                         {"name": "Design Content", "type": "richtext", "check_string_len": [10, 20000]},
                         {"name": "Attachment Link", "type": "text", "check_string_len": [0, 200]}
                    ],
                    "whocan": PERMISSION_CREATOR,
                    "next": "Design Submitted"
                }
            }
        },
        "Design Submitted": {
             "actions": {
                "score_design": {
                    "name": "Grading Complete",
                    "submitdata": [
                        {"name": "Score", "type": "int", "check_int_range": [0, 100]},
                        {"name": "Comments", "type": "textarea", "check_string_len": [0, 2000]}
                    ],
                    "whocan": PERMISSION_TEACHER_OF_CREATOR,
                    "next": "Grading Complete"
                },
                "return_design": {
                    "name": "Return for Revision",
                    "submitdata": [
                        {"name": "Return Reason", "type": "textarea"}
                    ],
                    "whocan": PERMISSION_TEACHER_OF_CREATOR,
                    "next": "Topic Approved"
                }
            }
        },
        "Grading Complete": {
            "actions": {} # Workflow ended, no operations
        }
    }
    
    class Meta:
        db_table = "cimp_graduatedesign"
        app_label = "main"
    # =========================================================
    #               Core Logic Methods
    # =========================================================

    @staticmethod
    def check_permission(whocan, user, gd_obj=None):
        """
        Check if the user has permission to execute the action
        """
        if user.is_staff: return True # Admin has all permissions
        
        # 1. Student required
        if whocan == GraduateDesign.PERMISSION_STUDENT:
            return user.usertype == 2000

        # 2. Creator required
        if whocan == GraduateDesign.PERMISSION_CREATOR:
            if not gd_obj: return False
            return gd_obj.creator_id == user.id

        # 3. Teacher required
        if whocan == GraduateDesign.PERMISSION_TEACHER_OF_CREATOR:
            if user.usertype == 3000:
                # Simplified: any teacher can operate.
                # Full version: query Profile table to check student-teacher relationship
                return True 
            return False

        return False
       
    @staticmethod
    def listbypage(pagenum, pagesize, keywords, current_user):
        try:
            qs = GraduateDesign.objects.values("id",
                                        "creator",
                                        "creator_realname",
                                        "title",
                                        "currentstate",
                                        "createdate"
            ).order_by('-id')
            
            # Permission filter: Students can only see their own
            if current_user.usertype == 2000:
                qs = qs.filter(creator=current_user)
            
            if keywords:
                conditions = [Q(content__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
                
            pgnt = Paginator(qs, pagesize)
            
            page = pgnt.page(pagenum)
            
            retlist = list(page)
            
            return {"ret": 0, "items": retlist, "total": pgnt.count, 'keywords': keywords}
            
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': keywords}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err} 
    
    # Get workflow info
    @staticmethod
    def getone(wf_id, withwhatcanido, current_user):
        try:
            # Case 1: Request new creation UI (id = -1)
            if wf_id == -1:
                ret_data = {
                    'ret': 0, 
                    'rec': {
                        "id": -1, "creatorname": "", "title": "", 
                        "currentstate": "Start", "createdate": ""
                    }
                }
                if withwhatcanido:
                    # Get actions for "Start" state
                    ret_data['whaticando'] = GraduateDesign.get_what_i_can_do(None, current_user)
                return ret_data

            # Case 2: Request existing record
            gd = GraduateDesign.objects.get(id=wf_id)
            
            # Get step history
            steps = list(GraduateDesignStep.objects.filter(design=gd).values(
                'id', 'operator__realname', 'actiondate', 'actionname', 'nextstate'
            ).order_by('id')) 
            
            rec = {
                "id": gd.id,
                "creatorname": gd.creator_realname,
                "title": gd.title,
                "currentstate": gd.currentstate,
                "createdate": gd.createdate,
                "steps": steps
            }
            
            ret_data = {'ret': 0, 'rec': rec}
            
            if withwhatcanido:
                ret_data['whaticando'] = GraduateDesign.get_what_i_can_do(gd, current_user)
                
            return ret_data

        except GraduateDesign.DoesNotExist:
             return {'ret': 1, 'msg': f'Record does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

    @staticmethod
    def get_what_i_can_do(gd_obj, user):
        """
        Return list of executable actions based on current state and user identity
        """
        ret_actions = []
        
        # Determine current state name
        current_state_name = "Start" if gd_obj is None else gd_obj.currentstate
            
        # Check configuration
        state_rule = GraduateDesign.WF_RULE.get(current_state_name)
        if not state_rule:
            return []
            
        actions_map = state_rule.get('actions', {})
        
        for key, action_def in actions_map.items():
            whocan = action_def.get('whocan')
            # Check permission
            if GraduateDesign.check_permission(whocan, user, gd_obj):
                # Construct data for frontend
                action_info = action_def.copy()
                action_info['key'] = key
                # If modify operation, pre-fill old values
                if key == 'modify_topic' and gd_obj:
                    for field in action_info['submitdata']:
                        if field['name'] == 'Graduate Design Title':
                            field['value'] = gd_obj.title
                ret_actions.append(action_info)
                
        return ret_actions
    
    
# Step Record Table
class GraduateDesignStep(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    design = models.ForeignKey(GraduateDesign, on_delete=models.CASCADE, related_name='steps')
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    operator_realname = models.CharField(max_length=30)
    actiondate = models.DateTimeField(default=timezone.now)
    actionname = models.CharField(max_length=50)
    nextstate = models.CharField(max_length=50)
    submitdata = models.TextField() # Stores JSON string

    class Meta:
        db_table = "cimp_graduatedesign_step"
        app_label = "main"

    @staticmethod
    def getstepactiondata(step_id):
        try:
            step = GraduateDesignStep.objects.get(id=step_id)
            # String to Object
            data = json.loads(step.submitdata)
            return {'ret': 0, 'data': data}
        except GraduateDesignStep.DoesNotExist:
             return {'ret': 1, 'msg': 'Step does not exist'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        