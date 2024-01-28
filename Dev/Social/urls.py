from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('',views.frontpage,name='frontpage'),
    path('home',views.home,name='home'),
    path('feed', views.feed, name='feed'),
    path('navbar', views.navbar),
    path('search', views.search, name='search'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('newpost',views.NewPost,name='newpost'),
    path('feed/<uuid:post_id>/', views.PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>', views.tags, name='tags'),
    path('<uuid:post_id>/saved', views.saved, name='saved'),
    path('like', views.like, name='like'),
    path('add_comment/<uuid:post_id>/', views.add_comment, name='add_comment'),
    path('fetch_post_comments/<uuid:post_id>/', views.fetch_post_comments, name='fetch_post_comments'),
    path('tweet', views.createtweet, name='newtweet'),
    path('editprofile', views.editProfile, name='editprofile'),
    # path('profile', views.profile, name='profile'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('<username>', views.profile, name='profilee'),
    path('<username>/saved', views.profile, name='savedd'),
    path('<username>/follow/<option>', views.follow, name='follow'),

    # path('usertweets',views.userprofile),
    # path('tweetopen/<int:id>',views.tweet_replies,name="twt_open"),
    
    # path('newtweet',views.createtweet),
    # path('edittweet/<int:id>',views.edittweet,name="twt_edit"),
    # path('deletetweet/<int:id>',views.deletetweet,name="twt_del"),

    path('test', views.test, name='test'),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)