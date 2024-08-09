from django.shortcuts import render
# from django.http import HttpResponse

posts = [
    {
        'author': 'Khoa Ho',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'June 9, 2024'
    },
    {
        'author': 'John Doe',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'June 10, 2024'
    }
]

def home(request):
    # return HttpResponse('<doctype>...')
    context = {
        'posts': posts
    }
    return render(request, 'blog/home.html', context)

def about(request):
    # return HttpResponse('<h1>Blog About</h1>')
    return render(request, 'blog/about.html')
    