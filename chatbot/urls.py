from django.urls import path
# from .views import chatbot_view
from . import views
from .views import chatbot_query, image_search
from .views import product_detail
from .views import helpful_feedback, get_user_info

urlpatterns = [
    # path("", chatbot_view, name="chatbot"),
    path("query/", views.chatbot_query, name="chatbot_query"),
    path("image-search/", image_search, name="image_search"),
    path("product/<int:pk>/", product_detail, name="product_detail"),
    path("feedback/", helpful_feedback, name="helpful_feedback"),
    path("user-info/", get_user_info, name="chatbot_user_info"),
]
