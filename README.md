# smart-resource-exchange
# Campusmart

A unified community platform that combines a smart **peer-to-peer marketplace** with an **automated lost-and-found registry**. The system uses machine learning to match buyers with relevant sellers and pair lost items with reported found listings based on item features, descriptions, and user preferences.

---

## 🌟 Key Features

### 🛒 Smart Buy & Sell

- **ML-Powered Recommendations:** Matches buyer interests, search history, and price sensitivities with relevant active listings.
- **Smart Pricing Insights:** Suggests competitive price ranges to sellers based on historical listing data and item condition.


### 🔍 Lost & Found Hub

- **Automated Item Matching:** Uses text embeddings and metadata (location, time, category, tags) to compute similarity scores between lost reports and found items.
- **Instant Match Alerts:** Automatically notifies users when a high-probability match is reported.

- **Claim Verification Flow:** Security questions/image proof flow to prevent wrongful item claims.

### 👤 User & Data Management
- **Role-Based Profiles:** Track active listings, purchase history, saved searches, and active lost/found claims.
- **Trust & Reputation:** Rating and review system for marketplace transactions.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML | CSS | JS |
| **Backend API** | Python (Flask) |
| **Database** | SQLite (relational user/transaction data) |
| **Machine Learning** | Python, Scikit-learn, Sentence-Transformers / Hugging Face, FAISS |

---

## 🤖 ML Engine Overview

The recommendation and matching pipeline operates on two primary models:

1. **Marketplace Matcher:** A hybrid collaborative-filtering and content-based recommendation model (`TF-IDF` / `Embedding-based similarity` + user interaction history) to rank seller listings for prospective buyers.
2. **Lost & Found Resolution Engine:** Cosine similarity scoring over dense text embeddings (generated via `Sentence-Transformers`) combined with geographic and temporal proximity filters.

---

## 🗄️ Database Schema Summary

- **Users:** `id`, `name`, `email`, `password_hash`, `reputation_score`, `created_at`
- **Marketplace Listings:** `id`, `seller_id`, `title`, `description`, `category`, `price`, `condition`, `status`, `embedding`
- **Lost & Found Items:** `id`, `reporter_id`, `type` (`LOST` | `FOUND`), `title`, `description`, `location`, `date_event`, `status`, `embedding`
- **Matches & Notifications:** `id`, `user_id`, `item_id`, `match_score`, `is_read`, `created_at`

---


### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/campus-trade-and-find.git](https://github.com/your-username/campus-trade-and-find.git)
   cd campus-trade-and-find