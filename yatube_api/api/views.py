from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (
    CommentSerializer, GroupSerializer, PostSerializer, FollowSerializer
)
from .permissions import IsOwnerOrReadOnly
from posts.models import Group, Post


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsOwnerOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return post.comments.all()

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(ListModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        user = self.request.user
        queryset = user.followers.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
