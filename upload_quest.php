<?php
$file_loc='./CSV_Files'; 
if(!is_dir($file_loc)) mkdir($file_loc);
$filename="quest_";
$filename=uniqid($filename);
$filename=$filename.".csv";
echo move_uploaded_file(
  $_FILES["upfile"]["tmp_name"], "$file_loc/$filename") ? "OK" : "ERROR UPLOADING";
?>