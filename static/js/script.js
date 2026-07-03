let selections = JSON.parse(localStorage.getItem("betslip")) || [];

function formatMoney(amount) {
    amount = Number(amount);

    if (isNaN(amount)) {
        amount = 0;
    }

    return amount.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function saveBetSlip() {
    localStorage.setItem("betslip", JSON.stringify(selections));
}

function addToBet(matchId, matchName, market, selection, odds) {

    // Remove any existing selection for this match
    selections = selections.filter(item => item.matchId != matchId);

    // Add the new selection
    selections.push({
        matchId: matchId,
        matchName: matchName,
        market: market,
        selection: selection,
        odds: parseFloat(odds)
    });

    // Save to localStorage
    localStorage.setItem("betslip", JSON.stringify(selections));

    // Refresh the UI
    updateBetCount();
    updateBetSlip();
}

function updateBetSlip() {

    const betItems = document.getElementById("bet-items");

    if (!betItems) {
        return;
    }

    const totalOdds = document.getElementById("total-odds");
    const potentialWin = document.getElementById("potential-win");
    const stakeInput = document.getElementById("stake");

    betItems.innerHTML = "";

    if (selections.length === 0) {

        betItems.innerHTML =
            '<p class="empty-slip">No selections yet.</p>';

        if (totalOdds)
            totalOdds.textContent = "1.00";

        if (potentialWin)
            potentialWin.textContent = currency + " 0.00";

        return;
    }

    let total = 1;

    selections.forEach(function(item, index) {

        total *= item.odds;

        betItems.innerHTML +=
            '<div class="bet-item">' +
            '<strong>' + item.matchName + '</strong><br>' +
            '<small>' + item.market + '</small><br>' +
            item.selection + ' @ ' + (item.odds || 0).toFixed(2) +
            '<br><button class="remove-btn" onclick="removeSelection(' + index + ')">Remove</button>' +
            '</div>';

    });

    if (totalOdds)
        totalOdds.textContent = formatMoney(total);

    const stake = stakeInput ? parseFloat(stakeInput.value) || 0 : 0;

    const bonusElement = document.getElementById("win-bonus");
const payoutElement = document.getElementById("payout");

const potential = stake * total;

// Bonus rules
let bonusPercent = 0;

if (selections.length >= 10) {
    bonusPercent = 20;
} else if (selections.length >= 5) {
    bonusPercent = 10;
} else if (selections.length >= 3) {
    bonusPercent = 5;
} else if (selections.length >= 2) {
    bonusPercent = 2;
}

const bonus = potential * (bonusPercent / 100);
const payout = potential + bonus;

if (potentialWin)
    potentialWin.textContent = formatMoney(potential);

if (bonusElement)
    bonusElement.textContent = formatMoney(bonus);

if (payoutElement)
    payoutElement.textContent = formatMoney(payout);

}

function removeSelection(index) {

    selections.splice(index, 1);

    localStorage.setItem("betslip", JSON.stringify(selections));

    updateBetCount();

    updateBetSlip();

}
    

const eyeButton = document.getElementById("toggle-balance");
const balanceText = document.getElementById("balance");

if (eyeButton && balanceText) {

    const originalBalance = balanceText.innerHTML;
    let hidden = false;

    eyeButton.addEventListener("click", function () {

        if (hidden) {

            balanceText.innerHTML = originalBalance;
            eyeButton.innerHTML = '<i class="fa-solid fa-eye"></i>';

        } else {

            balanceText.innerHTML = "••••••••";
            eyeButton.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';

        }

        hidden = !hidden;

    });

}

function updateBetCount() {

    selections = JSON.parse(localStorage.getItem("betslip")) || [];

    const badge = document.getElementById("bet-count");

    if (badge) {
        badge.textContent = selections.length;

        if (selections.length > 0) {
            badge.style.display = "inline-block";
        } else {
            badge.style.display = "none";
        }
    }

}

function clearBetSlip() {

    selections = [];

    localStorage.removeItem("betslip");

    updateBetCount();

    updateBetSlip();

}

function changeLanguage(lang) {
    localStorage.setItem("language", lang);
    location.reload();
}

document.addEventListener("DOMContentLoaded", function () {
    const lang = localStorage.getItem("language") || "en";

    const selector = document.getElementById("language");
    if (selector) {
        selector.value = lang;
    }

});

document.addEventListener("DOMContentLoaded", function () {

    selections = JSON.parse(localStorage.getItem("betslip")) || [];

    updateBetCount();

    updateBetSlip();

    const stakeInput = document.getElementById("stake");

    if (stakeInput) {
        stakeInput.addEventListener("input", updateBetSlip);
    }

});

const placeBetBtn = document.getElementById("place-bet-btn");

if (placeBetBtn) {

    placeBetBtn.addEventListener("click", async function () {

        selections = JSON.parse(localStorage.getItem("betslip")) || [];

        if (selections.length === 0) {
            alert("Please add at least one selection.");
            return;
        }

        const stake = parseFloat(document.getElementById("stake").value);

        if (isNaN(stake) || stake <= 0) {
            alert("Please enter a valid stake.");
            return;
        }

        const totalOdds = selections.reduce((t, s) => t * s.odds, 1);
        const potentialWin = stake * totalOdds;

        const response = await fetch("/place_bet", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                match_id: selections[0].matchId,
                selection: selections[0].selection,
                odds: selections[0].odds,
                stake: stake,
                potential_win: potentialWin
            })
        });

        const result = await response.json();

        if (!result.success) {
            alert(result.message);
            return;
        }

        alert(result.message);

        const balance = document.getElementById("balance");
        if (balance) {
            balance.textContent = currency + " " + formatMoney(result.balance);
        }

        selections = [];
        localStorage.removeItem("betslip");

        updateBetCount();
        updateBetSlip();

        document.getElementById("stake").value = "";

    });

}

function filterSport(sport) {
    window.location.href = "/matches?sport=" + encodeURIComponent(sport);
}

function filterLeague(league) {
    window.location.href = "/matches?league=" + encodeURIComponent(league);
}

function updatePrefix() {

    const country = document.getElementById("country");
    const prefix = document.getElementById("prefix");

    if (!country || !prefix) return;

    prefix.value = country.value;
}

document.addEventListener("DOMContentLoaded", function () {
    updatePrefix();
});

const lang = localStorage.getItem("language") || "en";
const t = translations[lang];

if (document.getElementById("sports-text"))
    document.getElementById("sports-text").textContent = t.sports;

if (document.getElementById("betslip-text"))
    document.getElementById("betslip-text").textContent = t.betslip;

if (document.getElementById("account-text"))
    document.getElementById("account-text").textContent = t.account;

