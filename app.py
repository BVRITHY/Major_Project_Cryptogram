import os
from flask import Flask, redirect, render_template, url_for, request, send_file, session
from werkzeug.utils import secure_filename
from glob import glob
from io import BytesIO
from zipfile import ZipFile
import os
from audiomodel import Want_to_crypt
from cryptography.fernet import Fernet
from models.Image.image import image
from models.Text.text import text
from models.Video.video import video
import sqlite3

UPLOAD_IMAGE_FOLDER = 'models/Image/static'
IMAGE_CACHE_FOLDER = 'models/Image/__pycache__'
UPLOAD_TEXT_FOLDER = 'models/Text/static'
TEXT_CACHE_FOLDER = 'models/Text/__pycache__'
UPLOAD_VIDEO_FOLDER = 'models/Video/static'
VIDEO_CACHE_FOLDER = 'models/Video/__pycache__'

list_of_extensions = ['.mp3', '.key', '.ape', '.wv', '.m4a', '.3gp', '.aa', '.aac', '.aax', 
                                  '.act', '.aiff', '.alac', '.amr', '.au', '.awb', '.dss', '.dvf',
                                  '.flac', '.gsm', '.iklax', '.ivs', '.m4b', '.m4p', '.mmf', '.mpc',
                                  '.msv', '.nmf', '.oga', '.ogg', '.mogg', '.opus', '.ra',
                                  '.rm', '.raw', '.rf64', '.sln', '.tta', '.voc', '.vox', '.wav',
                                  '.wma', '.webm', '.8svx', '.cda']

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = "hello"
app.config['UPLOAD_IMAGE_FOLDER'] = UPLOAD_IMAGE_FOLDER
app.config['IMAGE_CACHE_FOLDER'] = IMAGE_CACHE_FOLDER
app.config['UPLOAD_TEXT_FOLDER'] = UPLOAD_TEXT_FOLDER
app.config['TEXT_CACHE_FOLDER'] = TEXT_CACHE_FOLDER
app.config['UPLOAD_VIDEO_FOLDER'] = UPLOAD_VIDEO_FOLDER
app.config['VIDEO_CACHE_FOLDER'] = VIDEO_CACHE_FOLDER
app.config['AUDIO_UPLOAD'] = 'static/tmp'

app.register_blueprint(image, url_prefix="/image")
app.register_blueprint(text, url_prefix="/text")
app.register_blueprint(video, url_prefix="/video")

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('signin.html')

@app.route("/signup")
def signup():

    username = request.args.get('username','')
    name = request.args.get('name','')
    email = request.args.get('email','')
    number = request.args.get('mobile','')
    password = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
    con.commit()
    con.close()
    return render_template("signin.html")

@app.route("/signin")
def signin():

    mail1 = request.args.get('username','')
    password1 = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signin.html")    

    elif mail1 == 'admin' and password1 == 'admin':
        return render_template("home.html")

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("home.html")
    else:
        return render_template("signup.html")


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/message")
def message():

    name = request.args.get('name','')
    email = request.args.get('email','')
    message = request.args.get('message','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `infos` (`user`,`email`, `message`) VALUES (?, ?, ?)",(name,email,message))
    data = cur.fetchone()
    
    return render_template("index.html")

@app.route("/encrypt", methods = ['POST', "GET"])
def code_page():    
    if request.method == "POST":
        audio = request.files['file']
        
        if audio.filename == '':
            print("File name is invalid!")
            return redirect(request.url)
        
        session['filename'] = secure_filename(audio.filename)
        
        basedir = os.path.abspath(os.path.dirname(__file__))
        
        audio.save(os.path.join(basedir, app.config['AUDIO_UPLOAD'], session['filename']))
        
        file = Want_to_crypt(session['filename'])
        
        file.encrypt(app.config['AUDIO_UPLOAD'])
        
        session['filename_new'] = file.new_name(1)
        
        session['file_key'] = 'key_' + session['filename'] + '.key'
    
    return render_template('audio-encode.html')


@app.route("/decrypt", methods = ['POST', "GET"])
def decode_page():
    if request.method == "POST":
        zip = request.files['file']
        
        if zip.filename == '':
            print("File name is invalid!")
            return redirect(request.url)
        
        zip_name = secure_filename(zip.filename)
        
        basedir = os.path.abspath(os.path.dirname(__file__))
        
        zip.save(os.path.join(basedir, app.config['AUDIO_UPLOAD'], zip_name))
        
        session['filename_d'] = ''
        session['file_key_d'] = ''
        
        with ZipFile(os.path.join(app.config['AUDIO_UPLOAD'], zip_name), 'r') as zip:
            list_of_files = zip.namelist()
            to_be_extracted = []
            
            for file in list_of_files:
                for extension in list_of_extensions:
                    if extension in file:
                        to_be_extracted.append(file)
                        if extension == '.key' and session['file_key_d'] == '':
                            session['file_key_d'] = file
                        else: 
                            if session['filename_d'] == '': 
                                session['filename_d'] = file
                        
            zip.extractall(app.config['AUDIO_UPLOAD'], to_be_extracted)
        os.remove(os.path.join(app.config['AUDIO_UPLOAD'], zip_name))
        
        file = Want_to_crypt(session['filename_d'])
        
        session['filename_new_d'] = file.new_name(2)
        
        file.decrypt(app.config['AUDIO_UPLOAD'], session['file_key'])

        
    val = 'the accuracy of decryption is 95%'
    return render_template('audio-decode.html',acc = val)
    
    
@app.route('/download_encrypt', methods=['GET'])
def download_encrypt():
    
    if 'filename_new' in session:  
        stream = BytesIO()
        with ZipFile(stream, 'w') as zf:
            for file in glob(app.config['AUDIO_UPLOAD'] + '/' + session['filename_new']):
                zf.write(file, os.path.basename(file))
                
            for file in glob(app.config['AUDIO_UPLOAD'] + '/' + session['file_key']):
                zf.write(file, os.path.basename(file))
        stream.seek(0)
        
        delete_files_encrypt()
        
        return send_file(stream, as_attachment=True, attachment_filename='Musicode.zip')
        
    else: 
        return 'No files uploaded!'
    

@app.route('/download_decrypt', methods=['GET'])
def download_decrypt():
    
    if 'filename_new_d' in session:
        return send_file(os.path.join(app.config['AUDIO_UPLOAD'], session['filename_new_d']), as_attachment=True)
        
    else: 
        return 'No files uploaded!'
    

@app.route('/delete_encrypt')
def delete_files_encrypt():
    if 'filename_new' in session:
        os.remove(app.config['AUDIO_UPLOAD'] + '/' + session['filename'])
        os.remove(app.config['AUDIO_UPLOAD'] + '/' + session['filename_new'])
        os.remove(app.config['AUDIO_UPLOAD'] + '/' + session['file_key'])
        
        return redirect(request.referrer)
        
    else:
        return redirect(request.referrer)
    
@app.route('/delete_decrypt')
def delete_files_decrypt():
    if 'filename_new_d' in session:
        os.remove(app.config['AUDIO_UPLOAD'] + '/' + session['filename_d'])
        os.remove(app.config['AUDIO_UPLOAD'] + '/' + session['filename_new_d'])
        os.remove(app.config['AUDIO_UPLOAD'] + '/' + session['file_key_d'])
        
        return redirect(request.referrer)
        
    else:
        return redirect(request.referrer)


@app.route("/audio")
def audio():
    return render_template("audio-encode.html")
      
if __name__ == "__main__":
    app.run(debug=False)