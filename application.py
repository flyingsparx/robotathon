####
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
####


from flask import Flask, render_template, request, redirect, Response, url_for, session
import time, os, uuid, json, base64, hmac, urllib, random, db_manager, api

app = Flask(__name__)
app.secret_key = os.environ.get('ROBOT_SALT')


ALLOWED_EXTENSIONS = set(['py'])

def validate_session():
    if session == None:
        return False
    if 'token' not in session:
        return False
    if session['token'] == None:
        return False
    id = session['token'][:-5]
    global user
    user = db_manager.get_user_by_id(id)  
    if user == None:
        return False
    else:
        return user 

@app.route('/')
def home():
    if validate_session():
        robots = db_manager.get_robots_of_user(user['id']) 
        return render_template('dashboard.html', user = user, robots = robots, robot_count = len(robots))
    else:
        return render_template('home.html', user=None)
 
@app.route('/register', methods=['POST'])
def register():
    result = api.register_user(request.form['email'], request.form['username'], request.form['password1'], request.form['password2'])
    if result['error'] == False:
        session['logged'] = True
        session['token'] = result['id'] + str(random.randrange(10000,99999))
        del result['id']
    return json.dumps(result)

@app.route('/login', methods=['POST'])
def login():
    result = api.login_user(request.form['email'], request.form['password'])
    if result['error'] == False:
        session['logged'] = True
        session['token'] = result['id'] + str(random.randrange(10000,99999))
        del result['id']
    return json.dumps(result)

@app.route('/logout')
def logout():
    session['logged'] = False
    session['token'] = None
    return redirect(url_for('home'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload_robot', methods=['POST'])
def upload_robot():
    if validate_session():
        file = request.files['robot_file']
        if file and allowed_file(file.filename):
            robot_name = file.filename.rsplit(".",1)[0]
            filename = user['id']+"_"+str(uuid.uuid4())+".py"
            file.save('./robots/'+filename)
            result = api.create_robot(user, robot_name, filename)
            return json.dumps(result)
        else:
            return json.dumps({'error': True, 'message': 'Invalid file type'})
    else:
        return json.dumps({'error': True, 'message': 'Auth error'})    

@app.route('/delete_robot', methods=['GET'])
def delete_robot():
    if validate_session():
        id = request.args.get('id')
        api.delete_robot(user, id)
        return redirect(url_for('home'))
    else:
        return json.dumps({'error': True, 'message': 'Auth error'})

@app.route('/robot_source')
def view_robot_source():
    if validate_session():
        id = request.args.get('id')
        result = api.get_robot_source(user, id)
        return render_template('source.html', robot = result['robot'], source = result['source'], user=user)

@app.route('/arsenal/<username>')
def view_arsenal(username):
    print username
    if validate_session():
        arsenal = db_manager.get_user_by_username(username)
        if arsenal == None:
            return redirect(url_for('home'))
        robots = db_manager.get_robots_of_user(arsenal['id'])
        battles = db_manager.get_battles_of_user(arsenal['id'])
        print battles
        return render_template('arsenal.html', arsenal=arsenal, robots=robots, robot_count = len(robots), battle_count = len(battles), battles=battles, user=user)

@app.route('/find_battle')
def find_battle():
    if validate_session():
        arsenal = db_manager.get_robots_of_user(user['id'])
        robots = db_manager.get_all_robots(user['id'])
        return render_template('robot_list.html', arsenal = arsenal, robots = robots, user = user, robot_count = len(robots), arsenal_count = len(arsenal))
    else:
        return redirect(url_for('home'))

@app.route('/test')
def test():
    if validate_session():
        robot_id = request.args.get('id')
        result = api.test(robot_id)
        result['opposee'] = user
        return render_template('battle.html', result = result, user = user, test = True)

@app.route('/battle')
def battle():
    if validate_session():
        robot1_id = request.args.get('id1')
        robot2_id = request.args.get('id2')
        result = api.battle(user, robot1_id, robot2_id)
        return render_template('battle.html', result = result, user = user, test = False, )        
@app.route("/replay")
def replay():
    if validate_session():
        battle_id = request.args.get('id')
        result = api.get_battle(battle_id)
        return render_template('battle.html', result = result, user = user, test = False, replay = True)

# Main code
if __name__ == '__main__':
    db_manager.initalise()
    app.debug = True
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    
