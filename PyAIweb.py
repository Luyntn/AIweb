import base64
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
import xml.etree.ElementTree as ET
import pyttsx3
import os
import random
import cv2


# Khai báo Flask app
app = Flask(__name__)

CHAT_HISTORY_FILE = "chat_history.xml"
camera = cv2.VideoCapture(0)  # Mở webcam

# Route phục vụ file trong thư mục 'static'
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

def init_chat_history():
    if not os.path.exists(CHAT_HISTORY_FILE):
        root = ET.Element("chatHistory")
        tree = ET.ElementTree(root)
        tree.write(CHAT_HISTORY_FILE)

def save_message(user_message_old, reply):
    tree = ET.parse(CHAT_HISTORY_FILE)
    root = tree.getroot()

    # Mã hóa user_message_old (câu hỏi cũ) và reply (câu trả lời mới)
    encoded_user_message_old = base64.b64encode(user_message_old.encode('utf-8')).decode('utf-8')
    encoded_reply = base64.b64encode(reply.encode('utf-8')).decode('utf-8')
    
    # Lưu vào XML
    entry = ET.SubElement(root, "entry")
    ET.SubElement(entry, "User").text = encoded_user_message_old
    ET.SubElement(entry, "Reply").text = encoded_reply
    tree.write(CHAT_HISTORY_FILE)



     # Load lại file XML sau khi lưu
    tree = ET.parse(CHAT_HISTORY_FILE)
    root = tree.getroot()  # Đảm bảo cây XML được cập nhật

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield ('--frame\r\n'
                   'Content-Type: image/jpeg\r\n\r\n' + frame + '\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    print("📩 Tin nhắn nhận được:"+ user_message)  # Debug xem có nhận tin nhắn không

    # Kiểm tra câu hỏi trong lịch sử và lấy câu trả lời ngẫu nhiên
    bot_response = get_bot_response(user_message)
    
  
    
    # Phát âm thanh phản hồi
    text_to_speech(bot_response)

    print("🤖 AI trả lời: "+ bot_response)  # Debug xem AI trả lời gì
    return jsonify({"response": bot_response})

@app.route('/save_reply', methods=['POST'])
def save_reply():
    data = request.json
    question = data.get("question")
    reply = data.get("reply")  # Sửa lại từ "answer" -> "reply"

    if not question or not reply:
        return jsonify({"success": False, "message": "Thiếu dữ liệu đầu vào!"})

    try:
        tree = ET.parse(CHAT_HISTORY_FILE)
        root = tree.getroot()

        new_entry = ET.SubElement(root, "entry")
        ET.SubElement(new_entry, "User").text = base64.b64encode(question.encode('utf-8')).decode('utf-8')
        ET.SubElement(new_entry, "Reply").text = base64.b64encode(reply.encode('utf-8')).decode('utf-8')

        tree.write(CHAT_HISTORY_FILE, encoding="utf-8", xml_declaration=True)

        return jsonify({"success": True, "message": "Câu trả lời đã được lưu!"})
    
    except Exception :
        return jsonify({"success": False, "message": "Lỗi: {str(e)}"})

def get_bot_response(user_message):
    tree = ET.parse(CHAT_HISTORY_FILE)
    root = tree.getroot()
    
    # Lọc các câu hỏi từ người dùng tương tự với user_message
    similar_responses = [decode_base64(entry.find("Reply").text) for entry in root.findall("entry") if user_message.lower() in decode_base64(entry.find("User").text).lower()]
    
    if similar_responses:
        # Lấy ngẫu nhiên một câu trả lời từ các câu trả lời tìm được
        return random.choice(similar_responses)
    else:
         return "Bạn có thể dạy tôi câu trả lời không?"

def decode_base64(encoded_string):
    try:
        return base64.b64decode(encoded_string.encode('utf-8')).decode('utf-8')
    except Exception:
        print("Error decoding base64: {e}")
        return ""

@app.route('/history', methods=['GET'])
def get_history():
    tree = ET.parse(CHAT_HISTORY_FILE)
    root = tree.getroot()
    chats = [{"User": decode_base64(entry.find("User").text), "Reply": decode_base64(entry.find("Reply").text)} for entry in root.findall("entry")]
    return jsonify(chats)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    init_chat_history()
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, render_template

app = Flask(__name__, template_folder='path/to/your/templates')

@app.route('/')
def index():
    return render_template('index.html')