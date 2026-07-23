document.addEventListener("DOMContentLoaded", () => {

    const btn = document.getElementById("generateOdds");

    if (!btn) return;

    btn.addEventListener("click", () => {

        const home = parseFloat(document.getElementById("home_odds").value);
        const draw = parseFloat(document.getElementById("draw_odds").value);
        const away = parseFloat(document.getElementById("away_odds").value);

        if (isNaN(home) ||  isNaN(draw) ||  isNaN(away)) {
            alert("Enter Home, Draw and Away odds first.");
            return;
        }

        const p = OddsEngine.probabilities(home, draw, away);

        const dc = OddsEngine.doubleChance(p);
        const dnb = OddsEngine.drawNoBet(p);
        const btts = OddsEngine.bothTeamsToScore(p);
        const ou = OddsEngine.overUnder(p);
        const cs = OddsEngine.correctScore();
        const fg = OddsEngine.firstGoal(p);
        const oe = OddsEngine.oddEven();
        const htft = OddsEngine.halfTimeFullTime();

        document.querySelectorAll('input[type="number"]').forEach(input => {

            if (input.id === "home_odds" ||
                input.id === "draw_odds" ||
                input.id === "away_odds") {
                return;
            }

            const selection = input.dataset.selection;

            if (!selection) return;

            if (dc[selection] !== undefined) {
                input.value = dc[selection];
                return;
            }

            if (dnb[selection] !== undefined) {
                input.value = dnb[selection];
                return;
            }

            if (btts[selection] !== undefined) {
                input.value = btts[selection];
                return;
            }

            if (ou[selection] !== undefined) {
                input.value = ou[selection];
                return;
            }

            if (cs[selection] !== undefined) {
                input.value = cs[selection];
            }

            if (fg[selection] !== undefined) {
                input.value = fg[selection];
            }

            if (oe[selection] !== undefined) {
                input.value = oe[selection];
            }

            if (htft[selection] !== undefined) {
                input.value = htft[selection];
            }

        });

    });

});
