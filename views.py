from typing import Any, Dict
from django import http
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.views.generic import DetailView,View
from app2.models import Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from followers.models import Follower

class ProfileDetailView(DetailView):
    http_method_names = ["get"]
    model = User
    template_name ='profiles/detail.html'
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        user = self.get_object()
        # following = self.get_object()
        context = super().get_context_data(**kwargs)
        context["total_posts"] = Post.objects.filter(author=user).count()
        # TODO:adding number followers
        context["total_followers"] = Follower.objects.filter(following=user).count()
        
        if self.request.user.is_authenticated:
            context['you_follow'] = Follower.objects.filter(following=user, followed_by=self.request.user).exists()
        return context

class FollowView(LoginRequiredMixin, View):
    http_method_names = ["post"]
    model = Follower
    context_object_name = "following"

    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)
    
    # def get_context_data(self, **kwargs):
    #     following = self.get_object()
    #     context = super().get_context_data(**kwargs)
    #     context["total_followers"] = Follower.objects.filter(author=following).count()
    #     return context
    
    def post(self, request, *args, **kwargs):
        data = request.POST.dict()

        if "action" not in data or "username" not in data:
            return HttpResponseBadRequest("missing data")
        
        try:
            other_user = User.objects.get(username=data["username"])
        except User.DoesNotExist:                            
                return HttpResponseBadRequest("missing user")
        if data['action'] == "follow":
             follower, created = Follower.objects.get_or_create(
                  followed_by = request.user,
                  following = other_user
             )
        else:
             try:
                  follower = Follower.objects.get(
                       followed_by = request.user,
                       following = other_user
                  )
             
             except Follower.DoesNotExist:
                  follower = None
             if follower:
              follower.delete()
        
        return JsonResponse({
            'success': True,
            'wording': "unfollow" if data['action'] == "follow" else "Follow"
        })


  

