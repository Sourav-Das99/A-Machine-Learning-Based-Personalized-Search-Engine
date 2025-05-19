<?php

$servername = "localhost";
$username = "root";
$password = "";
$dbname = "dbase";

$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $vname = $_POST['vname'];
    $genre = $_POST['genre'];
    $tags = $_POST['tags'];
    $description = $_POST['description'];
    $video = $_FILES['video'];
    $pdf = $_FILES['pdf']; // PDF file for notes

    // Check if the video file is uploaded
    if ($video['error'] === UPLOAD_ERR_NO_FILE) {
        echo "No video file was uploaded.";
        exit;
    }

    // Check for video file errors
    if ($video['error'] !== UPLOAD_ERR_OK) {
        echo "Video Upload Error: " . $video['error'];
        exit;
    }

    // Handle PDF file upload (optional)
    if ($pdf['error'] !== UPLOAD_ERR_NO_FILE && $pdf['error'] !== UPLOAD_ERR_OK) {
        echo "PDF Upload Error: " . $pdf['error'];
        exit;
    }

    // Check for video file size (max 150MB)
    $maxFileSize = 152 * 1024 * 1024; // 150MB
    if ($video['size'] > $maxFileSize) {
        echo "Error: Video file size exceeds the maximum allowed size of 150MB.";
        exit;
    }

    // Allowed video file types
    $allowedFileTypes = ['video/mp4', 'video/avi', 'video/mkv', 'video/webm'];
    if (!in_array($video['type'], $allowedFileTypes)) {
        echo "Error: Invalid video file type.";
        exit;
    }

    // Handle PDF file if uploaded
    if ($pdf['error'] === UPLOAD_ERR_OK) {
        // Allowed PDF file type
        if ($pdf['type'] !== 'application/pdf') {
            echo "Error: Only PDF files are allowed for notes.";
            exit;
        }

        // Process the PDF file
        $pdfFileName = uniqid() . "_" . basename($pdf['name']);
        $pdfFilePath = "static/pdfs/" . $pdfFileName;
        if (!move_uploaded_file($pdf['tmp_name'], $pdfFilePath)) {
            echo "Error uploading PDF file.";
            exit;
        }
    } else {
        $pdfFilePath = null; // No PDF uploaded
    }

    // Process the video file
    $videoFileName = uniqid() . "_" . basename($video['name']);
    $videoFilePath = "static/videos/" . $videoFileName;
    if (!move_uploaded_file($video['tmp_name'], $videoFilePath)) {
        echo "Error uploading video file.";
        exit;
    }

    // Insert data into the database
    $sql = "INSERT INTO tables (vname, genre, tags, description, location, pdf_location) VALUES (?, ?, ?, ?, ?, ?)";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssssss", $vname, $genre, $tags, $description, $videoFilePath, $pdfFilePath);

    if ($stmt->execute()) {
        echo "Video and PDF uploaded successfully!";
    } else {
        echo "Error inserting video and PDF into database: " . $stmt->error;
    }

    $stmt->close();
}

$conn->close();
?>
