from django.shortcuts import render
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from store.models import Product # make sure path is correct
from store.models import Feedback
from category.models import Category
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torchvision.transforms as transforms
import torchvision.models as models
import torch
import json, re
from unidecode import unidecode
from thefuzz import fuzz
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth import get_user
from .models import ChatbotFeedback, PurchaseHistory, CustomerBehavior
from accounts.models import Account
from django.shortcuts import get_object_or_404, render
def get_user_info(request):
    if request.user.is_authenticated:
        user = request.user
        return JsonResponse({
            "logged_in": True,
            "name": user.full_name(),  # Uses your `full_name()` method
        })
    else:
        return JsonResponse({"logged_in": False})

@csrf_exempt
def chatbot_query(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "").strip().lower()
        user_email = data.get("email", "").strip().lower()

        message = re.sub(r'[^\w\s]', '', message)

        # 1. Feedback Check
        positive_keywords = ["good", "great", "love", "awesome", "excellent", "perfect", "amazing", "fantastic"]
        negative_keywords = ["bad", "worst", "poor", "expensive", "hate", "dislike", "terrible", "cheap quality"]

        for word in positive_keywords:
            if word in message:
                Feedback.objects.create(message=message, sentiment='positive')
                return JsonResponse({"response": "Thank you for your positive feedback!"})

        for word in negative_keywords:
            if word in message:
                Feedback.objects.create(message=message, sentiment='negative')
                return JsonResponse({"response": "We’re sorry for the inconvenience. We'll work on improving. 🙏"})

        # 2. RAM Filter
        ram_match = re.search(r'(\d+)\s*gb', message)
        ram_value = ram_match.group(1) + 'GB' if ram_match else None

        # 3. Price Filter
        price_match = re.search(r'under\s*\$?(\d+)|below\s*\$?(\d+)', message)
        price_limit = int(price_match.group(1) or price_match.group(2)) if price_match else None

        # 4. Personalized Recommendation
        if "recommend" in message or "suggest" in message:
            if user_email:
                history = PurchaseHistory.objects.filter(user_email=user_email).order_by('-purchase_count', '-last_searched')
                if history.exists():
                    top_category = history.first().category
                    top_products = Product.objects.filter(category=top_category, is_available=True).order_by('-price')[:4]
                    response = f"<p>Based on your interest in {top_category.category_name.title()}, here are some recommendations:</p>"
                    for product in top_products:
                        response += f"""
                            <div class="card mb-2" style="max-width: 300px;">
                              <img src="{product.images.url}" class="card-img-top" alt="{product.product_name}">
                              <div class="card-body">
                                <h6 class="card-title">{product.product_name}</h6>
                                <p class="card-text">Price: ${product.price}</p>
                                <a href="{product.get_url}" class="btn btn-sm btn-outline-primary" target="_blank">View Details</a>
                              </div>
                            </div>
                        """
                    return JsonResponse({"response": response})
                else:
                    return JsonResponse({"response": "We don't have your past purchase data yet. Please try searching for products first."})

        # 5. Fuzzy Product Match
        all_products = Product.objects.filter(is_available=True)
        product_names = [p.product_name.lower().replace('-', ' ') for p in all_products]
        best_product_match = process.extractOne(message, product_names, score_cutoff=85)

        if best_product_match:
            matched_product = all_products[product_names.index(best_product_match[0])]

            # Update search history
            if user_email:
                history, created = PurchaseHistory.objects.get_or_create(user_email=user_email, product=matched_product, category=matched_product.category)
                history.last_searched = timezone.now()
                history.save()

            # RAM and price filters
            if (not ram_value or matched_product.variation_set.filter(variation_category='ram', variation_value__icontains=ram_value).exists()) and \
               (not price_limit or matched_product.price <= price_limit):
                response = f"""
                    <div class="card mb-2" style="max-width: 300px;">
                      <img src="{matched_product.images.url}" class="card-img-top" alt="{matched_product.product_name}">
                      <div class="card-body">
                        <h5 class="card-title">{matched_product.product_name}</h5>
                        <p class="card-text">Price: $ {matched_product.price}</p>
                        <a href="{matched_product.get_url()}" class="btn btn-primary" target="_blank">View Details</a>
                      </div>
                    </div>
                """
                return JsonResponse({"response": response})
            
        # 6. Price Negotiation 
        negotiation_keywords = ["negotiate", "discount", "less", "bargain", "reduce", "lower price"]
        if any(word in message for word in negotiation_keywords):
            user = Account.objects.filter(email=user_email).first()
            if user:
                purchase_count = PurchaseHistory.objects.filter(user=user).count()
                behavior = CustomerBehavior.objects.filter(user=user).order_by('-views').first()
                print("Negotiation Triggered:", message)
                print("User Email:", user_email)
                print("User:", user)
                discount = 0
                if purchase_count >= 5:
                    discount = 15
                elif purchase_count >= 3:
                    discount = 10
                elif behavior and behavior.views >= 4:
                    discount = 5

                if discount > 0 and behavior:
                    product = behavior.product
                    original_price = product.price
                    discounted_price = round(original_price - (original_price * discount / 100), 2)
                    response = f"""
                        <div class="card mb-2" style="max-width: 300px;">
                          <img src="{product.images.url}" class="card-img-top" alt="{product.product_name}">
                          <div class="card-body">
                            <h5 class="card-title">{product.product_name}</h5>
                            <p class="card-text">
                              Original Price: <del>${original_price}</del><br>
                              🎁 Negotiated Price: <b>${discounted_price}</b> ({discount}% off)
                            </p>
                            <a href="{product.get_url}" class="btn btn-success" target="_blank">Buy Now</a>
                          </div>
                        </div>
                    """
                    return JsonResponse({"response": response})
                else:
                    return JsonResponse({"response": "You're not yet eligible for a discount. Browse or purchase more to unlock offers!"})
                
        # 6. Fuzzy Category Match
        all_categories = Category.objects.all()
        category_names = [c.category_name.lower() for c in all_categories]
        best_category_match = process.extractOne(message, category_names, score_cutoff=80)

        if best_category_match:
            matched_category = next((c for c in all_categories if c.category_name.lower() == best_category_match[0]), None)
            products = Product.objects.filter(category=matched_category, is_available=True)

            if ram_value:
                products = products.filter(variation__variation_category='ram', variation__variation_value__icontains=ram_value)

            if price_limit:
                products = products.filter(price__lte=price_limit)

            products = products.distinct()

            if products.exists():
                response = ""
                for product in products:
                    response += f"""
                        <div class="card mb-2" style="max-width: 300px;">
                          <img src="{product.images.url}" class="card-img-top" alt="{product.product_name}">
                          <div class="card-body">
                            <h6 class="card-title">{product.product_name}</h6>
                            <p class="card-text">Price: $ {product.price}</p>
                            <a href="{product.get_url()}" class="btn btn-sm btn-outline-primary" target="_blank">View Details</a>
                          </div>
                        </div>
                    """
                return JsonResponse({"response": response})

        # 7. Static FAQs
        faq_responses = {
            "how to order": "To place an order, just go to the product page and click 'Add to Cart'. 🛒",
            "place order": "To place an order, just go to the product page and click 'Add to Cart'. 🛒",
            "hello": "Hello! How can I help you today? 😊",
            "hi": "Hello! How can I help you today? 😊",
            "discount": "We’re offering discounts up to 10% on selected laptops and mobiles! 🎉",
            "offer": "We’re offering discounts up to 10% on selected laptops and mobiles! 🎉",
            "return policy": "You can return products within 7 days of delivery. Please keep the receipt. 📦",
            "free delivery": "We offer free delivery on all orders above Rs. 3000.",
            "shipping": "We offer free delivery on all orders above Rs. 3000.",
            "contact": "You can contact our support at shoaib@quickshop.com or call +923049585175.",
            "support": "You can contact our support at shoaib@quickshop.com or call +923049585175.",
        }

        for key in faq_responses:
            if key in message:
                return JsonResponse({"response": faq_responses[key]})

        # 8. Fallback to LLaMA AI
        api_key = config("TOGETHER_API_KEY")
        llama_prompt = f"You are an e-commerce assistant. Only talk about laptops, computers, and mobiles from our store. Answer concisely.\nUser: {message}\nAssistant:"
        url = "https://api.together.xyz/v1/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            "prompt": llama_prompt,
            "max_tokens": 150,
            "temperature": 0.7,
            "top_p": 0.9,
            "stop": ["\nUser:", "\nAssistant:"]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["text"].strip()
                return JsonResponse({"response": ai_response})
            else:
                return JsonResponse({"response": "Sorry, the AI server is not responding right now."})
        except Exception:
            return JsonResponse({"response": "Sorry, the AI server is not responding at the moment."})

    return JsonResponse({"error": "Invalid request method"}, status=400)

