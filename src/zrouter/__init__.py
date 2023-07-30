from zrouter import Router
from flask import request 


def get_user_agent():
    return request.user_agent.string.lower()


def get_ip():
    nodes = request.headers.getlist("X-Forwarded-For")
    return nodes[0] if nodes else request.remote_addr

