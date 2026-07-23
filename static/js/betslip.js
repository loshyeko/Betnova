

const betItems = document.getElementById("bet-items");
const totalOddsEl = document.getElementById("total-odds");
const potentialWinEl = document.getElementById("potential-win");
const stakeInput = document.getElementById("stake");
const selectionCount = document.getElementById("selection-count");

let bets = JSON.parse(localStorage.getItem("betslip")) || [];

function updateBetCount() {
    const counter = document.getElementById("bet-count");
    if (counter) {
        counter.textContent = bets.length;
    }
}

function addToBet(matchId, matchName, market, selection, odds) {

    // Remove previous selection from the same match
    bets = bets.filter(bet => bet.matchId != matchId);

    // Add new selection
    bets.push({
        matchId: matchId,
        matchName: matchName,
        market: market,
        selection: selection,
        odds: Number(odds)
    });

    // Save
    localStorage.setItem("betslip", JSON.stringify(bets));

updateBetCount();
renderBets();
}
function renderBets() {

    if (!betItems) return;

    betItems.innerHTML = "";

    if (bets.length === 0) {
        betItems.innerHTML = "<div class='bet-card'><p style='text-align:center;'>No selections yet.</p></div>";

        if (selectionCount) selectionCount.textContent = "0";
        if (totalOddsEl) totalOddsEl.textContent = "0.00";
        if (potentialWinEl) potentialWinEl.textContent = "0.00";
        return;
    }

    let totalOdds = 1;

    bets.forEach((bet, index) => {

        totalOdds *= Number(bet.odds);
        betItems.innerHTML += "<div class='bet-card'><div class='bet-match'>" + bet.matchName + "</div><div class='bet-selection'><span>" + bet.market + " - " + bet.selection + "</span><span class='bet-odds'>" + Number(bet.odds).toFixed(2) + "</span></div><button class='remove-btn' onclick='removeBet(" + index + ")'>Remove</button></div>";
    });

    if (selectionCount) selectionCount.textContent = bets.length;
    if (totalOddsEl) totalOddsEl.textContent = totalOdds.toFixed(2);

calculateWin();
}
function calculateWin() {

    if (!stakeInput || !totalOddsEl || !potentialWinEl) return;

    const stake = Number(stakeInput.value) || 0;
    const odds = Number(totalOddsEl.textContent) || 0;

    potentialWinEl.textContent = (stake * odds).toFixed(2);
}

function removeBet(index) {

    bets.splice(index, 1);

    localStorage.setItem("betslip", JSON.stringify(bets));

    updateBetCount();
    renderBets();
}

if (stakeInput) {
    stakeInput.addEventListener("input", calculateWin);
}

// Make functions available globally
window.addToBet = addToBet;
window.removeBet = removeBet;

// Initial page load
updateBetCount();
renderBets();

const placeBetBtn = document.getElementById("place-bet-btn");

if (placeBetBtn) {
    placeBetBtn.addEventListener("click", placeBet);
}

async function placeBet() {
    if (bets.length === 0) {
        alert("Please select at least one match.");
        return;
    }

    const stake = Number(stakeInput.value);

    if (!stake || stake <= 0) {
        alert("Enter a valid stake.");
        return;
    }

    const bet = bets[0];

    const response = await fetch("/place_bet", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            match_id: bet.matchId,
            selection: bet.selection,
            odds: bet.odds,
            stake: stake,
            potential_win: stake * Number(totalOddsEl.textContent)
        })
    });

    const result = await response.json();

    alert(result.message);

    if (result.success) {
        bets = [];
        localStorage.removeItem("betslip");
        renderBets();
        updateBetCount();
    }
}
