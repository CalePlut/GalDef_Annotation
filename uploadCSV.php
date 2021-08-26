<?php
echo move_uploaded_file(
  $_FILES["upfile"]["tmp_name"], 
  uniqid("Annot-".date("Y-m-d"), true)
) ? "OK" : "ERROR UPLOADING";
?>