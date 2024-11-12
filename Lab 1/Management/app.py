from flask import Flask, render_template, request, redirect, url_for, jsonify

import pymysql

app = Flask(__name__)

DATABASE = 'university'

DB_CONFIG = {
    'host': 'localhost',    # 数据库主机
    'port': 3306,           # 数据库端口
    'user': 'root',         # MySQL 用户名
    'password': '123456',   # MySQL 密码
    'database': DATABASE    # 数据库名称
}

@app.route('/')
def index():
    return redirect(url_for('table_student'))

# Page 1: Student Table - Query, Insert, Update, Delete
@app.get('/students')
def table_student():
    cur.execute('SELECT * FROM Student')
    students = cur.fetchall()
    return render_template('student.html', students=students)

@app.post('/students/insert')
def insert_student():
    SName = request.form['SName']
    SGender = request.form['SGender']
    GID = request.form['GID']

    # 插入学生信息
    cur.execute('INSERT INTO Student (SName, SGender, GID) VALUES (%s, %s, %s)', (SName, SGender, GID))
    con.commit()

    # 获取新插入的学生 ID
    SID = cur.lastrowid
    new_student = { "SID": SID, "GID": GID, "SName": SName, "SGender": SGender }
    return jsonify(new_student)

@app.post('/students/delete/<int:SID>')
def delete_student(SID):
    cur.execute('DELETE FROM Student WHERE SID = %s', (SID))
    con.commit()
    return jsonify({"success": True})

# Page 2: Course Table - Query, Insert, Update, Delete
@app.get('/courses')
def table_course():
    cur.execute('SELECT * FROM Course')
    courses = cur.fetchall()
    return render_template('course.html', courses=courses)

@app.post('/courses/insert')
def insert_course():
    CName = request.form['CName']
    Credits = request.form['Credits']
    DID = request.form['DID']

    # 插入课程信息
    cur.execute("INSERT INTO Course (CName, Credits, DID) VALUES (%s, %s, %s)", (CName, Credits, DID))

    # 获取新插入的课程 ID
    CID = cur.lastrowid
    con.commit()

    # 返回新插入课程的信息
    new_course = {"CID": CID, "CName": CName, "Credits": Credits, "DID": DID}
    return jsonify(new_course)

@app.post('/courses/delete/<int:CID>')
def delete_course(CID):
    # 删除课程
    cur.execute("DELETE FROM Course WHERE CID = %s", (CID))
    con.commit()

    return jsonify({"success": True})

# Page 3: Enrollment Table - Query, Insert, Delete
@app.get('/enrollments')
def table_enrollment():
    cur.execute('SELECT * FROM Enrollment')
    enrollments = cur.fetchall()
    return render_template('enrollment.html', enrollments=enrollments)

@app.route('/enrollments/insert', methods=['POST'])
def insert_enrollment():
    print(request.form)
    SID = request.form['SID']
    CID = request.form['CID']
    Score = request.form.get('Score', None)
    if Score == '':
        Score = None

    # 检查学生是否存在
    query_student_exist = "SELECT COUNT(*) FROM Student WHERE SID = %s"
    cur.execute(query_student_exist, (SID))

    if cur.fetchone()['COUNT(*)'] == 0:
        return jsonify({"success": False, "message": "不存在的学生"})

    # 检查课程是否存在
    query_course_exist = "SELECT COUNT(*) FROM Course WHERE CID = %s"
    cur.execute(query_course_exist, (CID))

    if cur.fetchone()['COUNT(*)'] == 0:
        return jsonify({"success": False, "message": "不存在的课程"})
    
    if Score != None:   # 更新成绩
        # 插入或者更新成绩
        insert_query = "INSERT INTO Enrollment (SID, CID, Score) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Score = VALUES(Score)"
        cur.execute(insert_query, (SID, CID, Score))
        con.commit()
        return jsonify({"success": True, "SID": SID, "CID": CID, "Score": Score})

    else:
        # 检查是否已经选课
        query_enroll_exist = "SELECT COUNT(*) FROM Enrollment WHERE SID = %s AND CID = %s"
        cur.execute(query_enroll_exist, (SID, CID))

        if cur.fetchone()['COUNT(*)'] != 0:
            return jsonify({"success": False, "message": "重复的选课"})

        # 插入选课信息
        insert_query = "INSERT INTO Enrollment (SID, CID, Score) VALUES (%s, %s, %s)"
        cur.execute(insert_query, (SID, CID, Score))
        con.commit()
        return jsonify({"success": True, "SID": SID, "CID": CID, "Score": Score})

@app.post('/enrollments/delete/<int:SID>/<int:CID>')
def delete_enrollment(SID, CID):
    # 删除选课
    cur.execute("DELETE FROM Enrollment WHERE SID = %s AND CID = %s", (SID, CID))
    con.commit()
    return jsonify({"success": True})

# Page 4: Feature Testing
@app.route('/test-funcs', methods=['GET', 'POST'])
def feature_test():
    return render_template('test_functions.html')

