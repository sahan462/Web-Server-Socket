<?php
if (isset($_POST["submit"])) {
    // Check if both input fields are filled
    if (!empty($_POST["num1"]) && !empty($_POST["num2"])) {
        // Get the values entered by the user
        $num1 = $_POST["num1"];
        $num2 = $_POST["num2"];

        // Add the two numbers
        $result = $num1 + $num2;
    } else {
        // Display an error message if one or both fields are empty
        $error = "Both fields are required!";
    }
}
?>

<html>
<head>
    <title>Add Two Numbers</title>
</head>
<body>
    <h1>Add Two Numbers</h1>
    <form method="POST" action="">
        <label for="num1">Enter the first number:</label>
        <input type="text" id="num1" name="num1"><br><br>
        
        <label for="num2">Enter the second number:</label>
        <input type="text" id="num2" name="num2"><br><br>

        <input type="submit" name="submit" value="Add">
    </form>

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
