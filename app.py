from cgitb import reset

from flask import Flask
from flask import redirect
from flask import request
from flask import jsonify

from flasgger import Swagger

from service import StackService, StackError


app = Flask(__name__)
swagger = Swagger(app)

stacks = StackService()  # Dictionary to store stacks by ID


# Initialize Swagger with the root URL `/`

# Redirect root URL `/` to Swagger UI
@app.route('/')
def root():
    return redirect('/apidocs/')


# Create a new stack
@app.route('/stacks', methods=['POST'])
def create_stack():
    """
    Create a new stack
    ---
    responses:
      200:
        description: Stack created
    """
    stacks.create_stack()
    return jsonify({'message': 'Stack created'})


# Get an existing stack
@app.route('/stacks/<stack_id>', methods=['GET'])
def get_stack(stack_id):
    """
    Get a stack by ID
    ---
    parameters:
      - name: stack_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Returns the stack data
    """
    # Code to retrieve and return the stack
    stack = stacks.get_stack(stack_id)
    return jsonify({'stack': stack})

# Get all stacks
@app.route('/stacks', methods=['GET'])
def get_stacks():
    """
    Get all stacks
    ---
    responses:
      200:
        description: Returns all stacks
    """
    # Code to retrieve and return all stacks
    return jsonify({'stacks': stacks.get_stacks()})


# Push stack
@app.route('/stacks/<stack_id>/push', methods=['POST'])
def push_stack(stack_id):
    """
    Push a value to a stack
    ---
    parameters:
      - name: stack_id
        in: path
        type: string
        required: true
      - name: value
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Value pushed to stack
    """
    # Code to push value to stack
    value = request.args.get('value')

    stacks.push_stack(stack_id, float(value))
    return jsonify({'message': 'Value pushed to stack'})

# Delete a stack
@app.route('/stacks/<stack_id>', methods=['DELETE'])
def delete_stack(stack_id):
    """
    Delete a stack by ID
    ---
    parameters:
      - name: stack_id
        in: path
        type: string
        required: true
    responses:
      201:
        description: Stack deleted
    """
    # Code to delete the stack
    try:
        stacks.delete_stack(stack_id)
    except StackError:
        # Avert possible attack by not revealing if stack does not exist
        return jsonify({'message': ''}, 201)

    return jsonify({'message': 'Stack deleted'})


# Perform an operation on a stack
@app.route('/stacks/<stack_id>/<string:operation>', methods=['POST'])
def operate_stack(stack_id, operation):
    """
    Perform an operation on a stack
    ---
    parameters:
      - name: stack_id
        in: path
        type: string
        required: true
      - name: operation
        in: path
        type: string
        required: true
    responses:
      200:
        description: Operation performed on stack
    """
    # Code to perform operation (push, pop, etc.) on stack
    stacks.do_operation(stack_id, operation)
    return jsonify({
        'message': 'Operation succesful',
        'stack': stacks.get_stack(stack_id)
    })
