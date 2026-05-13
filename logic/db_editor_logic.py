import database as database

def save_record(category, is_new, row_id, vals):
    """Uniwersalny przełącznik zapisu dla wszystkich tabel cennika."""
    conn = database.get_connection()
    cursor = conn.cursor()
    
    try:
        if category == "Narzędzia":
            if is_new:
                cursor.execute('''INSERT INTO pricelist_tools 
                    (category, tool_type, blades, diam_min, diam_max, price_1, price_2_4, price_5_10, price_11_20) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', vals)
            else:
                cursor.execute('''UPDATE pricelist_tools SET 
                    category=?, tool_type=?, blades=?, diam_min=?, diam_max=?, 
                    price_1=?, price_2_4=?, price_5_10=?, price_11_20=? WHERE id=?''', (*vals, row_id))
        
        elif category == "Powłoki":
            if is_new:
                cursor.execute('INSERT INTO pricelist_coatings (coating_name, diam_max, length, price) VALUES (?, ?, ?, ?)', vals)
            else:
                cursor.execute('UPDATE pricelist_coatings SET coating_name=?, diam_max=?, length=?, price=? WHERE id=?', (*vals, row_id))
        
        elif category == "Usługi":
            if is_new:
                cursor.execute('INSERT INTO pricelist_services (service_name, param_min, param_max, price) VALUES (?, ?, ?, ?)', vals)
            else:
                cursor.execute('UPDATE pricelist_services SET service_name=?, param_min=?, param_max=?, price=? WHERE id=?', (*vals, row_id))
        
        conn.commit()
    finally:
        conn.close()

def delete_record(category, row_id):
    """Usuwa rekord z odpowiedniej tabeli."""
    table = "pricelist_tools" if category == "Narzędzia" else "pricelist_coatings" if category == "Powłoki" else "pricelist_services"
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))
    conn.commit()
    conn.close()