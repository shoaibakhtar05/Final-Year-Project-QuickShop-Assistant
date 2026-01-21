# 🛒 QuickShop – AI Powered E‑Commerce Platform (Final Year Project)

QuickShop is an AI‑powered e‑commerce web application developed as a **Final Year Project (FYP)**. The system enhances the traditional online shopping experience by integrating
**text‑based and image‑based product search** along with an **intelligent chatbot** that assists customers with product queries, recommendations, and support.

---

## 📌 Project Objectives

* Build a modern e‑commerce platform with AI capabilities
* Implement **text and image‑based product search**
* Develop an **AI chatbot** for customer interaction
* Provide a scalable, real‑world full‑stack solution
* Demonstrate integration of AI with web technologies

---

## 🚀 Key Features

### 1️⃣ Text‑Based Product Search

* Search products using keywords (e.g., *"black watch"*, *"laptops"*)
* Supports fuzzy search and natural language queries
* Filter products by category, price, brand, etc.

### 2️⃣ Image‑Based Product Search

* Upload an image (e.g., a watch)
* System finds visually similar products
* Returns same product type with variations (color, style, brand)
* Uses deep learning (CNN feature extraction)

### 3️⃣ AI Chatbot

* Answers customer queries related to products
* Provides price, availability, and description
* Handles common customer support questions
* Can recommend products based on user input

### 4️⃣ User Management

* User registration and login
* Customer and admin roles
* Secure authentication

### 5️⃣ Admin Panel

* Add, update, and delete products
* Manage categories and inventory

---

## 🛠️ Technologies Used

### Frontend

* Django
* Bootstrap
* JavaScript
* HTML5 / CSS3

### Backend

* Django (Python)
* RESTful APIs

### Database

* MySQL / SqLite

### AI & Machine Learning

* Python
* TensorFlow / PyTorch
* Pre‑trained CNN (ResNet / VGG)
* Cosine Similarity / FAISS

### Chatbot & NLP

* LLaMA / OpenAI API
* LangChain (optional)
* Custom product data integration

---

## ⚙️ Installation & Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/quickshop-fyp.git
cd quickshop-fyp
```

---

### 2️⃣ Frontend Setup

```bash
cd frontend
npm install
npm start
```

* Runs on: `http://localhost:3000`

---

### 3️⃣ Backend Setup (Spring Boot)

```bash
cd backend
mvn clean install
mvn spring-boot:run
```

* Runs on: `http://localhost:8080`

**OR (Django Backend)**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

### 4️⃣ Image Search AI Service

```bash
cd image-search-service
pip install -r requirements.txt
python app.py
```

* Extracts image features and performs similarity matching

---

## 🤖 Chatbot Working Flow

1. User sends a message from frontend
2. Backend receives the query
3. Query is processed using NLP / LLM
4. Relevant product data is fetched from database
5. AI‑generated response is returned to the user

---

## 🖼️ Image‑Based Search Working Flow

1. User uploads an image
2. Image is sent to AI service
3. CNN extracts feature vector
4. Vector is compared with stored product vectors
5. Similar products are returned

---

## 🔐 Security

* Password hashing
* Role‑based access (Admin / Customer)
* Secure APIs

---

## 📈 Future Enhancements

* Voice‑based product search
* Personalized recommendations
* Price negotiation chatbot
* AR/VR product preview
* Payment gateway integration

---

## 🎓 Academic Information

* **Project Type:** Final Year Project (FYP)
* **Domain:** E‑Commerce + Artificial Intelligence
* **Purpose:** Academic & learning use

---

## 👤 Developer

**Name:** Shoaib Akhtar
**Degree:** BS Computer Science
**Project Title:** QuickShop – AI Powered E‑Commerce Platform

---

## Conclusion

QuickShop demonstrates how modern AI techniques can be integrated into an e‑commerce system to improve search accuracy, customer engagement, and overall shopping experience. The project combines full‑stack development with practical AI implementation, making it suitable for real‑world applications.
