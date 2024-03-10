from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('',views.frontpage,name='frontpage'),
    path('home',views.home,name='home'),
    path('feed', views.feed, name='feed'),
    path('tweetfeed', views.tweetfeed, name='tweetfeed'),
    path('notifications', views.notifications, name='notifications'),
    path('navbar', views.navbar),
    path('search', views.search, name='search'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('newpost',views.NewPost,name='newpost'),
    path('screentime',views.screen_time_view,name='screentime'),
    #Reset password
    path('reset_password',auth_views.PasswordResetView.as_view(template_name="reset_pass.html"),name="reset_password"),
    path('reset_password_sent',auth_views.PasswordResetDoneView.as_view(template_name="home/reset_pass_sent.html"),name="password_reset_done"),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name="home/reset_pass_confirm.html"),name="password_reset_confirm"),
    path('reset_password_complete',auth_views.PasswordResetCompleteView.as_view(template_name="home/reset_pass_done.html"),name="password_reset_complete"),
   
   
    path('feed/<uuid:post_id>/', views.PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>', views.tags, name='tags'),
    path('<uuid:post_id>/saved', views.saved, name='saved'),
    path('like', views.like, name='like'),
    path('add_comment/<uuid:post_id>/', views.add_comment, name='add_comment'),
    path('fetch_post_comments/<uuid:post_id>/', views.fetch_post_comments, name='fetch_post_comments'),
    path('tweet', views.createtweet, name='newtweet'),
    path('createprofile', views.createProfile, name='createprofile'),
    path('editprofile', views.editProfile, name='editprofile'),
    path('password_change', views.password_change, name='password_change'),
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
    path('<int:id>/<int:status>', views.followuser, name='follownow'),

    
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)