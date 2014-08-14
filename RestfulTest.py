"""RestfulTest: Test project of flask-restful-swagger
"""
from flask import Flask, current_app
from flask.ext.restful import abort, fields, marshal, marshal_with, reqparse, Api, Resource
from flask_restful_swagger import swagger
import json

app = Flask(__name__)
api = swagger.docs(Api(app),
                   apiVersion='0.1',
                   api_spec_url='/_spec')


update_parser = reqparse.RequestParser()
update_parser.add_argument('task', type=str, required=False)
update_parser.add_argument('comment', type=str, required=False, help="Optional comment.")

parser = reqparse.RequestParser()
parser.add_argument('task', type=str, required=True, help="Task text is required.")
parser.add_argument('comment', type=str, required=False, help="Optional comment.")

@swagger.model
class TodoModel(object):
    """Todo model object"""

    resource_fields = {
        'task': fields.String,
        'comment': fields.String,
    }

    def __init__(self, id, task, comment):
        self.id = id
        self.task = task
        self.comment = comment


TODOS = { }


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


def redirect_to_todo(todo_id, code=201):
    url = '/todos/{}'.format(todo_id)
    response = current_app.response_class("", code, content_type='application/json')
    response.headers['Location'] = url
    return response


# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):
    """RestfulTest TODO API by ID."""

    @swagger.operation(
        responseClass='TodoModel',
        nickname='get',
        notes='Get a todo.',
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
        """Return the TODO item with id <strong>todo_id</strong>."""
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    @swagger.operation(
        nickname='delete',
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
        """Delete TODO item <strong>todo_id</strong>."""
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204


    @swagger.operation(
        responseClass='TodoModel',
        notes='Please make sure the todo <strong>todo_id</strong> already ' \
              'exists.  Changing the id is forbidden',
        nickname='update',
        parameters=[
            {
                "description": "Text of TODO item.",
                "name": "body",
                "required": True,
                "allowMultiple": False,
                "dataType": "TodoModel",
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 204,
                "message": "Updated."
            },
            {
                "code": 400,
                "message": "Invalid request body."
            },
            {
                "code": 404,
                "message": "Todo {} doesn't exist."
            }
        ]
    )
    @marshal_with(TodoModel.resource_fields)
    def put(self, todo_id):
        """Update a todo task

        This will be added to the <strong>Implementation Notes</strong>.
        It lets you put very long text in your api.
        """
        abort_if_todo_doesnt_exist(todo_id)
        args = update_parser.parse_args()
        for k, v in args.items():
            if v:
                setattr(TODOS[todo_id], k, v)
        return "", 204


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    """RestfulTest TODO API."""

    @swagger.operation(
        nickname='getAll',
        responseMessages=[
            {
                "code": 200,
                "message": "OK."
            }
        ]
    )
    def get(self):
        """Retrieve the list of all todo items"""
        return {k: marshal(v, v.resource_fields) for k, v in TODOS.items()}

    @swagger.operation(
        nickname='create',
        notes='Returns a redirect to the URL of the new TODO item.',
        responseClass='TodoModel',
        parameters=[
            {
                "description": "TODO Schema",
                "name": "body",
                "required": True,
                "allowMultiple": False,
                "dataType": "TodoModel",
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 201,
                "message": "Created."
            },
            {
                "code": 400,
                "message": "Todo {} already exist."
            }
        ])
    def post(self):
        """Create a new TODO item"""
        args = parser.parse_args()
        todo_id = 'todo%d' % (len(TODOS) + 1)
        TODOS[todo_id] = TodoModel(todo_id, args['task'], args.get('comment'))
        return redirect_to_todo(todo_id)

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')


if __name__ == '__main__':
    app.run(debug=True)