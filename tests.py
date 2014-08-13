import json
import RestfulTest
import pytest


@pytest.fixture
def app():
    RestfulTest.app.config['TESTING'] = True
    return RestfulTest.app.test_client()


def get(app, id=None):
    """get: Helper to retrieve one or more todos.

    :param app: app test_client fixture
    :param id: todo id (options)
    :return: unpacked json value
    """
    url = '/todos/' + id if id else '/todos'
    rv = app.get(url)
    assert rv.status_code == 200
    return json.loads(rv.data)


def create(app, *tasks):
    urls = []
    for task in tasks:
        rv = app.post('/todos', content_type='application/json',
                      data=json.dumps({'task': task}))
        assert rv.status_code == 201
        urls.append(rv.headers['Location'])
    if len(tasks) == 1:
        return urls[0]
    return urls


def update(app, id, **kw):
    return app.put('/todos/' + id, content_type='application/json',
                   data=json.dumps(kw))


def clear(app):
    items = json.loads(app.get('/todos').data)
    for i in items:
        app.delete('/todos/' + i)


def populate(app):
    clear(app)
    create(app, 'abc', 'def', 'ghi')


def test_get_all(app):
    populate(app)
    assert get(app) == {
        'todo1': {'task': 'abc'},
        'todo2': {'task': 'def'},
        'todo3': {'task': 'ghi'},
    }


def test_post(app):
    clear(app)
    url = create(app, 'foo')
    assert url.endswith('/todos/todo1')


def test_get_one(app):
    populate(app)
    assert get(app, 'todo1') == {'task': 'abc'}

    rv = app.get('/todo/bogus')
    assert rv.status_code == 404


def test_update(app):
    populate(app)
    rv = update(app, 'todo1', task='yyy')
    assert rv.status_code == 204

    assert get(app, 'todo1') == {'task': 'yyy'}


def test_update_validation_fail(app):
    populate(app)
    rv = update(app, 'todo1', bogus='bogus')
    assert rv.status_code == 400

    rv = update(app, 'todo99', task='task')
    assert rv.status_code == 404


def test_swagger_root(app):
    rv = app.get('/_spec.json')
    assert rv.status_code == 200
    spec = json.loads(rv.data)
    assert spec['apiVersion'] == "0.1"
    assert len(spec['apis']) == 2
    assert set([o['method'] for o in spec['apis'][1]['operations']]) == set(['get', 'put', 'delete'])