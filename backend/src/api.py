
import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from sqlalchemy import desc
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks_short():
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)
    return jsonify({
        'success': 200,
        'drinks': [drink.short() for drink in drinks]
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)
    return jsonify({
        "success": 200,
        "drinks": [drink.long() for drink in drinks]
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    body = request.get_json()
    if not body:
        abort(422)
    title = body.get('title').replace("\'", "\"")
    recipe = [body.get('recipe')]
    if title is None:
        abort(422)
    if recipe is None:
        abort(422)
    try:
        drink = Drink(title=title, recipe = str(recipe).replace("\'", "\""))
        drink.insert()
        new_drink = Drink.query.order_by(desc(Drink.id)).first()
        
        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        })
    except Exception as e:
        print(e)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    if drink is None:
        abort(404)
    title = body.get("title")
    recipe = body.get("recipe")
    if drink is None:
        abort(400)
    if title:
        drink.title = body.get("title")
    if recipe:
        drink.recipe = str([body.get("recipe")])
    drink.update()

    updated_drink = Drink.query.filter(Drink.id==id).one_or_none()
    return jsonify({
            "success": True,
            "drinks": [updated_drink.long()]
            })
    

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
        'success': True,
        'delete': drink.id
    })
    except Exception as e:
        print(e)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def Not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(404)
def AuthError(error):
    return jsonify({
        "code": 'Not found',
        "description": 'resource not found',
    }), 404

@app.errorhandler(400)
def AuthError(error):
    return jsonify({
        "code": 'Bad_request',
        "description": 'Bad Request',
    }), 400

@app.errorhandler(403)
def AuthError(error):
    return jsonify({
        "code": 'No_Permission',
        "description": 'No permission to access the resource',
        'status': 403
    }),403