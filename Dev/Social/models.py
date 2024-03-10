from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.utils import timezone
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse
import uuid

#Uploading userfiles to a specific directory
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

# Create your models here.

# class Categorie(models.Model):
#     genre = models.CharField(max_length=50,primary_key=True)

#     def __str__(self):
#         return self.genre
    
# class Blogpost(models.Model):
#     btitle = models.CharField(max_length=50)
#     bdesc = models.TextField(max_length=200)
#     genre = models.ForeignKey(Categorie,on_delete = models.DO_NOTHING)
#     bimg = models.ImageField(upload_to = 'blog')
#     btags = models.CharField(max_length=20)
#     bdate = models.DateField(null=True)

#     def __str__(self):
#         return self.btitle

# class Shoes(models.Model):
#     shoeimg = models.ImageField(upload_to='shoe')
#     categoryname = models.ForeignKey(Categories,on_delete=models.CASCADE)
#     sname = models.CharField(max_length=50,null=True)
#     price = models.IntegerField(null=True)

#     def __str__(self):
#         return self.sname

# class Portal(models.Model):
#     name = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)
#     def __str__(self):
#         return self.name
    


#Models New

#Tags
class Tag(models.Model):
    title = models.CharField(max_length=100, verbose_name="Tag")
    slug = models.SlugField(null=False, unique=True, default=uuid.uuid1)
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse('tags', args=[self.slug])
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.slug)
        return super().save(*args, **kwargs)
    

#Posts
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    picture = models.ImageField(upload_to=user_directory_path, verbose_name="Picture", null=True,  blank=True)
    video = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    caption = models.CharField(max_length=10000, verbose_name="Caption")
    posted = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField(Tag, related_name="tags")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='post_lik' , blank=True)
    def get_absolute_url(self):
        return reverse('post-details', args=[str(self.id)])
    
    def __str__(self):
        return self.caption
    

#Follow
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f'{str(self.follower)} ~~~ Follows ~~~ {self.following}'

class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)

        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()


post_save.connect(Stream.add_post, sender=Post)

#Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True ,verbose_name='Picture')
    saved = models.ManyToManyField(Post ,blank=True)
    following=models.ManyToManyField("self",related_name="followers",symmetrical=False)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.user)
    
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.username
        super(Profile, self).save(*args, **kwargs)

    
@receiver(post_save, sender=Profile)
def self_follow(sender, instance, created, **kwargs):
    if created:
        Follow.objects.create(
            follower = instance.user,
            following = instance.user
        )
    
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user = instance
        )
    

#Comment
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    text = models.TextField(max_length=150)
    created=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'[{str(self.user)}] @ [{str(self.post)}  post  {str(self.post.id)}] ~~ " {self.text} "'


#Tweet
class Tweet(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    tweet=models.CharField(max_length=400)
    likes = models.ManyToManyField(User, related_name='tweet_like' , blank=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'[{str(self.user)}] ~~~ {self.tweet}'
    
#Reply Tweet
class Reply(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    tweet=models.ForeignKey(Tweet,on_delete=models.CASCADE)
    reply=models.CharField(max_length=400)
    created=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'[{str(self.user)}] @ {str(self.tweet)}   ~~~ " {self.reply} "'
    

class Notification(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name="sender")
    receiver=models.ForeignKey(User,on_delete=models.CASCADE,related_name="receiver")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True,related_name="post")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True,related_name="comment")
    body=models.CharField(max_length=100)
    created=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.sender} {self.body} {self.receiver}'
    
class ScreenTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(blank=True, null=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    time_spent_seconds = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)

    def update_time_spent(self):
        if self.login_time and self.logout_time:
            time_difference = self.logout_time - self.login_time
            seconds_spent = time_difference.total_seconds()
            # Update the total time spent in seconds
            self.time_spent_seconds += int(seconds_spent)
        self.save()
        

