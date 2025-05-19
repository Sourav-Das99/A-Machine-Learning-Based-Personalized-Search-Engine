<?php
session_start();


$servername = "localhost";
$username = "root";        
$password = "";            
$dbname = "dbase"; 


$conn = mysqli_connect($servername, $username, $password, $dbname);


if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}


if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $input_username = mysqli_real_escape_string($conn, $_POST['username']);
    $input_password = mysqli_real_escape_string($conn, $_POST['password']);
    
    
    $query = "SELECT * FROM admins WHERE username = '$input_username'";
    $result = mysqli_query($conn, $query);

    if (mysqli_num_rows($result) > 0) {
       
        $user = mysqli_fetch_assoc($result);
        
      
        if ($input_password === $user['password']) { 
            
            header("Location: http://127.0.0.1:5000/aaa");
            exit();
        } else {
            echo "<script>alert('Incorrect password.');</script>";
        }
    } else {
        echo "<script>alert('Username not found.');</script>";
    }
}
?>
 