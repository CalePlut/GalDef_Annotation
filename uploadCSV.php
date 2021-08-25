<?php
$filename = uniqid("Annot-".date("Y-m-d"), true)

echo move_uploaded_file(
  $_FILES["upfile"]["tmp_name"], 
  $filename
) ? "OK" : "ERROR UPLOADING";
?>