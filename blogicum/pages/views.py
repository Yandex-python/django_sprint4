from http.client import HTTPResponse

from django.shortcuts import render


def about(request) -> HTTPResponse:
    return render(request, 'pages/about.html')


def rules(request) -> HTTPResponse:
    return render(request, 'pages/rules.html')
