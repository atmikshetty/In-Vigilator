from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
import threading as th
import audio
import head_pose
import detection
import sqlite3
import csv
import re
from collections import Counter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



app = Flask(__name__)
socketio = SocketIO(app)

# Function to create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to start proctoring
def start_proctoring():
    head_pose_thread = th.Thread(target=head_pose.pose)
    audio_thread = th.Thread(target=audio.sound)
    detection_thread = th.Thread(target=detection.run_detection)

    head_pose_thread.start()
    audio_thread.start()
    detection_thread.start()

    head_pose_thread.join()
    audio_thread.join()
    detection_thread.join()
    
    # After the detection is complete, redirect to the report route
    return redirect(url_for('report'))

def start_proctoring_thread():
    proctoring_thread = th.Thread(target=start_proctoring)
    proctoring_thread.start()

# Function to read data from CSV file
def read_data_from_csv(file_path):
    data = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

# Function to generate report
def generate_report():
    data = read_data_from_csv('detections.csv')
    
    # Extract cheat probability values
    cheat_probabilities = [float(entry['Cheat Probability']) for entry in data]

    # Calculate average cheat probability
    total_percentage = sum(cheat_probabilities)
    average_percentage = total_percentage / len(data) if data else 0

    # Combine all cheat probabilities into a single string
    cheat_text = ' '.join([str(prob) for prob in cheat_probabilities])

    # Tokenize the cheat text using regular expressions
    tokens = re.findall(r'\w+', cheat_text.lower())

    # Define stopwords
    stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 
                      'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                      'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
                      'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
                      'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
                      'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
                      'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above',
                      'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 
                      'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 
                      'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
                      'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should',
                      'now'])
    
    # Remove stopwords
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Calculate word frequency distribution
    word_counts = Counter(filtered_tokens)
    most_common_words = word_counts.most_common(5)  # Get the top 5 most common words

    return data, average_percentage, most_common_words

@app.route('/report')
def report():
    data, average_percentage, most_common_words = generate_report()
    return render_template('report.html', data=data, average_percentage=average_percentage, most_common_words=most_common_words)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username and password match the stored credentials
        conn = create_connection('database.db')
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                row = cursor.fetchone()
                if row:
                    # If the user is authenticated, start the proctoring
                    start_proctoring_thread()
                    return redirect(url_for('index'))
                else:
                    return 'Invalid username or password'
            except sqlite3.Error as e:
                print("Error:", e)
            finally:
                conn.close()
        else:
            return 'Failed to connect to the database'
    else:
        return redirect(url_for('index'))

@app.route('/send_report', methods=['POST'])
def send_report():
    if request.method == 'POST':
        proctor_name = request.form['proctorName']
        proctor_email = request.form['proctorEmail']
        data, average_percentage, most_common_words = generate_report()
        
        try:
            # Email configuration
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'atmikshetty10@gmail.com'
            sender_password = 'xowq jqag jzwy crpy'
            
            # Create a multipart message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = proctor_email
            msg['Subject'] = 'Proctoring Report'

            # Generate the report content
            report_content = f"Hello {proctor_name},\n\nHere is the proctoring report:\n\n"
            report_content += f"Average Cheat Percentage: {average_percentage}\n"
            report_content += "Most Common Words:\n"
            for word, count in most_common_words:
                report_content += f"- {word}: {count}\n"

            # Add body to email
            msg.attach(MIMEText(report_content, 'plain'))

            # Establish a connection to the SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()

            # Log in to the SMTP server
            server.login(sender_email, sender_password)

            # Send the email
            server.sendmail(sender_email, proctor_email, msg.as_string())

            # Quit the server
            server.quit()

            return 'Report sent successfully!'
        except Exception as e:
            return f'Failed to send report: {str(e)}'


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)
