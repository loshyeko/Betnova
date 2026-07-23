def generate_match_result(home_odds, draw_odds, away_odds):
    return [
        ("Match Result", "Home", home_odds),
        ("Match Result", "Draw", draw_odds),
        ("Match Result", "Away", away_odds),
    ]


def generate_double_chance(home_odds, draw_odds, away_odds):
    return [
        ("Double Chance", "1X", round((home_odds + draw_odds) / 2.2, 2)),
        ("Double Chance", "12", round((home_odds + away_odds) / 2.2, 2)),
        ("Double Chance", "X2", round((draw_odds + away_odds) / 2.2, 2)),
    ]


def generate_draw_no_bet(home_odds, away_odds):
    return [
        ("Draw No Bet", "Home", round(home_odds * 0.78, 2)),
        ("Draw No Bet", "Away", round(away_odds * 0.78, 2)),

   ]



def generate_correct_score(home_odds, draw_odds, away_odds):
    home_factor = float(home_odds)
    draw_factor = float(draw_odds)
    away_factor = float(away_odds)

    return [
        ("Correct Score", "0-0", round(draw_factor * 4.5, 2)),
        ("Correct Score", "1-0", round(home_factor * 2.9, 2)),
        ("Correct Score", "2-0", round(home_factor * 3.8, 2)),
        ("Correct Score", "2-1", round(home_factor * 3.4, 2)),
        ("Correct Score", "3-0", round(home_factor * 6.5, 2)),
        ("Correct Score", "3-1", round(home_factor * 5.5, 2)),
        ("Correct Score", "3-2", round(home_factor * 8.5, 2)),

        ("Correct Score", "1-1", round(draw_factor * 3.4, 2)),
        ("Correct Score", "2-2", round(draw_factor * 6.8, 2)),
        ("Correct Score", "3-3", round(draw_factor * 18.0, 2)),

        ("Correct Score", "0-1", round(away_factor * 2.9, 2)),
        ("Correct Score", "0-2", round(away_factor * 4.2, 2)),
        ("Correct Score", "1-2", round(away_factor * 3.6, 2)),
        ("Correct Score", "0-3", round(away_factor * 7.2, 2)),
        ("Correct Score", "1-3", round(away_factor * 6.1, 2)),
        ("Correct Score", "2-3", round(away_factor * 8.9, 2)),

        ("correct score", "Any other Home Win", round(home_factor*7.5,2)),
        ("Correct Score", "Any Other Away Win", round(away_factor * 8.5, 2)),
        ("Correct Score", "Any Other Draw", round(draw_factor * 10.0, 2)),
    ]


def generate_btts(home_odds, away_odds):
    return [
        ("Both Teams To Score", "Yes", round((home_odds + away_odds) / 2.8, 2)),
        ("Both Teams To Score", "No", round((home_odds + away_odds) / 2.6, 2)),
    ]


def generate_over_under():
    return [
        ("Over/Under Goals", "Over 0.5", 1.08),
        ("Over/Under Goals", "Under 0.5", 8.50),

        ("Over/Under Goals", "Over 1.5", 1.28),
        ("Over/Under Goals", "Under 1.5", 3.60),

        ("Over/Under Goals", "Over 2.5", 1.90),
        ("Over/Under Goals", "Under 2.5", 1.90),

        ("Over/Under Goals", "Over 3.5", 3.20),
        ("Over/Under Goals", "Under 3.5", 1.35),

        ("Over/Under Goals", "Over 4.5", 5.50),
        ("Over/Under Goals", "Under 4.5", 1.15),
    ]


def generate_odd_even():
    return [
        ("Odd/Even Goals", "Odd", 1.92),
        ("Odd/Even Goals", "Even", 1.92),
    ]


def generate_first_half(home_odds, draw_odds, away_odds):
    return [
        ("First Half Result", "Home", round(home_odds * 1.25, 2)),
        ("First Half Result", "Draw", round(draw_odds * 1.10, 2)),
        ("First Half Result", "Away", round(away_odds * 1.25, 2)),
    ]


def generate_second_half(home_odds, draw_odds, away_odds):
    return [
        ("Second Half Result", "Home", round(home_odds * 1.20, 2)),
        ("Second Half Result", "Draw", round(draw_odds * 1.08, 2)),
        ("Second Half Result", "Away", round(away_odds * 1.20, 2)),
    ]













