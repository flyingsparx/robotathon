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
    c.execute("CREATE TABLE IF NOT EXISTS robot (robot_id TEXT, user_id TEXT, robot_name TEXT, robot_file TEXT)")
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
    c.execute("INSERT INTO robot VALUES(?,?,?,?)", [robot_id, user_id, robot_name, robot_file])
    con.commit()
    disconnect(con)

def delete_robot(robot_id):
    con, c = connect()
    c.execute("DELETE FROM robot WHERE robot_id = ?", [robot_id])
    con.commit()
    disconnect(con)
