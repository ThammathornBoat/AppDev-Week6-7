from flask import Flask, request, jsonify, abort
from flask_basicauth import BasicAuth
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/studentsdb'  # MongoDB connection URI
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'password'
basic_auth = BasicAuth(app)
mongo = PyMongo(app)

@app.route('/')
def welcome():
    return "Welcome to Student Management API"

@app.route('/students', methods=['GET'])
@basic_auth.required
def get_all_students():
    students = mongo.db.students.find()
    return jsonify({'students': students}), 200

@app.route('/students/<int:std_id>', methods=['GET'])
@basic_auth.required
def get_one_student(std_id):
    student = mongo.db.students.find_one({'std_id': std_id})
    if student:
        return jsonify({'student': student}), 200
    else:
        return jsonify({'error': 'Student not found'}), 404

@app.route('/students', methods=['POST'])
@basic_auth.required
def create_student():
    data = request.get_json()
    if not data or 'std_id' not in data:
        abort(400)  # Bad Request

    existing_student = mongo.db.students.find_one({'std_id': data['std_id']})
    if existing_student:
        return jsonify({'error': 'Cannot create new student'}), 500

    new_student = {'std_id': data['std_id'], 'name': data['name'], 'age': data['age']}
    mongo.db.students.insert_one(new_student)
    return jsonify({'student': new_student}), 200

@app.route('/students/<int:std_id>', methods=['PUT'])
@basic_auth.required
def update_student(std_id):
    data = request.get_json()
    if not data:
        abort(400)  # Bad Request

    existing_student = mongo.db.students.find_one({'std_id': std_id})
    if existing_student:
        updated_student = {'std_id': std_id, 'name': data['name'], 'age': data['age']}
        mongo.db.students.update_one({'std_id': std_id}, {'$set': updated_student})
        return jsonify({'student': updated_student}), 200
    else:
        return jsonify({'error': 'Student not found'}), 404

@app.route('/students/<int:std_id>', methods=['DELETE'])
@basic_auth.required
def delete_student(std_id):
    result = mongo.db.students.delete_one({'std_id': std_id})
    if result.deleted_count > 0:
        return jsonify({'message': 'Student deleted successfully'}), 200
    else:
        return jsonify({'error': 'Student not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
