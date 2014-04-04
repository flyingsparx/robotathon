import db_manager
import uuid, random, hashlib
from rgkit import run

salt = '10988f4a-1d23-4a90-a34d-20ee36294d07'

def hash_password(password):
    hashed = hashlib.sha1(password + salt).hexdigest()    
    return hashed

def check_password(password, hash):
    hashed = hashlib.sha1(password + salt).hexdigest()
    if(hashed == hash):
        return True
    return False 
    
def register_user(email, username, password1, password2):
    result = {}
    email = email.lower()
    if "@cs.cf.ac.uk" not in email and "@cardiff.ac.uk" not in email and "@cs.cardiff.ac.uk" not in email:
        result['error'] = True
        result['message'] = 'Invalid email.'
        return result
    
    if password1 != password2:
        result['error'] = True
        result['message'] = 'Your passwords do not match.'
        return result

    email_row = db_manager.get_user_by_email(email) 
    if email_row is not None:
        result['error'] = True
        result['message'] = 'Email address already taken.'
        return result
    
    username_row = db_manager.get_user_by_username(username)
    if username_row is not None:
        result['error'] = True      
        result['message'] = 'Username is already taken.'
        return result

    id = uuid.uuid4()
    db_manager.create_user(str(id), email, username, hash_password(password1))
    result['error'] = False
    result['id'] = str(id)
    return result
    
def login_user(email, password):
    result = {}
    email = email.lower()
    email_row = db_manager.get_user_by_email(email)
    if email_row is None:
        result['error'] = True
        result['message'] = 'Email is not registered.'   
        return result
    if not check_password(password, email_row['password']):
        result['error'] = True
        result['message'] = 'Password is incorrect.'
        return result
    result['error'] = False
    result['id'] = email_row['id']
    return result

def create_robot(user, robot_name, filename):
    result = {}
    name_row = db_manager.get_robot_by_name(robot_name)
    if name_row is not None:
        result['error'] = True
        result['message'] = 'There is already another robot with that name.'
        return result
    robot_id = str(uuid.uuid4())
    db_manager.create_robot(robot_id, user['id'], robot_name, filename)
    result['error'] = False
    return result

def delete_robot(user, robot_id):
    result = {}
    robot = db_manager.get_robot_by_id(robot_id)
    if robot == None:
        result['error'] = True
        result['message'] = 'Invalid robot.'
        return result
    if robot['user_id'] != user['id']:
        result['error'] = True
        result['message'] = 'Auth error.'
        return result
    db_manager.delete_robot(robot_id)
    result['error'] = False
    return result

def get_all_robots(user):
    robots = db_manager.get_all_robots(user)
    return robots 

def get_robot_source(user, robot_id):
    result = {}
    robot = db_manager.get_robot_by_id(robot_id)
    if robot == None:
        result['error'] = True
        result['message'] = 'Invalid robot.'
        return result
    if robot['user_id'] != user['id']:
        result['error'] = True
        result['message'] = 'Auth error.'
        return result
    source = db_manager.get_robot_source(robot)
    result['error'] = False
    result['robot'] = robot
    result['source'] = source
    return result

def battle(robot1_id, robot2_id):
    result = {}
    robot1 = db_manager.get_robot_by_id(robot1_id)
    robot2 = db_manager.get_robot_by_id(robot2_id)
    if robot1 == None or robot2 == None:
        result['error'] = True
        result['messgae'] = 'There is an invalid robot.'
        return result
    robot1_file = './robots/'+robot1['robot_file']
    robot2_file = './robots/'+robot2['robot_file']
    
    runner = run.Runner(player1_file=robot1_file, player2_file=robot2_file)
    runner.run()
    game = runner.game 
    options = runner.options
    history = game.get_history()
    scores = game.get_scores() 
    opposer = db_manager.get_robot_owner(robot2) 
    
    map_file = open(options.map_filepath, 'r')
    map = map_file.read()
    map_file.close()    

    for item in history:
        for item2 in item:
            item2['location'] = [item2['location'][0],item2['location'][1]]

    result['map'] = map.replace("(","[").replace(")","]")
    result['robot1'] = robot1
    result['robot2'] = robot2 
    result['error'] = False
    result['scores'] = scores
    result['history'] = history
    result['opposer'] = opposer
    return result
