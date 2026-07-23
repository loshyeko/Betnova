const OddsEngine = {

    round(value) {
        return Math.max(1.01, Number(value.toFixed(2)));
    },

    probabilities(home, draw, away) {
        const pHome = 1 / home;
        const pDraw = 1 / draw;
        const pAway = 1 / away;

        const total = pHome + pDraw + pAway;

        return {
            home: pHome / total,
            draw: pDraw / total,
            away: pAway / total
        };
    },

    doubleChance(p) {
        return {
            "Home/Draw": this.round(1 / (p.home + p.draw)),
            "Home/Away": this.round(1 / (p.home + p.away)),
            "Draw/Away": this.round(1 / (p.draw + p.away))
        };
    },

    drawNoBet(p) {
        return {
            "Home": this.round(1 / (p.home / (p.home + p.away))),
            "Away": this.round(1 / (p.away / (p.home + p.away)))
        };
    },

    bothTeamsToScore(p) {
        return {
            "Yes": 1.85,
            "No": 1.95
        };
    },

    overUnder(p) {
        return {
            "Over 0.5": 1.05,
            "Under 0.5": 10.00,

            "Over 1.5": 1.30,
            "Under 1.5": 3.50,

            "Over 2.5": 1.90,
            "Under 2.5": 1.90,

            "Over 3.5": 3.20,
            "Under 3.5": 1.35,

            "Over 4.5": 6.50,
            "Under 4.5": 1.10
        };
    },

    correctScore() {
        return {
            "0-0": 8.00,
            "1-0": 7.50,
            "2-0": 9.00,
            "2-1": 8.50,
            "3-0": 15.00,
            "3-1": 16.00,
            "1-1": 6.50,
            "2-2": 13.00,
            "3-3": 50.00,
            "0-1": 7.50,
            "0-2": 9.00,
            "1-2": 8.50,
            "0-3": 15.00,
            "1-3": 16.00,
            "Any Other Home Win": 40.00,
            "Any Other Draw": 80.00,
            "Any Other Away Win": 45.00
        };
    },

    firstGoal(p) {
        return {
            "Home": this.round(1 / p.home),
            "Away": this.round(1 / p.away),
            "No Goal": 15.00
        };
    },

    oddEven() {
        return {
            "Odd": 1.95,
            "Even": 1.95
        };
    },

    halfTimeFullTime() {
        return {
            "Home/Home": 3.20,
            "Home/Draw": 18.00,
            "Home/Away": 45.00,

            "Draw/Home": 5.00,
            "Draw/Draw": 4.50,
            "Draw/Away": 6.00,

            "Away/Home": 45.00,
            "Away/Draw": 18.00,
            "Away/Away": 3.20
        };
    }

};


