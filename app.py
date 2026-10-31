from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'online_exam_secret_key_2024'

# Sample data for demonstration
USERS = {
    'student1': {'password': 'pass123', 'role': 'student', 'name': 'John Doe'},
    'student2': {'password': 'pass123', 'role': 'student', 'name': 'Jane Smith'},
    'teacher1': {'password': 'admin123', 'role': 'teacher', 'name': 'Prof. Anderson'}
}

EXAMS = [
    {
        'id': 1,
        'name': 'Python Programming',
        'questions': 10,
        'duration': 15,
        'subject': 'Computer Science'
    },
    {
        'id': 2,
        'name': 'Data Structures',
        'questions': 8,
        'duration': 12,
        'subject': 'Computer Science'
    },
    {
        'id': 3,
        'name': 'Web Development',
        'questions': 12,
        'duration': 20,
        'subject': 'Information Technology'
    }
]

QUESTIONS = {
    1: [
        {'id': 1, 'question': 'What is Python?', 'options': ['A programming language', 'A snake', 'A car', 'A food'], 'answer': 0},
        {'id': 2, 'question': 'Which keyword is used to define a function in Python?', 'options': ['function', 'def', 'func', 'define'], 'answer': 1},
        {'id': 3, 'question': 'What is the output of print(2**3)?', 'options': ['6', '8', '9', '5'], 'answer': 1},
        {'id': 4, 'question': 'Which data type is immutable in Python?', 'options': ['List', 'Dictionary', 'Tuple', 'Set'], 'answer': 2},
        {'id': 5, 'question': 'What does len() function do?', 'options': ['Returns length', 'Returns type', 'Returns value', 'Returns index'], 'answer': 0},
        {'id': 6, 'question': 'Which symbol is used for comments in Python?', 'options': ['//', '/*', '#', '--'], 'answer': 2},
        {'id': 7, 'question': 'What is PIP in Python?', 'options': ['Package installer', 'IDE', 'Compiler', 'Debugger'], 'answer': 0},
        {'id': 8, 'question': 'Which of the following is a valid variable name?', 'options': ['2var', 'var_2', 'var-2', 'var 2'], 'answer': 1},
        {'id': 9, 'question': 'What is the file extension for Python files?', 'options': ['.python', '.py', '.pt', '.pyt'], 'answer': 1},
        {'id': 10, 'question': 'Which operator is used for floor division?', 'options': ['/', '//', '%', '**'], 'answer': 1}
    ],
    2: [
        {'id': 1, 'question': 'What is a Stack?', 'options': ['LIFO structure', 'FIFO structure', 'Random access', 'None'], 'answer': 0},
        {'id': 2, 'question': 'What is the time complexity of binary search?', 'options': ['O(n)', 'O(log n)', 'O(n^2)', 'O(1)'], 'answer': 1},
        {'id': 3, 'question': 'Which data structure uses FIFO?', 'options': ['Stack', 'Queue', 'Tree', 'Graph'], 'answer': 1},
        {'id': 4, 'question': 'What is a linked list?', 'options': ['Array', 'Linear data structure', 'Tree', 'Graph'], 'answer': 1},
        {'id': 5, 'question': 'What is the worst case of Quick Sort?', 'options': ['O(n)', 'O(n log n)', 'O(n^2)', 'O(1)'], 'answer': 2},
        {'id': 6, 'question': 'Which traversal visits root first?', 'options': ['Inorder', 'Preorder', 'Postorder', 'Level order'], 'answer': 1},
        {'id': 7, 'question': 'What is a complete binary tree?', 'options': ['All levels filled', 'Only leaves', 'One child', 'No children'], 'answer': 0},
        {'id': 8, 'question': 'Hash table uses which technique?', 'options': ['Hashing', 'Sorting', 'Searching', 'Traversing'], 'answer': 0}
    ],
    3: [
        {'id': 1, 'question': 'What does HTML stand for?', 'options': ['Hyper Text Markup Language', 'High Tech ML', 'Home Tool ML', 'None'], 'answer': 0},
        {'id': 2, 'question': 'Which tag is used for links?', 'options': ['<link>', '<a>', '<href>', '<url>'], 'answer': 1},
        {'id': 3, 'question': 'What does CSS stand for?', 'options': ['Cascading Style Sheets', 'Computer Style Sheets', 'Creative Style Sheets', 'Colorful Style Sheets'], 'answer': 0},
        {'id': 4, 'question': 'Which property changes text color?', 'options': ['text-color', 'color', 'font-color', 'text-style'], 'answer': 1},
        {'id': 5, 'question': 'What is JavaScript?', 'options': ['Programming language', 'Markup language', 'Database', 'Server'], 'answer': 0},
        {'id': 6, 'question': 'Which HTML tag contains JavaScript?', 'options': ['<js>', '<javascript>', '<script>', '<code>'], 'answer': 2},
        {'id': 7, 'question': 'What is Bootstrap?', 'options': ['CSS Framework', 'JS Library', 'Database', 'Server'], 'answer': 0},
        {'id': 8, 'question': 'Which unit is relative to viewport width?', 'options': ['px', 'em', 'vw', 'pt'], 'answer': 2},
        {'id': 9, 'question': 'What is DOM?', 'options': ['Document Object Model', 'Data Object Model', 'Digital Ordinance Model', 'None'], 'answer': 0},
        {'id': 10, 'question': 'Which method selects element by ID?', 'options': ['querySelector', 'getElementById', 'getElement', 'selectId'], 'answer': 1},
        {'id': 11, 'question': 'What is responsive design?', 'options': ['Adapts to screen size', 'Fast loading', 'Colorful design', 'None'], 'answer': 0},
        {'id': 12, 'question': 'Which is a CSS preprocessor?', 'options': ['SASS', 'jQuery', 'React', 'Node'], 'answer': 0}
    ]
}

