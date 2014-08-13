from flask import Flask
from flask.ext.restful import abort, fields, marshal_with, reqparse, Api, Resource
from flask_restful_swagger import swagger

app = Flask(__name__)
api = swagger.docs(Api(app), apiVersion='0.1')

parser = reqparse.RequestParser()
parser.add_argument('task', type=str)


@swagger.model
class TodoModel(object):
    """Todo model object"""

    resource_fields = {
        'task': fields.String,
        'id':   fields.String,
    }

    def __init__(self, id, task):
        self.id = id
        self.task = task


TODOS = {
    'todo1': TodoModel('todo1', 'build an API'),
    'todo2': TodoModel('todo2', 'make it work'),
    'todo3': TodoModel('todo3', 'profit!'),
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):

    @swagger.operation(
        responseClass='TodoModel',
        responseMessages=[
            {
                "code": 200,
                "message": "Retrieved."
            },
            {
                "code": 404,
                "message": "Todo {} doesn't exist."
            }
        ]
    )
    @marshal_with(TodoModel.resource_fields)
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    @swagger.operation(
        responseMessages=[
            {
                "code": 204,
                "message": "Deleted."
            },
            {
                "code": 404,
                "message": "Todo {} doesn't exist."
            }
        ]
    )
    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204


    @swagger.operation(
        responseClass='TodoModel',
        parameters=[
            {
                "description": "Text of TODO item.",
                "name": "task",
                "required": True,
                "allowMultiple": False,
                "dataType": TodoModel.__name__,
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 201,
                "message": "Created."
            },
            {
                "code": 404,
                "message": "Todo {} doesn't exist."
            }
        ]
    )
    @marshal_with(TodoModel.resource_fields)
    def put(self, todo_id):
        args = parser.parse_args()
        task = TodoModel(todo_id, args['task'])
        TODOS[todo_id] = task
        return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):

    @swagger.operation(
        responseMessages=[
            {
                "code": 200,
                "message": "OK."
            }
        ]
    )
    @marshal_with(TodoModel.resource_fields)
    def get(self):
        return TODOS.values()

    def post(self):
        args = parser.parse_args()
        todo_id = 'todo%d' % (len(TODOS) + 1)
        TODOS[todo_id] = TodoModel(args['task'])
        return TODOS[todo_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')


if __name__ == '__main__':
    app.run(debug=True)