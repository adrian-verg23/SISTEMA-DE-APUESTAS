import random
from datetime import datetime, timedelta
import psycopg
from faker import Faker

# Inicializar Faker en español
fake = Faker('es_ES')

# Configuración de conexión
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "gestion_apuestas",
    "user": "postgres",
    "password": "workbench333"
}

def generar_datos():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Conexión establecida con éxito a gestion_apuestas.")

        # ==========================================
        # 1. USERS (1000)
        # ==========================================
        print("Generando usuarios...")
        users_data = []
        emails_used = set()
        for _ in range(1000):
            fn = fake.first_name()
            ln = fake.last_name()
            email = fake.unique.email()
            phone = fake.phone_number()[:20]
            dob = fake.date_of_birth(minimum_age=18, maximum_age=75)
            kyc = random.choices(['Pending', 'Verified', 'Rejected'], weights=[20, 75, 5])[0]
            balance = round(random.uniform(0.0, 5000.0), 2)
            users_data.append((fn, ln, email, phone, dob, kyc, balance))

        cursor.executemany("""
            INSERT INTO users (first_name, last_name, email, phone_number, date_of_birth, kyc_status, account_balance)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, users_data)
        
        cursor.execute("SELECT id_user FROM users ORDER BY id_user;")
        user_ids = [row[0] for row in cursor.fetchall()]

        # ==========================================
        # 2. TEAMS (120)
        # ==========================================
        print("Generando equipos...")
        teams_data = []
        team_names = set()
        while len(team_names) < 120:
            name = f"{fake.city()} {random.choice(['FC', 'Club', 'United', 'Real', 'Atlético', 'BC', 'TC', 'Gamers', 'E-Sports'])}"
            team_names.add(name)

        teams_data = [(name,) for name in team_names]
        cursor.executemany("INSERT INTO teams (name) VALUES (%s)", teams_data)

        cursor.execute("SELECT id_team FROM teams ORDER BY id_team;")
        team_ids = [row[0] for row in cursor.fetchall()]

        # ==========================================
        # 3. LEAGUES (20)
        # ==========================================
        print("Generando ligas...")
        cursor.execute("SELECT id_sport FROM sports;")
        sport_ids = [row[0] for row in cursor.fetchall()]

        leagues_data = []
        league_names = ["Liga Premier", "Copa Nacional", "Serie A", "Liga Profesional", "Torneo de Verano", "Superliga", "Championship"]
        countries = ["Colombia", "España", "Inglaterra", "Argentina", "Brasil", "EE.UU.", "Alemania", "Francia"]

        for i in range(20):
            s_id = random.choice(sport_ids)
            l_name = f"{random.choice(league_names)} {i+1}"
            cntry = random.choice(countries)
            leagues_data.append((s_id, l_name, cntry))

        cursor.executemany("INSERT INTO leagues (id_sport, name, country) VALUES (%s, %s, %s)", leagues_data)

        cursor.execute("SELECT id_league FROM leagues ORDER BY id_league;")
        league_ids = [row[0] for row in cursor.fetchall()]

        # ==========================================
        # 4. TEAM_LEAGUES (240)
        # ==========================================
        print("Asignando equipos a ligas...")
        team_leagues_set = set()
        for l_id in league_ids:
            assigned_teams = random.sample(team_ids, 6)
            for t_id in assigned_teams:
                team_leagues_set.add((t_id, l_id))

        while len(team_leagues_set) < 240:
            team_leagues_set.add((random.choice(team_ids), random.choice(league_ids)))

        cursor.executemany("INSERT INTO team_leagues (id_team, id_league) VALUES (%s, %s)", list(team_leagues_set))

        league_teams_map = {}
        for t_id, l_id in team_leagues_set:
            league_teams_map.setdefault(l_id, []).append(t_id)

        # ==========================================
        # 5. SPORTS_EVENTS (500)
        # ==========================================
        print("Generando eventos deportivos...")
        events_data = []
        statuses = ['Scheduled', 'Live', 'Finished', 'Cancelled']
        status_weights = [30, 10, 55, 5]

        for _ in range(500):
            l_id = random.choice([lid for lid, tlist in league_teams_map.items() if len(tlist) >= 2])
            home_team, away_team = random.sample(league_teams_map[l_id], 2)
            event_date = fake.date_time_between(start_date='-30d', end_date='+30d')
            st = random.choices(statuses, weights=status_weights)[0]

            if st == 'Finished':
                h_score = random.randint(0, 5)
                a_score = random.randint(0, 5)
                winner = 'Home' if h_score > a_score else ('Away' if a_score > h_score else 'Draw')
            elif st == 'Live':
                h_score = random.randint(0, 3)
                a_score = random.randint(0, 3)
                winner = None
            else:
                h_score = None
                a_score = None
                winner = None

            events_data.append((l_id, home_team, away_team, event_date, st, h_score, a_score, winner))

        cursor.executemany("""
            INSERT INTO sports_events (id_league, id_home_team, id_away_team, event_date, status, home_score, away_score, winner)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, events_data)

        cursor.execute("SELECT id_event, id_home_team, id_away_team, status FROM sports_events ORDER BY id_event;")
        events_info = cursor.fetchall()

        # ==========================================
        # 6. MARKETS (1500) & MARKET_SELECTIONS (4000)
        # ==========================================
        print("Generando mercados y selecciones...")
        cursor.execute("SELECT id_market_type FROM market_types;")
        m_type_ids = [row[0] for row in cursor.fetchall()]

        markets_data = []
        market_tuples = set()

        for ev_id, h_team, a_team, ev_st in events_info:
            selected_mtypes = random.sample(m_type_ids, min(len(m_type_ids), random.randint(2, 4)))
            for mt_id in selected_mtypes:
                param = round(random.choice([1.5, 2.5, 3.5]), 2) if mt_id in [3, 4] else None
                m_key = (ev_id, mt_id, param)
                if m_key not in market_tuples:
                    market_tuples.add(m_key)
                    m_status = 'Open' if ev_st in ['Scheduled', 'Live'] else 'Settled'
                    markets_data.append((ev_id, mt_id, param, m_status))
                if len(markets_data) >= 1500:
                    break
            if len(markets_data) >= 1500:
                break

        cursor.executemany("""
            INSERT INTO markets (id_event, id_market_type, market_parameter, status)
            VALUES (%s, %s, %s, %s)
        """, markets_data)

        cursor.execute("SELECT id_market, id_event, id_market_type FROM markets ORDER BY id_market;")
        markets_info = cursor.fetchall()
        events_dict = {e[0]: (e[1], e[2]) for e in events_info}

        selections_data = []
        for m_id, ev_id, mt_id in markets_info:
            h_team, a_team = events_dict[ev_id]
            if mt_id == 1:
                selections_data.extend([(m_id, 'Gana Local', h_team), (m_id, 'Empate', None), (m_id, 'Gana Visitante', a_team)])
            elif mt_id == 2:
                selections_data.extend([(m_id, 'Local o Empate', None), (m_id, 'Visitante o Empate', None), (m_id, 'Local o Visitante', None)])
            elif mt_id in [3, 4]:
                selections_data.extend([(m_id, 'Sí', None), (m_id, 'No', None)])
            else:
                selections_data.extend([(m_id, 'Ambos Anotan - Sí', None), (m_id, 'Ambos Anotan - No', None)])

        cursor.executemany("""
            INSERT INTO market_selections (id_market, selection_label, id_team)
            VALUES (%s, %s, %s)
        """, selections_data)

        cursor.execute("SELECT id_market_selection FROM market_selections ORDER BY id_market_selection;")
        selection_ids = [row[0] for row in cursor.fetchall()]

        # ==========================================
        # 7. ODDS_HISTORY (10000)
        # ==========================================
        print("Generando historial de cuotas...")
        odds_data = []
        now = datetime.now()
        for sel_id in selection_ids:
            for i in range(2):
                odd_val = round(random.uniform(1.10, 8.50), 2)
                dt = now - timedelta(days=random.randint(1, 15), hours=i*3)
                odds_data.append((sel_id, odd_val, dt))

        while len(odds_data) < 10000:
            sel_id = random.choice(selection_ids)
            odd_val = round(random.uniform(1.10, 8.50), 2)
            dt = now - timedelta(days=random.randint(1, 15), minutes=random.randint(1, 5000))
            odds_data.append((sel_id, odd_val, dt))

        unique_odds = {}
        for sel_id, val, dt in odds_data:
            unique_odds[(sel_id, dt)] = val

        odds_data_clean = [(sel_id, val, dt) for (sel_id, dt), val in list(unique_odds.items())[:10000]]

        cursor.executemany("""
            INSERT INTO odds_history (id_market_selection, odd_value, changed_at)
            VALUES (%s, %s, %s)
        """, odds_data_clean)

        cursor.execute("SELECT id_odd, odd_value FROM odds_history ORDER BY id_odd;")
        odds_pool = cursor.fetchall()

        # ==========================================
        # 8. BET_TICKETS (5000) & BET_SELECTIONS (12000)
        # ==========================================
        print("Generando tickets y selecciones de apuestas...")
        tickets_data = []
        bet_selections_data = []

        statuses_ticket = ['Pending', 'Won', 'Lost', 'Cancelled']
        weights_ticket = [30, 40, 25, 5]

        for ticket_id_temp in range(1, 5001):
            u_id = random.choice(user_ids)
            stake = round(random.uniform(2.0, 100.0), 2)
            t_status = random.choices(statuses_ticket, weights=weights_ticket)[0]
            placed = fake.date_time_between(start_date='-10d', end_date='now')

            num_sels = random.randint(1, 4)
            chosen_odds = random.sample(odds_pool, num_sels)

            combined_odd = 1.0
            for o_id, o_val in chosen_odds:
                combined_odd *= float(o_val)

            potential_payout = round(stake * combined_odd, 2)
            tickets_data.append((u_id, stake, potential_payout, t_status, placed))

        cursor.executemany("""
            INSERT INTO bet_tickets (id_user, total_stake, potential_payout, ticket_status, placed_at)
            VALUES (%s, %s, %s, %s, %s)
        """, tickets_data)

        cursor.execute("SELECT id_ticket, ticket_status FROM bet_tickets ORDER BY id_ticket;")
        tickets_info = cursor.fetchall()

        for t_id, t_status in tickets_info:
            num_sels = random.randint(1, 3)
            chosen_odds = random.sample(odds_pool, num_sels)
            for o_id, o_val in chosen_odds:
                if t_status == 'Won':
                    sel_st = 'Won'
                elif t_status == 'Lost':
                    sel_st = random.choice(['Won', 'Lost'])
                elif t_status == 'Cancelled':
                    sel_st = 'Void'
                else:
                    sel_st = 'Pending'
                bet_selections_data.append((t_id, o_id, o_val, sel_st))

        cursor.executemany("""
            INSERT INTO bet_selections (id_ticket, id_odd, odd_value_at_bet, status)
            VALUES (%s, %s, %s, %s)
        """, bet_selections_data)

        # ==========================================
        # 9. FINANCIAL_TRANSACTIONS (6000)
        # ==========================================
        print("Generando transacciones financieras...")
        cursor.execute("SELECT id_payment_method FROM payment_methods;")
        pm_ids = [row[0] for row in cursor.fetchall()]

        transactions_data = []

        won_tickets = [t for t in tickets_info if t[1] == 'Won']
        for t_id, _ in won_tickets:
            cursor.execute("SELECT id_user, potential_payout FROM bet_tickets WHERE id_ticket = %s", (t_id,))
            u_id, payout_amt = cursor.fetchone()
            transactions_data.append((u_id, None, t_id, 'Payout', payout_amt, 'Completed'))

        while len(transactions_data) < 6000:
            u_id = random.choice(user_ids)
            t_type = random.choice(['Deposit', 'Withdrawal', 'Adjustment'])
            pm_id = random.choice(pm_ids) if t_type != 'Adjustment' else None
            amt = round(random.uniform(10.0, 500.0), 2)
            transactions_data.append((u_id, pm_id, None, t_type, amt, 'Completed'))

        cursor.executemany("""
            INSERT INTO financial_transactions (id_user, id_payment_method, id_ticket, transaction_type, amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, transactions_data)

        conn.commit()
        cursor.close()
        conn.close()
        print("\n¡PROCESO COMPLETADO EXITOSAMENTE! Se poblaron todas las tablas en PostgreSQL.")

    except Exception as e:
        print(f"\nERROR durante la ejecución: {e}")

if __name__ == "__main__":
    generar_datos()