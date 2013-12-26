import os
import re
from string import letters

import webapp2
import jinja2

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class BlogHandler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = JINJA_ENVIRONMENT.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))


class MainPage(BlogHandler):
  def get(self):
    self.write('yo yo test test')

###### blog implementation 

def blog_key(name = 'default'):
  return ndb.Key.from_path('blogs',name)

class Post(ndb.Model):
  subject = ndb.StringProperty(required = True)
  content = ndb.TextProperty(required = True)
  created = ndb.DateTimeProperty(auto_now_add = True)
  last_modified = ndb.DateTimeProperty(auto_now = True)

  def render(self):
    self._render_text = self.content.replace('\n' '<br>')
    return render_str("post.html", p = self)

class BlogFront(BlogHandler):
  def get(self):
    posts = ndb.gql("SELECT * from Post order by created desc limit 10") # look up all the post ordered by creation time. store them in post object. Only show the last 10 entries
    self.render('index.html', posts = posts) # renders the html page with the result of the query and var post anpersjournalblog

class PostPage(BlogHandler):
  def get(self, post_id):
    key = ndb.Key.from_path('Post', int(post_id), parent=blog_key())
    post = ndb.get(key)

    if not post:
      self.error(404)
      return

    self.render("permalink.html", post = post)


class NewPost(BlogHandler):
  def get(self):
    self.render("newpost.html")

  def post(self):
    subject = self.request.get('subject') #verifying the form
    content = self.request.get('content') 

    if subject and content:
      p = Post(parent = blog_key(), subject=subject, content=content) #if valid content add post
      p.put() #stores the element in the database 
      self.redirect('/blog/%s' % str(p.key().id())) #redirect
    else:
      error = "A paragraph or subject is missing! " 
      self.render("newpost.html", subject=subject, content=content, error=error)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog/?', BlogFront),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/newpost', NewPost), #syntax for GAE pull up last 10 posts
], debug=True)



