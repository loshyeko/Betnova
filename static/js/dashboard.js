document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".odd").forEach(button => {

        button.addEventListener("click", function () {

            this.classList.toggle("selected");

            console.log("Selected:", this.innerText);

        });

    });

});