# Store exam results
RESULTS = []

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        if username in USERS and USERS[username]['password'] == password:
            if USERS[username]['role'] == role:
                session['user'] = username
                session['role'] = role
                session['name'] = USERS[username]['name']
                if role == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                return redirect(url_for('student_dashboard'))
            else:
                error = 'Invalid role for this account'
        else:
            error = 'Invalid username or password'
    
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    success = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        name = request.form.get('name', username)
        
        if username in USERS:
            error = 'Username already exists'
        elif password != confirm_password:
            error = 'Passwords do not match'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters'
        else:
            USERS[username] = {'password': password, 'role': role, 'name': name}
            success = 'Account created successfully! Please login.'
    
    return render_template('signup.html', error=error, success=success)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('teacher_dashboard'))
    return render_template('student_dashboard.html', 
                         name=session.get('name'), 
                         exams=EXAMS)

@app.route('/exam/<int:exam_id>')
@login_required
def exam(exam_id):
    if session.get('role') != 'student':
        return redirect(url_for('teacher_dashboard'))
    
    exam_data = next((e for e in EXAMS if e['id'] == exam_id), None)
    if not exam_data:
        return redirect(url_for('student_dashboard'))
    
    questions = QUESTIONS.get(exam_id, [])
    return render_template('exam.html', 
                         exam=exam_data, 
                         questions=questions,
                         total_questions=len(questions))

@app.route('/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    data = request.get_json()
    exam_id = data.get('exam_id')
    answers = data.get('answers', {})
    time_per_question = data.get('time_per_question', {})
    total_time = data.get('total_time', 0)
    
    questions = QUESTIONS.get(exam_id, [])
    correct = 0
    total = len(questions)
    
    for q in questions:
        q_id = str(q['id'])
        if q_id in answers and answers[q_id] == q['answer']:
            correct += 1
    
    score = (correct / total) * 100 if total > 0 else 0
    passed = score >= 40
    
    # Check for suspicious timing (less than 3 seconds per question average)
    avg_time = total_time / total if total > 0 else 0
    suspicious = avg_time < 3
    
    result = {
        'student_name': session.get('name'),
        'username': session.get('user'),
        'exam_id': exam_id,
        'exam_name': next((e['name'] for e in EXAMS if e['id'] == exam_id), 'Unknown'),
        'correct': correct,
        'total': total,
        'score': round(score, 1),
        'passed': passed,
        'time_per_question': time_per_question,
        'total_time': total_time,
        'suspicious': suspicious
    }
    
    RESULTS.append(result)
    session['last_result'] = result
    
    return jsonify({'success': True, 'result_id': len(RESULTS) - 1})

@app.route('/result')
@login_required
def result():
    result_data = session.get('last_result')
    if not result_data:
        return redirect(url_for('student_dashboard'))
    return render_template('result.html', result=result_data)

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('student_dashboard'))
    return render_template('teacher_dashboard.html', 
                         name=session.get('name'), 
                         results=RESULTS)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
