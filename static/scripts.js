document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const answerBtn = document.getElementById("answer-btn");
    const inputField = document.getElementById("chat-input"); // Đảm bảo ID đúng
    let previousQuestion = ""; // Biến lưu câu hỏi trước đó

    sendBtn.addEventListener("click", function () {
        sendMessage();
    });
    //thử để nhận phím khi nhập liệu xong bám enter.
    inputField.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            sendMessage(); // Gọi hàm gửi tin nhắn
        }
    });
    answerBtn.addEventListener("click", function () {
        answerMessage();
    });

    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === "") {
            alert("Vui lòng nhập câu hỏi!");
            return;
        }

        previousQuestion = message; // Lưu câu hỏi trước đó
        appendMessage("Bạn", message);
        chatInput.value = ""; // Xóa input sau khi gửi

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                appendMessage("AI", data.response);
            })
            .catch(error => {
                console.error("Lỗi khi gửi tin nhắn:", error);
                appendMessage("AI", "Có lỗi xảy ra, vui lòng thử lại!");
            });
    }

    function answerMessage() {
        const replyMessage = chatInput.value.trim();
        if (previousQuestion === "") {
            alert("Không có câu hỏi nào để trả lời!");
            return;
        }
        if (replyMessage === "") {
            alert("Vui lòng nhập câu trả lời!");
            return;
        }

        fetch('/save_reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: previousQuestion, reply: replyMessage })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // ✅ Thêm câu trả lời vào khung chat ngay sau khi lưu
                    appendMessage("Bạn (Trả lời)", replyMessage);
                    chatInput.value = ""; // Xóa input sau khi nhập câu trả lời
                } else {
                    alert("Lỗi khi lưu câu trả lời: " + data.message);
                }
            })
            .catch(error => {
                console.error("Lỗi khi lưu câu trả lời:", error);
            });

        chatInput.value = ""; // Xóa input sau khi nhập câu trả lời
    }

    function appendMessage(sender, message) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        // Nếu tin nhắn không bắt đầu bằng "Bạn", căn phải
        if (!message.startsWith("Bạn")) {
            messageElement.classList.add("right-align");
        }
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    selectAI = function (aiName, videoSrc) {
        console.log("Chọn AI:", aiName, "Video:", videoSrc);
        document.getElementById("video-source").src = videoSrc;
        document.getElementById("bg-video").load();
    };
});
