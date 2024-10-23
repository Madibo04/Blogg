from django.urls import path
from app.views  import *

urlpatterns = [
    path('', homepage, name = 'home'),
    path('About', about, name = 'about'),
    path('hello/<name>', hello, name= 'school'),
    path('blogs', blogs, name= 'blogs'),
    path('read/<str:id>', read, name="read"),
    path('delete/<str:id>', delete, name="delete"),
    path('edit/<str:id>', edit, name="edit"),
    path('create', create, name="create"),
    path('signup', signup, name="signup"),
    path('login', login, name="login"),
    path('logout', logout, name="logout"),
    path('contact', contact, name="contact"),
    path('donate', donate,  name="donate"),
    path('verify', verify, name = "verify"),
]