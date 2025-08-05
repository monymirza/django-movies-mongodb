from django.shortcuts import render
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
import os
from django.conf import settings
from django.core.paginator import Paginator

client = MongoClient(
    settings.MONGODB_URI,
    tlsCAFile=certifi.where()
)
db = client["sample_mflix"]
movies_collection = db["movies"]
comments_collection = db["comments"]

def movie_list(request):
    search = request.GET.get("q", "")
    page = request.GET.get("page", 1)

    query = {}
    if search:
        query["title"] = {"$regex": search, "$options": "i"}

    movies_cursor = movies_collection.find(query, {"title": 1, "year": 1}).sort("year", -1)
    formatted = [{"id": str(m["_id"]), **m} for m in movies_cursor]

    paginator = Paginator(formatted, 10)  # 10 per page
    page_obj = paginator.get_page(page)

    return render(request, "movies_app/movie_list.html", {
        "page_obj": page_obj,
        "search": search,
    })

def movie_detail(request, movie_id):
    movie = movies_collection.find_one({"_id": ObjectId(movie_id)})
    if not movie:
        raise Http404("Movie not found")

    comments = list(comments_collection.find({"movie_id": ObjectId(movie_id)}))
    return render(request, "movies_app/movie_detail.html", {
        "movie": movie,
        "comments": comments,
    })

