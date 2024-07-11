var pizzaGroupCounter = 1;

var pizzaTypes = [
    "The Italian Vegetables Pizza",
    "The Napolitana Pizza",
    "The Thai Chicken Pizza",
    "The Four Cheese Pizza",
    "The Hawaiian Pizza",
    "The Green Garden Pizza",
    "The Barbecue Chicken Pizza",
    "The Southwest Chicken Pizza",
    "The Pepperoni, Mushroom, and Peppers Pizza",
    "The Vegetables + Vegetables Pizza",
    "The Spinach Pesto Pizza",
    "The Italian Supreme Pizza",
    "The Mexicana Pizza",
    "The Mediterranean Pizza",
    "The Spinach and Feta Pizza",
    "The Pepperoni Pizza",
    "The Brie Carre Pizza",
    "The Chicken Pesto Pizza",
    "The Chicken Alfredo Pizza",
    "The Soppressata Pizza",
    "The Five Cheese Pizza",
    "The Pepper Salami Pizza",
    "The Classic Deluxe Pizza",
    "The California Chicken Pizza",
    "The Greek Pizza",
    "The Calabrese Pizza",
    "The Spinach Supreme Pizza",
    "The Sicilian Pizza",
    "The Italian Capocollo Pizza",
    "The Prosciutto and Arugula Pizza",
    "The Big Meat Pizza",
    "The Spicy Italian Pizza"
];

var pizzaOptions = pizzaTypes.map(function(pizzaType) {
    return `<option value="${pizzaType.toLowerCase().replace(/ /g, "-")}">${pizzaType}</option>`;
}).join("\n");

let totalCostElement = document.getElementById('total_cost');
console.log(totalCostElement);
pizzaTypeElement = document.getElementById('pizza_type');
pizzaSizeElement = document.getElementById('pizza_size');
quantityElement = document.getElementById('quantity');
costElement = document.getElementById('cost');
console.log("costElement:", costElement);

costElement.addEventListener('change', function() {
    updateTotalCost()
});
pizzaTypeElement.addEventListener('change', function() {
    updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement)
});
pizzaSizeElement.addEventListener('change', function() {
    updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement)
});
quantityElement.addEventListener('change', function() {
    updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement)
});


function updateTotalCost() {
    // console.log("Updating Total Cost");
    let totalCost = 0;
    for (let costElement of document.querySelectorAll('#cost')) {
        console.log("Cost Element:", costElement);
        console.log("TCost:", costElement.textContent);
        totalCost += parseFloat(costElement.textContent);
    }
    console.log("Total Cost:", totalCost);
    console.log("TCOST ELEMENT", totalCostElement);
    totalCostElement.textContent = totalCost;
}

function updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement) {
    console.log("Pizza Type Element:", pizzaTypeElement, "Pizza Size Element:", pizzaSizeElement, "Quantity Element:", quantityElement, "Cost Element:", costElement);
    let pizzaType = pizzaTypeElement.options[pizzaTypeElement.selectedIndex].text;
    let pizzaSize = pizzaSizeElement.value;
    let quantity = quantityElement.value;

    getPizzaCost(pizzaType, pizzaSize, quantity)
        .then(totalCost => {
            costElement.textContent = totalCost;
            let event = new Event('change');
            costElement.dispatchEvent(event);
        });
}

function getPizzaCost(pizzaType, pizzaSize, quantity) {
    return fetch(`/pizza-cost/${pizzaType}/${pizzaSize}`)
        .then(response => response.json())
        .then(data => {
            // data.cost is the cost of the pizza
            console.log("Data Cost:", data.cost, "Quantity:", quantity);
            let totalCost = data.cost * quantity;
            console.log("Cost:", totalCost);
            return totalCost;
        });
}

document.getElementById('add-pizza').addEventListener('click', function() {
    var pizzaOrderFields = document.getElementsByClassName('pizza-order-fields')[0];

    var newPizzaOrderFields = document.createElement('div');
    newPizzaOrderFields.className = `pizza-group-${pizzaGroupCounter}`;
    newPizzaOrderFields.innerHTML = `
      
      <div class="form-group" style = "margin-top: 20px;">
        <label for="pizza_size">Size:</label>
        <select id="pizza_size" name="pizza_size">
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
        </select>
      </div>
      <div class="form-group">
        <label for="pizza_type">Type:</label>
        <select id="pizza_type" name="pizza_type">
            ${pizzaOptions}
        </select>
      </div>
      <div class="form-group">
        <label for="quantity">Quantity:</label>
        <input type="number" class="form-control" id="quantity" name="quantity" min="1" max="10" value="1">
      </div>
      <div class="form-group">
        <label for="cost">Cost:</label>
        <span id="cost"></span>
      </div>
        <button type="button" class="remove-pizza" style = "margin-top: 20px; margin-bottom: 20px;">Remove this pizza</button>
      <br>
    `;
    console.log(newPizzaOrderFields);
    let pizzaTypeElement = newPizzaOrderFields.querySelector('#pizza_type');
    let pizzaSizeElement = newPizzaOrderFields.querySelector('#pizza_size');
    let quantityElement = newPizzaOrderFields.querySelector('#quantity');
    let costElement = newPizzaOrderFields.querySelector('#cost');

    console.log("costElement:", costElement);
    costElement.addEventListener('change', function() {
        updateTotalCost()
    });
    pizzaTypeElement.addEventListener('change', function() {
        updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement)
    });
    pizzaSizeElement.addEventListener('change', function() {
        updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement)
    });
    quantityElement.addEventListener('change', function() {
        updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement)
    });

    updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement);
    newPizzaOrderFields.querySelector('.remove-pizza').addEventListener('click', function() {
        pizzaOrderFields.removeChild(newPizzaOrderFields);
        updateTotalCost();
    });
    pizzaOrderFields.appendChild(newPizzaOrderFields);

    pizzaGroupCounter++
});

// Call updateCost immediately when the script loads
updateCost(pizzaTypeElement, pizzaSizeElement, quantityElement, costElement);