#  Load pre-trained ResNet-50 model
model = models.resnet50(pretrained=True)
model.eval()
#  Image transform (same as before)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])
# Feature extractor
def extract_features(image_path):
    image = Image.open(image_path).convert("RGB")
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        features = model(img_tensor).numpy()
    return features

#  Image search view
@csrf_exempt
def image_search(request):
    if request.method == "POST" and request.FILES.get("image"):
        img_file = request.FILES["image"]
        path = default_storage.save("uploads/" + img_file.name, ContentFile(img_file.read()))
        image_path = os.path.join(settings.MEDIA_ROOT, path)

        try:
            input_feat = extract_features(image_path)

            best_match = None
            best_score = -1

            for product in Product.objects.all():
                product_img_path = os.path.join(settings.MEDIA_ROOT, str(product.images))
                if not os.path.exists(product_img_path):
                    continue
                try:
                    prod_feat = extract_features(product_img_path)
                    score = cosine_similarity(input_feat, prod_feat)[0][0]
                    if score > best_score:
                        best_score = score
                        best_match = product
                except:
                    continue

            if best_match:
                product_card = f"""
               <div class="card mb-2" style="max-width: 300px;">
            <img src="/media/{best_match.images}" class="card-img-top" alt="{best_match.product_name}">
          <div class="card-body">
        <h6 class="card-title">{best_match.product_name}</h6>
        <p class="card-text">Rs. {best_match.price}</p>
        <a href="/product/{best_match.id}/" class="btn btn-primary">View Product</a>
      </div>
    </div>
    """
                return JsonResponse({"response": product_card})
            else:
                return JsonResponse({"response": "Sorry, no matching product found."})
        except Exception as e:
            return JsonResponse({"response": f"Error: {str(e)}"})

    return JsonResponse({"response": "Please upload an image."})


@csrf_exempt
def helpful_feedback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        helpful = data.get("helpful")

        if helpful in ["yes", "no"]:
            ChatbotFeedback.objects.create(
                query="Was this helpful?",
                feedback=helpful,
                user=request.user if request.user.is_authenticated else None
            )
            return JsonResponse({"status": "saved"})

    return JsonResponse({"error": "Invalid request"}, status=400)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product_detail.html", {"product": product})



