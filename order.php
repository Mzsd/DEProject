<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $pizza_size = $_POST["pizza_size"];
    $pizza_type = $_POST["pizza_type"];
    $quantity = $_POST["quantity"];

    // Process each pizza in the order
    echo "Order received! Type: $pizza_type, Size: $pizza_size, Quantity: $quantity";
}
?>