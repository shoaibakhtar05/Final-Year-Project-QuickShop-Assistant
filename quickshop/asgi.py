# import os
# import django
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickshop.settings')
# django.setup()  #  This must come BEFORE importing anything from your app

# import chatbot.routing  #  Safe to import after setup()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(chatbot.routing.websocket_urlpatterns)
#     ),
# })
