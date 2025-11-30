<!-- login.php -->
<?php
// 데이터베이스 연결 정보
$servername = "localhost";
$username = "your_username";
$password = "your_password";
$dbname = "your_database_name";

// 데이터베이스 연결
$conn = new mysqli($servername, $username, $password, $dbname);

// 연결 확인
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// POST로 전송된 사용자명과 비밀번호 가져오기
$username = $_POST['username'];
$password = $_POST['password'];

// 사용자명과 비밀번호를 이용하여 데이터베이스에서 검색
$sql = "SELECT * FROM users WHERE username='$username'";
$result = $conn->query($sql);

// 검색 결과 확인
if ($result->num_rows > 0) {
    $user = $result->fetch_assoc();
    // 비밀번호 확인
    if (password_verify($password, $user['password'])) {
        // 로그인 성공
        echo "Login successful!";
    } else {
        // 비밀번호 불일치
        echo "Invalid password!";
    }
} else {
    // 사용자명이 없음
    echo "User not found!";
}

// 연결 종료
$conn->close();
?>