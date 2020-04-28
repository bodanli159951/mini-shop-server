# _*_ coding: utf-8 _*_
"""
  Created by Mohan on 2020/4.
"""
from app.models.route import Route
from app.models.menu import Menu
from app.core.db import db
from app.core.error import Forbidden
from app.libs.utils import TreeNode, Tree
from sqlalchemy.exc import IntegrityError

__author__ = 'Mohan'


class RouteNode(TreeNode):
    def __init__(self, id=None, parent_id=None, title=None, name=None, icon=None, path=None, component=None, hidden=None):
        super(RouteNode, self).__init__(id=id, parent_id=parent_id)
        self.title = title
        self.name = name
        self.icon = icon
        self.path = path
        self.component = component
        self.hidden = hidden

    def keys(self):
        attrs = super(RouteNode, self).keys()
        return attrs + ('title', 'name', 'icon', 'path', 'component', 'hidden')


class RouteTree(Tree):
    def __init__(self, root=None):
        super(RouteTree, self).__init__(root, nodeType=RouteNode)


class RouteDao(object):
    @staticmethod
    def get_route_tree_all() -> dir:
        t = RouteTree()
        t.generate_by_list(Route.query.all())
        return t.serialize()

    @staticmethod
    def change_route(route_dir):
        cur_t = RouteTree()
        cur_t.generate_by_dir(route_dir)
        cur_list = cur_t.deserialize()
        for cur_route in cur_list:
            old_route = Route.get(id=cur_route['id'])
            if old_route and\
                    old_route.parent_id != cur_route['parent_id']:
                old_route.update(id=cur_route['id'], parent_id=cur_route['parent_id'], commit=False)
        pass

    @staticmethod
    def get_route_node_by_id(id) -> dir:
        return Route.filte(id=id).first()

    @staticmethod
    def update(id: int, **kwargs):
        route = Route.get_or_404(id=id, msg='该节点不存在')
        route.update(**kwargs)

    @staticmethod
    def delete(id: int):
        route = Route.get_or_404(id=id, msg='路由不存在, 删除失败')
        if Menu.get(route_id=id):
            raise Forbidden(msg='存在权限组绑定路由，不可删除')

        with db.auto_commit():
            route.delete(commit=False)
            Route.query.filter_by(parent_id=id).delete(synchronize_session=False)

    @staticmethod
    def create(**kwargs):
        Route.abort_repeat(msg='唯一键重复', name=kwargs['name'])
        route = Route.create(**kwargs)