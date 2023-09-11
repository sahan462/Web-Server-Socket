<?php
if (isset($_GET["submit"])) {
    // Check if both input fields are filled
    if (!empty($_GET["num1"]) && !empty($_GET["num2"])) {
        // Get the values entered by the user
        $num1 = $_GET["num1"];
        $num2 = $_GET["num2"];

        // Add the two numbers
        $result = $num1 + $num2;
    } else {
        // Display an error message if one or both fields are empty
        $error = "Both fields are required!";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Add Two Numbers Result</title>
</head>
<body>
    <h1>Add Two Numbers Result</h1>
    
    <?php
    if (isset($result)) {
        echo "<p>Result: $result</p>";
    }

    if (isset($error)) {
        echo "<p>Error: $error</p>";
    }
    ?>
</body>
</html>
