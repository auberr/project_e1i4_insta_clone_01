from uuid import uuid4
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from content.models import Feed, Reply, Like, Bookmark
from user.models import User
import os
from e1i4.settings import MEDIA_ROOT
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

def home(request):
    email = request.session.get('email', None)

    if email is None:
        return render(request, "user/login.html")

    user = User.objects.filter(email=email).first()

    if user is None:
        return render(request, "user/login.html")

    return render(request, "main.html") # 오형석 - 유저리스트 추가
    

class Main(APIView):
    def get(self, request):
        email = request.session.get('email', None)

        if email is None:
            return render(request, "user/login.html")

        user = User.objects.filter(email=email).first()

        if user is None:
            return render(request, "user/login.html")

        '''요기서부터 구현'''
        # 오형석 - 회원님을 위한 추천에 유저리스트 구현
        # 추천유저는 여기
        recommend_user_object_list = User.objects.all()
        recommend_user_list = []
        for reco_user in recommend_user_object_list:
            recommend_user = User.objects.filter(email=reco_user.email).first()
            recommend_user_list.append(dict(profile_image=recommend_user.profile_image,
                                        recommend_nickname=recommend_user.nickname,
                                        recommend_user=recommend_user))
        # 아래는 유저리스트 추가만

        feed_object_list = Feed.objects.all().order_by('-id')  # select  * from content_feed;
        feed_list = []

        for feed in feed_object_list:
            feed_user = User.objects.filter(email=feed.email).first()
            reply_object_list = Reply.objects.filter(feed_id=feed.id)
            reply_list = []
            for reply in reply_object_list:
                reply_user = User.objects.filter(email=reply.email).first()
                reply_list.append(dict(reply_content=reply.reply_content,
                                       nickname=reply_user.nickname,
                                       id=reply.id
                                       ))
                                       
            like_count=Like.objects.filter(feed_id=feed.id, is_like=True).count()
            is_liked=Like.objects.filter(feed_id=feed.id, email=email, is_like=True).exists()
            is_marked=Bookmark.objects.filter(feed_id=feed.id, email=email, is_marked=True).exists()
            feed_list.append(dict(id=feed.id,
                                  image=feed.image,
                                  content=feed.content,
                                  like_count=like_count,
                                  profile_image=feed_user.profile_image,
                                  nickname=feed_user.nickname,
                                  reply_list=reply_list,
                                  is_liked=is_liked,
                                  is_marked=is_marked
                                  ))

        
        return render(request, "e1i4/main.html", context=dict(feeds=feed_list, user=user, recommends=recommend_user_list)) # 오형석 - 유저리스트 추가
        '''요기까지 바뀐점 있음'''


    def detail(self, id):
        feed = Feed.objects.get(id=id)
        feed.delete()
        return redirect('detail.html')


    # def detail(self, request, pk):
    #     content_detail = Feed.objects.get(pk=pk)
    #     context = {
    #         'content':content_detail,
    #     }

    #     return render(request, "e1i4/main.html", context) 

class UploadFeed(APIView):
    def post(self, request):

        # 일단 파일 불러와
        file = request.FILES['file']

        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        asdf = uuid_name
        content123 = request.data.get('content')
        email = request.session.get('email', None)

        Feed.objects.create(image=asdf, content=content123, email=email)

        return Response(status=200)


class Profile(APIView):
    def get(self, request):
        email = request.session.get('email', None)

        if email is None:
            return render(request, "user/login.html")

        user = User.objects.filter(email=email).first()

        if user is None:
            return render(request, "user/login.html")

        feed_list = Feed.objects.filter(email=email)
        like_list = list(Like.objects.filter(email=email, is_like=True).values_list('feed_id', flat=True))
        like_feed_list = Feed.objects.filter(id__in=like_list)
        bookmark_list = list(Bookmark.objects.filter(email=email, is_marked=True).values_list('feed_id', flat=True))
        bookmark_feed_list = Feed.objects.filter(id__in=bookmark_list)
        return render(request, 'content/profile.html', context=dict(feed_list=feed_list,
                                                                    like_feed_list=like_feed_list,
                                                                    bookmark_feed_list=bookmark_feed_list,
                                                                    user=user))


class UploadReply(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        reply_content = request.data.get('reply_content', None)
        email = request.session.get('email', None)

        Reply.objects.create(feed_id=feed_id, reply_content=reply_content, email=email)

        return Response(status=200)

@csrf_exempt
def delete_reply(request, id):
    reply = Reply.objects.get(id=id)
    reply.delete()

    return redirect('/main/')


class ToggleLike(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        favorite_text = request.data.get('favorite_text', True)

        if favorite_text == 'favorite_border':
            is_like = True
        else:
            is_like = False
        email = request.session.get('email', None)

        like = Like.objects.filter(feed_id=feed_id, email=email).first()

        if like:
            like.is_like = is_like
            like.save()
        else:
            Like.objects.create(feed_id=feed_id, is_like=is_like, email=email)

        return Response(status=200)


class ToggleBookmark(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        bookmark_text = request.data.get('bookmark_text', True)
        print(bookmark_text)
        if bookmark_text == 'bookmark_border':
            is_marked = True
        else:
            is_marked = False
        email = request.session.get('email', None)

        bookmark = Bookmark.objects.filter(feed_id=feed_id, email=email).first()

        if bookmark:
            bookmark.is_marked = is_marked
            bookmark.save()
        else:
            Bookmark.objects.create(feed_id=feed_id, is_marked=is_marked, email=email)

        return Response(status=200)


# 게시글 삭제 함수
@ csrf_exempt
def delete_feed(request, id):
    feed = Feed.objects.get(id=id)
    feed.delete()
    return redirect('/main/')

# 게시글 수정 함수
@ csrf_exempt
def update_feed(request, id):
    feed = Feed.objects.get(id=id)
    
    feed.content = request.POST.get('content')

    feed.save()
    return redirect('/main/')


# 1번 방식
# class Detail(APIView):
def detail(request, pk):
    content_detail = Feed.objects.get(pk=pk)
    # context = {
    #     'content':content_detail,
    # }
    # feed_id = request.data.get('feed_id', None)
    email = request.session.get('email', None)

    if email is None:
        return render(request, "user/login.html")

    user = User.objects.filter(email=email).first()

    if user is None:
        return render(request, "user/login.html")

    feed_object_list = Feed.objects.all().order_by('-id')  # select  * from content_feed;
    feed_list = []

    for feed in feed_object_list:
        feed_user = User.objects.filter(email=feed.email).first()
        reply_object_list = Reply.objects.filter(feed_id=feed.id)
        reply_list = []
        for reply in reply_object_list:
            reply_user = User.objects.filter(email=reply.email).first()
            reply_list.append(dict(reply_content=reply.reply_content,
                                    nickname=reply_user.nickname))
                                    
        like_count=Like.objects.filter(feed_id=feed.id, is_like=True).count()
        is_liked=Like.objects.filter(feed_id=feed.id, email=email, is_like=True).exists()
        is_marked=Bookmark.objects.filter(feed_id=feed.id, email=email, is_marked=True).exists()
        feed_list.append(dict(content_detail=content_detail,
                                id=feed.id,
                                image=feed.image,
                                content=feed.content,
                                like_count=like_count,
                                profile_image=feed_user.profile_image,
                                nickname=feed_user.nickname,
                                reply_list=reply_list,
                                is_liked=is_liked,
                                is_marked=is_marked
                                ))


    return render(request, "e1i4/detail.html", context=dict(feeds=feed_list, user=user, pk=pk))
