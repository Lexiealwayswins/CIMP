from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
import traceback
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage

# You can create a superuser via command: python manage.py createsuperuser
# This adds a record to this User table
class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)

    # User Type
    # 1: Super Admin | 1000: Admin | 2000: Student | 3000: Teacher
    usertype = models.PositiveIntegerField()

    # Real Name
    realname = models.CharField(max_length=30, db_index=True)

    # Student Number
    studentno = models.CharField(
        max_length=10,  
        db_index=True, 
        null=True, blank=True
        )

    # Description / Remarks
    desc = models.CharField(max_length=500, null=True, blank=True)

    REQUIRED_FIELDS = ['usertype', 'realname']

    class Meta:
        db_table = "cimp_user"
        app_label = "main"
    
    
    @staticmethod 
    def addone(data):
        try:
            user = User.objects.create(
                username = data['username'],
                password = make_password(data['password']),
                usertype = data['usertype'],
                realname = data['realname'],
                studentno = data['studentno'],
                desc = data['desc']
            )
            
            return {'ret': 0, 'id': user.id}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
        
    @staticmethod 
    def listbypage(pagenum, pagesize, keywords):
        try:
            qs = User.objects.values('id', 
                                     'username', 
                                     'realname', 
                                     'studentno', 
                                     'desc', 
                                     'usertype')\
                .order_by('-id') # Order by ID descending (newest first)
            
            # Check for keyword search parameters
            if keywords:
                conditions = [Q(username__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)

            # Use Paginator
            pgnt = Paginator(qs, pagesize)

            # Read specific page from database
            page = pgnt.page(pagenum)

            # Convert QuerySet to list
            retlist = list(page)

            return {'ret': 0, 'items': retlist,'total': pgnt.count, 'keywords': keywords}
        
        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': keywords}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
    
    @staticmethod 
    def modifyone(oid, newdata):
        try:
            user = User.objects.get(id=oid)
            
            if 'username' in newdata:
                username = newdata['username']
                if User.objects.filter(username=username).exists():
                    return {'ret': 3, 'msg': f'Username {username} already exists'}
            
            if 'password' in newdata:
                # Pop password to prevent overwriting in the loop below
                user.password = make_password(newdata.pop('password')) 
                
            for field, value in newdata.items():
                setattr(user, field, value)
            
            user.save()
            
            return {'ret': 0}
        
        except User.DoesNotExist:
            return {'ret': 1, 'msg': f'User with id {oid} does not exist'}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod 
    def deleteone(oid):
        try:
            user = User.objects.get(id=oid)
            
            user.delete()
            
            return {'ret': 0}
        
        except User.DoesNotExist:
            return {'ret': 1, 'msg': f'User with id {oid} does not exist'}
        
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

# Personal Profile Settings
class Profile(models.Model):
    # Teacher set by student
    teacherid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_profile')
    # Student
    studentid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_profile')
    
    class Meta:
        db_table = "cimp_profile"
        app_label = "main"
    
    @staticmethod
    def setmyprofile(data, current_user):
        try:
            if 'password' in data:
                current_user.password = make_password(data['password'])
            if 'realname' in data:
                current_user.realname = data['realname']
            
            current_user.save()
            
            # If teacher
            if current_user.usertype == 3000:            
                return {'ret': 0}
            
            # If student
            if current_user.usertype == 2000:
                if 'tearcherid' in data:
                    Profile.objects.update_or_create(teacherid=data['teacherid'], 
                                            studentid=current_user.id)
                    
                return {'ret': 0}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
    
    @staticmethod
    def getmyprofile(current_user):
        try:
            profile_user = current_user.values("userid",
                                            "username",
                                            "usertype",
                                            "realname")
            # If teacher
            if current_user.usertype == 3000:
                return {'ret': 0, 'profile': profile_user}
                
            # If student
            elif current_user.usertype == 2000:
                profile = Profile.objects.get(studentid=current_user.id)
                if profile:
                    profile_user["teacher"] = {"id": profile.teacherid,
                                                "realname": current_user.realname}
                else:
                    profile_user["teacher"] = {
                                                    "id": -1,
                                                    "realname": "Not Set"}
                return {'ret': 0, 'profile': profile_user}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
        
    @staticmethod
    def listteachers(keywords):
        try:
            qs = User.objects.filter(usertype=3000).values("id", "realname")
            
            if keywords:
                conditions = [Q(realname__contains=one) for one in keywords.split(" ") if one]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)
            if qs.count() > 30:
                qs = qs[:30]
            retlist = list(qs)
            
            return {"ret": 0, "items": retlist, "total": qs.count(), "keyword": keywords}
                
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}
          