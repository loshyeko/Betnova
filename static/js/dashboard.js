// ==============================
// BetNova Dashboard
// ==============================

const selections = [];

document.addEventListener("DOMContentLoaded", () => {

    const oddButtons = document.querySelectorAll(".odd");

    oddButtons.forEach(button => {

        button.addEventListener("click", () => {

            button.classList.toggle("selected");

            console.log("Odd selected");

        });

    });

});