# 查询学生需要用到的所有教材
@app.route('/test-funcs/find-books', methods=['POST'])
def find_books():
    SID = request.form['studentID']
    DID = request.form['DID']

    try:
        # 查询学生选的课程及对应的教材
        query = """
            SELECT DISTINCT B.BName
            FROM Book B
            WHERE B.CID IN (
                SELECT C.CID
                FROM Course C
                WHERE C.CID IN (
                    SELECT E.CID
                    FROM Enrollment E
                    WHERE E.SID = %s
                ) AND C.DID = %s
            );
        """
        cur.execute(query, (SID, DID))
        books = [row['BName'] for row in cur.fetchall()]
    except:
        con.rollback()
    else:
        con.commit()

    return jsonify({"books": books})

# 查询学生的成绩平均值
@app.route('/test-funcs/find-avg-grade', methods=['POST'])
def find_avg_grade():
    students = []
    try:
        # 从视图里查询
        query = """
            SELECT * FROM Avg
        """
        cur.execute(query)
        results = cur.fetchall()

        for row in results:
            students.append({
                "SID": row["SID"],
                "SName": row["SName"],
                "avg_grade": row["avg_grade"]
            })
    except:
        con.rollback()
    else:
        con.commit()

    return jsonify({"students": students})

# 选课逻辑，检查时间冲突
@app.post('/test-funcs/enroll-course')
def enroll_course():
    SID = request.form['studentIDEnroll']
    CID = request.form['courseIDEnroll']

    try:
        # 检查学生是否存在
        query_student_exist = "SELECT COUNT(*) FROM Student WHERE SID = %s"
        cur.execute(query_student_exist, (SID))

        if cur.fetchone()['COUNT(*)'] == 0:
            return jsonify({"success": False, "message": "不存在的学生"})

        # 检查课程是否存在
        query_course_exist = "SELECT COUNT(*) FROM Course WHERE CID = %s"
        cur.execute(query_course_exist, (CID))

        if cur.fetchone()['COUNT(*)'] == 0:
            return jsonify({"success": False, "message": "不存在的课程"})

        # 检查是否已选该课程
        query_check_enrolled = "SELECT COUNT(*) FROM Enrollment WHERE SID = %s AND CID = %s"
        cur.execute(query_check_enrolled, (SID, CID))

        already_enrolled = cur.fetchone()['COUNT(*)']

        if already_enrolled > 0:
            return jsonify({"success": False, "message": "该课程已选"})

        # 查询学生已选课程的上课时间，检查是否冲突
        query_check_conflict = """
            SELECT COUNT(*) 
            FROM Enrollment E 
            JOIN Course_Room CR1 ON E.CID = CR1.CID
            JOIN Course_Room CR2 ON CR1.RID = CR2.RID
            WHERE E.SID = %s AND CR2.CID = %s AND CR1.ClassTime = CR2.ClassTime
        """
        cur.execute(query_check_conflict, (SID, CID))
        time_conflict = cur.fetchone()['COUNT(*)']

        if time_conflict > 0:
            return jsonify({"success": False, "message": "课程时间冲突"})

        # 无冲突，执行选课
        insert_query = "INSERT INTO Enrollment (SID, CID) VALUES (%s, %s)"
        cur.execute(insert_query, (SID, CID))

        con.commit()
    except:
        con.rollback()

    return jsonify({"success": True})


# Page 5: Feature Testing
@app.get('/test-config')
def config_test():
    return render_template('test_config.html')

@app.post('/test-config/create-view')
def test_config_view():
    try:

        # 创建视图
        cur.execute("""
        CREATE OR REPLACE VIEW Avg AS
        SELECT S.GID, S.SID, S.SName, AVG(E.Score) AS avg_grade
        FROM Student AS S
        JOIN Enrollment AS E
        ON E.SID = S.SID AND E.Score IS NOT NULL
        GROUP BY S.SID, S.SName
        HAVING avg_grade > 60
        """)

        con.commit()

        return jsonify({"success": True, "message": "视图创建成功"})
    except:
        return jsonify({"success": False, "message": "视图创建失败"})
    
@app.post('/test-config/create-index')
def test_config_index():
    try:
        # 创建索引
        cur.execute("CREATE INDEX idx_enrollment_sid_cid_grade ON Enrollment(SID, CID, Score);")
        con.commit()

        return jsonify({"success": True, "message": "索引创建成功"})
    except:
        return jsonify({"success": False, "message": "索引创建失败"})

# Page 6: Other Tables
@app.get('/others')
def table_other():
    cur.execute('SELECT * FROM Book')
    books = cur.fetchall()
    cur.execute('SELECT * FROM Term')
    terms = cur.fetchall()
    cur.execute('SELECT * FROM Room')
    rooms = cur.fetchall()
    cur.execute('SELECT * FROM Class')
    grades = cur.fetchall()
    cur.execute('SELECT * FROM Teacher')
    teachers = cur.fetchall()
    cur.execute('SELECT * FROM Course_Room')
    times = cur.fetchall()
    cur.execute('SELECT * FROM Course_Book')
    usebooks = cur.fetchall()
    return render_template(
        'other.html',
        books = books,
        terms = terms,
        rooms = rooms,
        grades = grades,
        teachers = teachers,
        times = times,
        usebooks = usebooks
    )

if __name__ == '__main__':
    con = pymysql.connect(host='localhost', port=3306, user='root', password='123456', charset='utf8', database='university')
    cur = con.cursor(pymysql.cursors.DictCursor)  # 执行sql语句的游标

    app.run(debug=True)