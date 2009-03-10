#coding:utf-8
import wsgiref.handlers
import os
from functools import wraps
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import methods,logging
from django.utils import simplejson

adminFlag=True

class AdminControl(webapp.RequestHandler):
    def render(self,template_file,template_value):
        path=os.path.join(os.path.dirname(__file__),template_file)
        self.response.out.write(template.render(path, template_value))
    def returnjson(self,dit):
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(simplejson.dumps(dit))
        
def requires_admin(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not users.is_current_user_admin() and adminFlag:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            return method(self, *args, **kwargs)
    return wrapper

class Admin_Upload(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/upload.html', {})
    @requires_admin
    def post(self):
        bf=self.request.get("file")
        if not bf:
            return self.redirect('/admin/upload/')
#        name=self.request.body_file.vars['file'].filename
        mime = self.request.body_file.vars['file'].headers['content-type']
        if mime.find('image')==-1:
             return self.redirect('/admin/upload/')
        description=self.request.get("description")
        image=methods.addImage( mime, description, bf)
        
        self.redirect('/show/%s/' %image.id)

class Admin_Upload2(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/upload2.html', {})
    @requires_admin
    def post(self):
        dit={"result":"error"}
        bf=self.request.get("Filedata")
        if not bf:
            return self.returnjson(dit)
        image=methods.addImage2(bf)
        if not image:
             return self.returnjson(dit)
        dit["result"]="ok"
        dit["id"]=image.id
        return self.returnjson(dit)
        
class Delete_Image(AdminControl):
    @requires_admin
    def get(self,key):
        methods.delImage(key)
        self.redirect('/')
        
class Delete_Image_ID(AdminControl):
    @requires_admin
    def get(self,id):
        methods.delImageByid(id)
        self.redirect('/')

class Admin_Login(AdminControl):
    @requires_admin
    def get(self):
        self.redirect('/')
        
def main():
    application = webapp.WSGIApplication(
                                       [(r'/admin/upload/', Admin_Upload),
                                        (r'/admin/upload2/', Admin_Upload2),
                                        (r'/admin/del/(?P<key>[a-z,A-Z,0-9]+)', Delete_Image),
                                        (r'/admin/delid/(?P<id>[0-9]+)/', Delete_Image_ID),
                                        (r'/admin/', Admin_Login),
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()