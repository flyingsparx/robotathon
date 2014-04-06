import sqlite3

def connect():
    con = sqlite3.connect("main.db")
    con.row_factory = sqlite3.Row
    c = con.cursor()
    return (con, c)

def disconnect(con):
    con.close()

def initalise():
    print "Initialising database..."
    con, c = connect()
    c.execute("CREATE TABLE IF NOT EXISTS user (id TEXT, email TEXT, username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS robot (robot_id TEXT, user_id TEXT, robot_name TEXT, robot_file TEXT, status NUMBER)")
    c.execute("CREATE TABLE IF NOT EXISTS battle (battle_id TEXT, user1_id TEXT, user2_id TEXT, robot1_id TEXT, robot2_id TEXT, robot1_name TEXT, robot2_name, timestamp NUMBER, score1 NUMBER, score2 NUMBER, history TEXT)")
    con.commit()
    disconnect(con)

def get_battles_of_user(user_id):
    con, c = connect()
    first = c.execute("""SELECT
            user.username as username,
            battle.score1 as home_score,
            battle.score2 as away_score,
            battle.robot1_name as home_robot,
            battle.robot2_name as away_robot,
            battle.timestamp as timestamp,
            battle.battle_id as id
            FROM battle
            LEFT JOIN user ON battle.user2_id=user.id WHERE battle.user1_id=?""",[user_id]).fetchall();
    second = c.execute("""SELECT
            user.username as username,
            battle.score1 as away_score,
            battle.score2 as home_score,
            battle.robot1_name as away_robot,
            battle.robot2_name as home_robot,
            battle.timestamp as timestamp,
            battle.battle_id as id
            FROM battle
            LEFT JOIN user ON battle.user1_id=user.id WHERE battle.user2_id=?""",[user_id]).fetchall();
    combined = first+second
    combined = sorted(combined, key=lambda k: k['timestamp'])
    combined.reverse()
    disconnect(con)
    return combined

def get_battle(battle_id):
    con, c = connect()
    row = c.execute("SELECT * FROM battle WHERE battle_id=?", [battle_id]).fetchone()
    disconnect(con)
    return row

def store_battle(battle_id, user1_id, user2_id, robot1_id, robot2_id, robot1_name, robot2_name, timestamp, score1, score2, history):
    con, c = connect()
    c.execute("INSERT INTO battle VALUES(?,?,?,?,?,?,?,?,?,?,?)", [battle_id, user1_id, user2_id, robot1_id, robot2_id, robot1_name, robot2_name, timestamp, score1, score2, history])
    con.commit()
    disconnect(con)



def create_user(id, email, username, password):
    con, c = connect()
    c.execute("INSERT INTO user VALUES(?,?,?,?)", [id, email, username, password])
    con.commit()
    disconnect(con)

def get_user_by_id(id):
    con, c = connect()
    row = c.execute("SELECT * FROM user WHERE id = ?", [id]).fetchone()
    disconnect(con)
    return row
 
def get_user_by_email(email):
    con, c = connect()
    row = c.execute("SELECT * FROM user WHERE email = ?", [email]).fetchone()
    disconnect(con)
    return row
   
def get_user_by_username(username):
    con, c = connect()
    row = c.execute("SELECT * FROM user WHERE username= ?", [username]).fetchone()
    disconnect(con)
    return row
  
def get_robots_of_user(id):
    con, c = connect()
    rows = c.execute("SELECT * FROM robot WHERE user_id= ?", [id]).fetchall()
    disconnect(con)
    return rows 

def get_all_robots(user_id):
    con,c = connect()
    rows = c.execute("SELECT robot_name, robot_id, username FROM robot AS r JOIN user AS u ON r.user_id=u.id WHERE r.status=1 and r.user_id != ?", [user_id]).fetchall()
    disconnect(con)
    return rows



def get_robot_by_id(id):
    con, c = connect()
    row = c.execute("SELECT * FROM robot WHERE robot_id= ?", [id]).fetchone()
    disconnect(con)
    return row 

def get_robot_by_name(name):
    con, c = connect()
    row = c.execute("SELECT * FROM robot WHERE robot_name= ?", [name]).fetchone()
    disconnect(con)
    return row 

def get_robot_source(robot):
    robot_file = open('./robots/'+robot['robot_file'], 'r')
    source = robot_file.read()
    robot_file.close()
    return source

def get_robot_owner(robot):
    con, c = connect()
    row = c.execute("SELECT * FROM user WHERE id= ?", [robot['user_id']]).fetchone()
    disconnect(con)
    return row 

def create_robot(robot_id, user_id, robot_name, robot_file):
    con, c = connect()
    c.execute("INSERT INTO robot VALUES(?,?,?,?,0)", [robot_id, user_id, robot_name, robot_file])
    con.commit()
    disconnect(con)

def robot_tested(robot_id, status):
    con, c = connect()
    if status == True:
        c.execute("UPDATE robot SET status = 1 WHERE robot_id = ?", [robot_id])
    if status == False:
        c.execute("UPDATE robot SET status = -1 WHERE robot_id = ?", [robot_id])
    con.commit()
    disconnect(con)    

def delete_robot(robot_id):
    con, c = connect()
    c.execute("DELETE FROM robot WHERE robot_id = ?", [robot_id])
    con.commit()
    disconnect(con)
