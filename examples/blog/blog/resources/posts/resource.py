from __future__ import absolute_import

from restart.resource import Resource

from blog.api import api


@api.register
class Posts(Resource):
    name = 'posts'

    def index(self, request):
        return []
