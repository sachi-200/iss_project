from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import hashlib
import os
import tkinter as tk
from tkinter import ttk
from pydub import AudioSegment
from moviepy.editor import VideoClip,ColorClip,VideoFileClip,CompositeVideoClip, concatenate_videoclips,AudioFileClip, vfx, clips_array
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.all import fadein, fadeout
from moviepy.video.fx import rotate
from moviepy.video import fx
from moviepy.video.fx.fadeout import fadeout
from moviepy.editor import ImageSequenceClip
from moviepy.video.fx.all import crop
import shutil
import subprocess
import pymysql
from PIL import Image
import os
from werkzeug.utils import secure_filename
import cv2
import mimetypes
import numpy as np
import psycopg2
from psycopg2 import Error
import base64


from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['DATABASE'] = 'postgresql://ars_project_24:nFB1gdzfCFoG3th7gxpEWw@iss-project-1-2-4150.7s5.aws-ap-south-1.cockroachlabs.cloud:26257/iss_project?sslmode=verify-full'

def connect_to_database():
    return psycopg2.connect(app.config['DATABASE'])

connection = connect_to_database()
db = connect_to_database()
mysql = connect_to_database()

def save_images_to_database(uploaded_images, user_id, connection):
    try:
        with connection.cursor() as cursor:
            # Iterate over uploaded images
            for image in uploaded_images:
                img_data = image.read()  # Read the image file
                # Insert image data into the database
                cursor.execute("""
                    INSERT INTO storeimages (user_id, storeimage)
                    VALUES (%s, %s)
                """, (user_id, psycopg2.Binary(img_data)))

                cursor.execute("""
                    INSERT INTO images (user_id, image)
                    VALUES (%s, %s)
                """, (user_id, psycopg2.Binary(img_data)))
            # Commit the transaction
        connection.commit()
        flash('Images uploaded successfully', 'success')
    except Error as e:
        flash(f'Error uploading images: {str(e)}', 'error')

