from http import server
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime
import pymysql
"""
@TODO am not sure but i think something is wrong it is not connecting to the remote database.
i think it is a username and password issue
------------------------------------------------------------------------------
username ='admin'
password ="56c075795035208aec92acb612e14660a70f41a893fafcb1"
host ='spotze-db-do-user-8609256-0.b.db.ondigitalocean.com'
port ='25060'
database ='cruzers'
"""

app = Flask(__name__)

"""
@TODO replace the usename, password, host, port, database, with your default mysql data infomation.
NOTE : please use a local database to check 
"""

username ='root'
password =""
host ='localhost'
port ='3306'
database ='echu'
#mysql://username:password@host:port/database_name
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://'+username+':'+password+'@'+host+':'+port+'/'+database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app, resources={r'/*':{'origins':'*'}}) 
db = SQLAlchemy(app)


class Secret(db.Model):
    __tablename__ ="secrets"
    id = db.Column(db.Integer,primary_key =True)
    token = db.Column(db.String(120), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, expiry_date, created_at, updated_at):
        self.token = token
        self.expiry_date = expiry_date
        self.created_at = created_at
        self.updated_at = updated_at

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'token': self.token,
            'expiry_date': self.expiry_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            }

db.create_all()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','POST,GET,PATCH,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials','true')
    #response.headers.add('Access-Control-Allow-Origin','*')
    return response

# home info
@app.route('/')
def hello():
    return jsonify({
        'hello': 'hello world'
    })


#creating or inserting a new token route
@app.route('/tokens', methods =['POST'] )
def create_token():
    data = request.get_json()
    if 'token' in data:
        try:
            token = data['token']
            now = datetime.datetime.today()
            exp = now + datetime.timedelta(days=30)
            
            add = Secret(token = token, expiry_date = exp,created_at = now , updated_at = now)
            add.insert()

            return jsonify({
                'success': True,
                'response': "added succesfully",
                'created': add.id
            })
        except:
            abort(422)
    else:
        abort(404)


#updating or editing an existing token route
@app.route('/tokens/<int:id>', methods =['PATCH'] )
def update_token(id):
    data = request.get_json()
    if 'token' in data:
        try:
            query = Secret.query.get(id)
            token = data['token']
            now = datetime.datetime.today()
            exp = now + datetime.timedelta(days=30)
            
            query.token = token
            query.expiry_date = exp
            query.updated_at = now
            query.update()

            return jsonify({
                'success': True,
                'response': "updated succesfully",
                'updated': query.id
            })
        except:
            abort(422)
    else:
        abort(404)


# viewing all tokens data
@app.route('/tokens')
def show_all_tokens():
    try:
        query = Secret.query.all()
        datas ={data.id : data.format() for data in query}

        return jsonify({
            'success': True,
            'response': datas
        })
    except:
        abort(404)


#viewing a specific token data
@app.route('/tokens/<int:id>')
def show_token(id):
    try:
        query = Secret.query.get(id)

        return jsonify({
            'success': True,
            'response': query.format()
        })
    except:
        abort(404)


#deleting a specific token
@app.route('/tokens/<int:id>/delete', methods=['DELETE'])
def delete_token(id):
    try:
        query = Secret.query.get(id)
        query.delete()

        return jsonify({
            'success': True,
            'response': 'deleted successfully',
            'deleted': query.id
        })
    except:
        abort(404)
# verifying token route
@app.route('/tokens/search', methods =['POST'] )
def search():
    data = request.get_json()
    if 'search' in data:
        try:
            search = data['search']
            query = Secret.query.filter_by(token = search).first()

            if query :
                now = datetime.datetime.today()
                if query.expiry_date >= now:

                    return jsonify({
                    'success': True,
                    'response': "token is still valid . will expire in {}".format(query.expiry_date - now),
                    'expiring_date': query.expiry_date,
                    'time_diff' : str(query.expiry_date - now),
                     })

                else:

                    return jsonify({
                    'success': True,
                    'response': "token has expired ",
                    'expiring_date': query.expiry_date
                     })
            else:

               return jsonify({
                    'success': False,
                    'response': "token not found ",
                    
                     }) 
        except:
            abort(422)
    else:
        abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        'success': False,
        'message': 'request not found',
        'error': 404,
    }),404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'message': 'unprocessable request',
        'error': 422,
    }),422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'message': 'bad request',
        'error': 400,
    }),400

@app.errorhandler(405)
def invalid_method(error):
    return jsonify({
        'success': False,
        'message': 'invalid method',
        'error': 405,
    }),405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'message': 'internal server error',
        'error': 500,
    }),500

if __name__ == "__main__":
    app.run( debug=True)