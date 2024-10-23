from django.shortcuts import render, redirect, reverse
from app.models import Blog, Comment, Contact
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
import requests
import random

# Create your views here.

def homepage(request):
    all_products = ['Tote-bag', 'Shoes', 'Jewelries', 'Amala', 'Assorted']
    context = {'product': all_products}
    return render(request, 'app/index.html', context)

def about(request):
    return render(request, 'app/about.html')

def hello(request, name):
    context = {"person": name}
    return render(request,'app/hello.html', context)

@login_required
def blogs(request):
    # if not request.user.is_authenticated:
    #     return redirect(login)
    # all_blogs= Blog. objects.all().order_by("-created_at")
    # context = {'blogs': all_blogs}
    user = request.user
    my_blogs = Blog.objects.filter(owner = user).order_by('-created_at')
    other_blogs = Blog.objects.all ().exclude(owner = user)
    # other_blogs = Blog.objects.filter(owner != user)
    context = {'my_blogs': my_blogs, 'other_blogs': other_blogs}
    return render(request, 'app/blogs.html', context)
               
@login_required
def read(request, id):
    # single_blog= Blog.objects.get(id = id)
    user = request.user
    single_blog = Blog.objects.filter(id=id).first()
    if not single_blog:
        messages.error(request, "Invalid Blog")
        return redirect(reverse('blogs'))
    
    if request.method == "POST":
        body = request.POST.get('comment')
        if not body:
            messages.error(request, "Please enter a comment")
            return redirect (reverse('read', kwargs={"id":id}))
        Comment.objects.create(
            owner = user,
            blog = single_blog,
            body = body
        )
        return redirect (reverse(read, kwargs={"id":id}))
    blog_comment = Comment.objects.filter(blog = single_blog).order_by('-created_at')
    context = {'blog':single_blog, 'comments':blog_comment}
    return render(request, 'app/read.html', context)

def delete(request, id):
    user = request.user
    single_blog = Blog.objects.filter(id=id).first()
    if not single_blog:
        messages.error(request, "Invalid Blog")
        return redirect(blogs)
    if single_blog.owner != user and not  user.is_staff:
        messages.error (request, "Unauthorised Access")
        return redirect (blogs)
    single_blog.delete()
    messages.success(request, "Blog deleted successfully")
    return redirect(blogs)

@login_required
def edit(request, id):
    user = request.user
    single_blog = Blog.objects.filter(id=id).first()
    if not single_blog:
        messages.error(request, "Invalid Blog")
        return redirect(blogs)
    context = {'blog':single_blog}
    if single_blog.owner != user:
        messages.error (request, "Unauthorised Access")
        return redirect (blogs)
    if  request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        img = request.POST.get('image')
        dsc = request.POST.get('Description')
        if not title or not body:
            messages.error(request, 'Field cannot be blank')
            return redirect(edit)
        if len(title) > 250:
            messages.error(request, "Title cannot be more than 250 characters")
            return redirect(edit)
        single_blog.title = title
        single_blog.body = body
        single_blog.description = dsc
        if img:
            single_blog.image = img
        single_blog.save()
        messages.success(request, "Blog updated Successsfully")
        return redirect(blogs)

    return render(request, 'app/edit.html', context)

@login_required
def create (request):
    user = request.user
    if request.method == "POST":
        title = request.POST.get('title')
        body = request.POST.get('body')
        img = request.FILES.get('image')
        dsc = request.POST.get('Description')
        if not title or not body:
            messages.error(request, "Field cannot be blank")
            return redirect(create)
        if len(title) > 250:
            messages.error(request,  "Title cannot be more than 250 characters")
            return redirect(create)
        Blog.objects.create(
            title = title,
            body = body,
            image = img,
            description = dsc,
            owner = user
        )
        messages.success(request, "Blog created successfully")
        return redirect(blogs)
    return render (request, 'app/create.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect (homepage)
    if request.method =="POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        if not username or not email or not firstname or not lastname or not  password or not cpassword:
            messages.error(request, "Field cannot be blank")
            return redirect(signup)
        if password != cpassword:
            messages.error(request, "Password does not match")
            return redirect(signup)
        if len(password) < 8:
            messages.error(request, "Password should be at least 8 characters long")
            return redirect(signup)
        if len(username) < 5:
            messages.error(request,  "Username should be at least 5 characters long")
            return redirect(signup)
        username_exists = User.objects.filter(username=username).exists()
        if username_exists:
            messages.error(request, "Username already exists")
            return redirect(signup)
        email_exists = User.objects.filter(email=email).exists()
        if email_exists:
            messages.error(request, "Email already exists")
            return redirect(signup)
        user = User.objects.create(
            username = username,
            email = email,
            first_name = firstname,
            last_name = lastname,
        )
        user.set_password(password)
        user.save()
        messages.success(request,  "Account created successfully")
        return redirect(blogs)

    return render(request, 'app/signup.html')

def login(request):
    if request.user.is_authenticated:
        return redirect (homepage)
    next = request.GET.get('next')
    if  request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not  username or not password:
            messages.error(request, "Field cannot be blank")
            return redirect(login)
        user = auth.authenticate(username=username, password=password)
        if not  user:
            messages.error(request,  "Invalid username or password")
            return redirect(login)
        auth.login(request, user)
        return redirect(next or homepage)


    return render(request, 'app/login.html')

def logout(request):
    auth.logout(request)
    return redirect(login)

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get('email')
        message = request.POST.get('message')
        if not name or not email or not message:
            messages.error(request, "Field cannot be blank")
            return  redirect(contact)
        new_contact = Contact.objects.create(
            name = name,
            email = email,
            message = message
        )
        new_contact.save()
        subject = "Thank you for reaching out"
        body = f"Hello {name},\n\nThank you for contacting us.\n\n\tOkiki\nCEO Klicks Venture"
        send_email = EmailMessage(
            subject= subject,
            body = body,
            from_email = settings.EMAIL_HOST_USER,
            to = [email]
        )
        send_email.send()

        send_email = EmailMessage(
            subject="New contact us message!",
            body = f"Someone filled the form with the following details:\nName:{name}\nEmail:{email}\nMessage:{message}",
            from_email = settings.EMAIL_HOST_USER,
            to = ['madibohabeeb04@gmail.com']
        )
        send_email.send()
        messages.success(request, "Message sent successfully")
        return redirect(homepage)
    return render(request, "app/contact.html")

def donate(request):
    if request.method == "POST":
        email = request.POST.get('email')
        amount = request.POST.get("amount")
        if not amount or not email:
            messages.error(request, 'All Fields required')
            return redirect(donate)
        
        reference = random.randrange(1111111111, 9999999999)

        amount = int(amount) * 100
        data = {"email": email, 'amount':amount, 'reference': reference, 'callback_url': "http://127.0.0.1:8000/verify"}
        url = 'https://api.paystack.co/transaction/initialize'
        headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
        req = requests.post(url, headers=headers, data=data)
        response = req.json()
        if response.get("status"):
            authorization_url = response["data"].get("authorization_url")
            if authorization_url:
                return redirect(authorization_url)
    return render(request, 'app/donate.html')

def verify(request):
    reference = request.GET.get("trxref")
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
    req = requests.get(url, headers=headers)
    response = req.json()
    if response.get("status"):
        return render(request , 'app/thanks.html')
    return redirect(donate)


def custom_404(request, exception):
    return render(request, 'app/error_404.html', status=404)

def custom_500(request):
    return render(request, 'app/error_500.html', status=500)