@app.route('/upload', methods=['POST'])
def upload():
    if 'id' in session:
        user_id = session['id']

        # Check if files were provided in the request
        if 'images' in request.files:
            file_list = request.files.getlist('images')
            if not file_list:
                flash('No images provided', 'error')
                return redirect(url_for('home'))
        else:
            # Handle the case where files are submitted using a file input
            file_list = [request.files['images']]

        try:
            save_images_to_database(file_list, user_id, connection)
            flash('Images uploaded successfully', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error uploading images: {str(e)}', 'error')
            return redirect(url_for('home'))
    else:
        flash('Login required', 'error')
        return redirect(url_for('login'))




def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def write_login_info(username, email):
    with open('login.txt', 'w') as file:
        file.write(f'Username: {username}, Email: {email}\n')

def get_user_data(username) :
    return {"username": username} 

def resize_image(image_path, output_path, new_dimensions):
    """
    Resize an image to the specified dimensions.

    Parameters:
    - image_path: Path to the input image.
    - output_path: Path to save the resized image.
    - new_dimensions: Tuple (width, height) of the new dimensions.
    """
    image = Image.open(image_path)
    resized_image = image.resize(new_dimensions)
    resized_image.save(output_path)

def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width, height

def save_image(image_blob, image_path):
    with open(image_path, 'wb') as file:
        file.write(image_blob)

def download_image(image_url, image_path):
    response = request.get(image_url, stream=True)
    response.raise_for_status()

    # Get the content type from the response headers
    content_type = response.headers.get('content-type')
    
    # Use the mimetypes module to guess the extension based on content type
    extension = mimetypes.guess_extension(content_type)
    
    # If the extension is not recognized, default to '.jpg'
    if not extension:
        extension = '.jpg'

    # Update the image path with the determined extension
    image_path_with_extension = f"{image_path}{extension}"

    with open(image_path_with_extension, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

@app.route('/')
def index():
    return render_template('login.html')

# ... (your existing routes)

@app.route('/inbuilt')
def inbuilt():
    return render_template('inbuilt.html')

# @app.route('/get_audio_names')
# def get_audio_names():
#     try:
#         with db.cursor() as cursor:
#             cursor.execute("SELECT audio_name FROM audio")
#             audio_names = [row['audio_name'] for row in cursor.fetchall()]
#             return jsonify({'audio_names': audio_names})
#     except Exception as e:
#         return jsonify({'error': str(e)})
@app.route('/get_audio_names')
def get_audio_names():
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT audio_name FROM audio")
            audio_names = [row[0] for row in cursor.fetchall()]
            # audio_names = [row['audio_name'] for row in cursor.fetchall()]
            return jsonify({'audio_names': audio_names})
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        auth = request.form

        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (auth.get('username'),))
        user_data = cursor.fetchone()

        if user_data:
            stored_password = user_data[2]
            entered_password_hashed = hash_password(auth.get('password'))

            if stored_password == entered_password_hashed:
                session['id'] = user_data[0]
                session['username'] = auth.get('username')
                write_login_info(auth.get('username'), user_data[3])
                if auth.get('username') == 'Admin':
                   cursor = mysql.cursor()
                   cursor.execute("SELECT * FROM users")
                   user_details = cursor.fetchall()
                   return render_template('admin_screen.html', user_details=user_details)
                else:
                    flash('Login successful', 'success')
                    return redirect(url_for('success'))
            else:
                flash('Invalid username or password', 'error')
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        new_username = request.form.get('newUsername')
        new_password = request.form.get('newPassword')
        email = request.form.get('Email')

        if not new_username or not new_password or not email:
            flash('Missing field', 'error')
            return render_template('signup.html')

        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (new_username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists', 'error')
        else:
            hashed_password = hash_password(new_password)
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                           (new_username, hashed_password, email))
            mysql.commit()  # Commit the transaction
            flash('Signup successful, please login', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/success')
def success():
    if 'username' in session:
        username = session['username']
        return render_template('success.html',username = username)
    else:
        flash('Login Required','error')
        return redirect(url_for('login'))

@app.route('/home')
def home():
    username = session.get('username')
    return render_template('home.html', username=username)

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/page3')
def page3():
    return render_template('page3.html')

@app.route('/page4')
def page4():
    return render_template('page4.html')

@app.route('/view_photos', methods=['GET'])
def view_photos():
    if 'id' in session:
        user_id = session['id']
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, storeimage FROM storeimages WHERE user_id = %s", (user_id,))
            storimages = cursor.fetchall()            
            storimages = [{'id': image[0], 'storeimage': base64.b64encode(image[1]).decode('utf-8')} for image in storimages]
            return render_template('new2.html', images=storimages)
    else:
        flash('User not logged in', 'error')
        return redirect(url_for('login'))
    
@app.route('/view_my_photos', methods=['GET'])
def view_my_photos():
    if 'id' in session:
        user_id = session['id']
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, image FROM images WHERE user_id = %s", (user_id,))
            storimages = cursor.fetchall()            
            storimages = [{'id': image[0], 'image': base64.b64encode(image[1]).decode('utf-8')} for image in storimages]
            return render_template('new.html', images=storimages)
    else:
        flash('User not logged in', 'error')
        return redirect(url_for('login'))
    
@app.route('/browse', methods=['POST','GET'])
def browse() :
    return render_template('browse.html')

@app.route('/drag_drop', methods=['POST','GET']) 
def drag_drop() :
    return render_template('drag_drop.html')

@app.route('/upload_dragdrop', methods=['POST'])
def upload_dragdrop():
    try:
        if 'id' in session:
            user_id = session['id']
            # Check if files were provided in the request
            if 'images' in request.files:
                file_list = request.files.getlist('images')
                print("Received files:", file_list)  # Debugging statement
                if not file_list:
                    flash('No images provided', 'error')
                    return redirect(url_for('home'))
                # Save images to the database
                save_images_to_database(file_list, user_id,connection)
                flash('Images uploaded successfully', 'success')
                return redirect(url_for('home'))
            else:
                flash('No images provided', 'error')
                return redirect(url_for('home'))
        else:
            flash('Login required', 'error')
            return redirect(url_for('login'))
    except Exception as e:
        flash(f'Error uploading images: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/create_video',methods=['POST'])
def create_video():
    user_id = session['id']
    # Get selected background music and image duration from the frontend
    background_music = request.files.get('backgroundMusic')
    filename_music = request.form.get('selectedFilename')
    image_duration = int(request.form.get('imageDuration'))
    selected_transition = request.form.get('selected_transition')    
    durations_input = request.form['durations']
    video_quality = request.form.get('videoQuality')  # Retrieve selected video quality
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT image FROM images WHERE user_id = %s", (user_id,))
        selected_images = cursor.fetchall()
    
    # Create a temporary directory to store image files
    temp_dir = os.path.join(app.root_path, 'static', 'uploads', 'temp_images')
    try:
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Directory '{temp_dir}' created successfully.")
    except Exception as e:
        print(f"Error creating directory '{temp_dir}': {e}")


    try:
        # Download each image and save it to the temporary directory
        for idx, image_data in enumerate(selected_images):
            image_blob = image_data[0]  # Access the first element of the tuple
            print(image_blob)

            if image_blob:
            # Image is a longblob, use save_image function
                image_path = os.path.join(temp_dir, f'image_{idx + 1}.jpg')
                save_image(image_blob, image_path)
                resize_image(image_path,image_path,(736,500))
                width, height = get_image_dimensions(image_path)
                print(f"Width: {width}, Height: {height}")
            else:
                print("ERROR") 
                pass
        output_video_path = os.path.join(app.root_path, 'static', 'output_video.mp4')
        desired_video_duration =len(selected_images) * image_duration

        # Adjust video resolution based on selected video quality
        if video_quality == '360p':
            resolution = (480, 360)
        elif video_quality == '480p':
            resolution = (854, 480)
        elif video_quality == '720p':
            resolution = (1280, 720)
        else:
            # Default resolution if video quality is not recognized
            resolution = (1280, 720)


        
        durations = durations_input.split()
        if len(durations)>1:
            audio_files = request.files.getlist('backgroundMusic')
            audio_segments = []
            k= 0
            for audio_file, duration in zip(audio_files, durations):
                audio = AudioSegment.from_file(audio_file)
                k = k+ int(duration)
                duration_ms = int(duration) * 1000
                audio_segment = audio[:duration_ms]
                audio_segments.append(audio_segment)
                final_audio = sum(audio_segments)
                final_audio_path = os.path.join(app.root_path, 'static', 'uploads', 'final_audio.mp3')
                final_audio.export(final_audio_path, format="mp3")
                music_path = final_audio_path
            if k!= len(selected_images)* image_duration:
                return jsonify({"status": "error", "message": "Give appropriate values"})
        else:
            music_filename = background_music.filename
            music_path = os.path.join(app.root_path, 'static', 'uploads', music_filename)
            background_music.save(music_path)
            print(music_path)
            
        if selected_transition == 'No Transition':
            
            create_video_command = (
                f'ffmpeg -r 1/{image_duration} -start_number 1 -i {temp_dir}/image_%d.jpg -i {music_path} '
                f'-c:a aac -c:v libx264 -vf "fps=25,format=yuv420p" -pix_fmt yuv420p -t {desired_video_duration} {output_video_path}'
            )
        else:
            output_video_path = os.path.join(app.root_path, 'static')
            audio_clip = AudioFileClip(music_path)
            def image_to_clip(image_path, duration):
                return VideoFileClip(image_path).set_duration(duration)
            image_files = sorted([f for f in os.listdir(temp_dir) if f.startswith("image_") and f.endswith(".jpg")]) 
            clips = [image_to_clip(os.path.join(temp_dir, image_file), image_duration) for image_file in image_files]
            
            if selected_transition=='fade':
                translucent_clips=[]
                translucent_clips = [clip.crossfadein(2).crossfadeout(2) for clip in clips]
                final_clip = concatenate_videoclips(translucent_clips, method="compose")

            final_clip = final_clip.set_audio(audio_clip)
            final_clip = final_clip.subclip(0, desired_video_duration)            
            final_clip.write_videofile(os.path.join(output_video_path, 'output_video.mp4'), codec="libx264", audio_codec="aac", fps=25)
            return render_template('page4.html')

        print(temp_dir)
        print(music_path)
        print(output_video_path)
        print("Files in temp_images directory:", os.listdir(temp_dir))
        subprocess.run(create_video_command, shell=True)
        result = subprocess.run(create_video_command, shell=True, capture_output=True)
        print(result.stdout.decode())
        print(result.stderr.decode())
        
        return render_template('page4.html')
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
@app.route('/update_image_status', methods=['POST'])
def update_image_status():
    if 'id' in session:
        user_id = session['id']
        selected_images = request.form.getlist('selected_images[]')
        
        try:
            with connection.cursor() as cursor:
                # Convert selected images to tuple for SQL query
                selected_images_tuple = tuple(selected_images)
                
                # Delete images that are not selected
                cursor.execute("DELETE FROM images WHERE id NOT IN %s AND user_id = %s", (selected_images_tuple, user_id))
                connection.commit()
                
                # Fetch updated images
                cursor.execute("SELECT image FROM images WHERE user_id = %s", (user_id,))
                updated_images = cursor.fetchall()
                
                # Convert binary image data to base64 for rendering
                images_base64 = [base64.b64encode(img[0]).decode('utf-8') for img in updated_images]
                
                flash('Selected images saved successfully', 'success')
                return render_template('new3.html', images=images_base64)
        except psycopg2.Error as e:
            connection.rollback()
            print("Error occurred:", e)
            return jsonify({"status": "error", "message": "Failed to update image status. Error: " + str(e)})
    else:
        return jsonify({"status": "error", "message": "User not logged in"})


@app.route('/logout')
def logout():
    
    session.clear()
    flash('Logout successful', 'success')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
