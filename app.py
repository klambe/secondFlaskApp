from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'tempSecretKey'

api = Api(app)

jwt = JWT(app, authenticate, identity)

items = []


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field must not be blank"
                        )

    @jwt_required()
    def get(self, name):
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'item': item}, 200 if item else 404

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None) is not None:
            return {'message': "An item with name '{}' already exists".format(name)}, 400
        else:
            new_item = Item.parser.parse_args()
            item = {'name': name, 'price': new_item['price']}
            items.append(item)
            return item, 201

    @jwt_required()
    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': "Item Deleted"}

    def put(self, name):
        item = next(filter(lambda x: x['name'] == name, items), None)
        updated_item = Item.parser.parse_args()

        if item is None:
            item = {'name': name, 'price': updated_item['price']}
            items.append(item)
        else:
            item.update(updated_item)

        return {'item': item}, 200


class ItemList(Resource):
    def get(self):
        return {'items': items}

        # def post(self, name):
        #     item = {'name': name, 'price': 12.00}
        #     items.append(item)
        #     return item, 201


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

app.run(port=5000, debug=True)
