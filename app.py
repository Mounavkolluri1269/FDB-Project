from flask import Flask, render_template, request, redirect, session, url_for, flash
from db import get_connection
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Events WHERE Date >= CURDATE() ORDER BY Date ASC")
    events = cursor.fetchall()
    conn.close()
    return render_template('events.html', events=events, role=session.get('role'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Users (Name, Email, Password) VALUES (%s, %s, %s)", (name, email, password))
            conn.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect('/login')
        except:
            flash('Email already exists.', 'danger')
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = None  # Define user early

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE Email=%s AND Password=%s", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['UserID']
            session['role'] = user['Role']
            session['name'] = user['Name']
            flash('Login Successful!', 'success')
            return redirect('/home')  # Redirect to Home Page
        else:
            flash("Invalid credentials", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/checkin/<int:event_id>', methods=['GET', 'POST'])
def checkin(event_id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        location = request.form['location']
        preferred_date = request.form['preferred_date']
        guests = request.form['guests']

        # Save all to session temporarily
        session['checkin_data'] = {
            'event_id': event_id,
            'name': name,
            'email': email,
            'contact': contact,
            'location': location,
            'preferred_date': preferred_date,
            'guests': guests
        }

        return redirect('/summary')  # Redirect to confirmation summary

    return render_template('checkin.html', event_id=event_id)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if 'checkin_data' not in session:
        return redirect('/')

    checkin_data = session['checkin_data']

    if request.method == 'POST':
        # Save into Checkins table
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
    INSERT INTO Checkins (UserID, EventID, Guests, PreferredLocation, PreferredDate)
    VALUES (%s, %s, %s, %s, %s)
""", (
    session['user_id'],
    checkin_data['event_id'],
    checkin_data['guests'],
    checkin_data['location'],
    checkin_data['preferred_date']
))

        conn.commit()
        checkin_id = cursor.lastrowid
        conn.close()

        # After saving, clear session
        session.pop('checkin_data', None)

        return redirect(f'/payment/{checkin_id}')  # Proceed to Payment page

    return render_template('summary.html', checkin_data=checkin_data)


@app.route('/payment/<int:checkin_id>', methods=['GET', 'POST'])
def payment(checkin_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT C.Guests, E.Price, E.Title
        FROM Checkins C
        JOIN Events E ON C.EventID = E.EventID
        WHERE C.CheckinID = %s
    """, (checkin_id,))
    data = cursor.fetchone()

    total_amount = data['Guests'] * data['Price']

    if request.method == 'POST':
        method = request.form['method']
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Payments (CheckinID, Amount, Method) VALUES (%s, %s, %s)", (checkin_id, total_amount, method))
        conn.commit()
        conn.close()
        flash('Payment successful!', 'success')
        return redirect('/my_bookings')

    conn.close()
    return render_template('payment.html', checkin_id=checkin_id, total=total_amount, title=data['Title'])

@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT C.CheckinID, E.Title, E.Location, E.Date, C.Guests, P.Amount, P.Method, P.PaymentDate
        FROM Checkins C
        JOIN Events E ON C.EventID = E.EventID
        LEFT JOIN Payments P ON P.CheckinID = C.CheckinID
        WHERE C.UserID = %s
        ORDER BY C.CheckinTime DESC
    """, (session['user_id'],))
    bookings = cursor.fetchall()
    conn.close()
    return render_template('user_bookings.html', bookings=bookings)

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Access Denied", 403

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT U.Name AS UserName, E.EventID, E.Title, SUM(P.Amount) AS TotalPaid
        FROM Payments P
        JOIN Checkins C ON P.CheckinID = C.CheckinID
        JOIN Users U ON C.UserID = U.UserID
        JOIN Events E ON C.EventID = E.EventID
        GROUP BY U.UserID, E.EventID, E.Title
    """)
    summary = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', summary=summary)


@app.route('/credit_card_payment/<int:checkin_id>', methods=['GET', 'POST'])
def credit_card_payment(checkin_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT C.Guests, E.Price, E.Title
        FROM Checkins C
        JOIN Events E ON C.EventID = E.EventID
        WHERE C.CheckinID = %s
    """, (checkin_id,))
    data = cursor.fetchone()

    total_amount = data['Guests'] * data['Price']

    if request.method == 'POST':
        # Simulate successful credit card payment
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Payments (CheckinID, Amount, Method) VALUES (%s, %s, %s)",
                       (checkin_id, total_amount, 'credit_card'))
        conn.commit()
        conn.close()
        flash('Credit Card payment successful!', 'success')
        return redirect('/my_bookings')

    conn.close()
    return render_template('credit_card_payment.html', checkin_id=checkin_id, title=data['Title'], total=total_amount)
@app.route('/debit_card_payment/<int:checkin_id>', methods=['GET', 'POST'])
def debit_card_payment(checkin_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT C.Guests, E.Price, E.Title
        FROM Checkins C
        JOIN Events E ON C.EventID = E.EventID
        WHERE C.CheckinID = %s
    """, (checkin_id,))
    data = cursor.fetchone()

    total_amount = data['Guests'] * data['Price']

    if request.method == 'POST':
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Payments (CheckinID, Amount, Method) VALUES (%s, %s, %s)",
                       (checkin_id, total_amount, 'debit_card'))
        conn.commit()
        conn.close()
        flash('Debit Card payment successful!', 'success')
        return redirect('/my_bookings')

    conn.close()
    return render_template('debit_card_payment.html', checkin_id=checkin_id, title=data['Title'], total=total_amount)

@app.route('/admin/add_event', methods=['GET', 'POST'])
def add_event():
    if session.get('role') != 'admin':
        return "Access Denied", 403

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        date = request.form['date']
        price = request.form['price']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Events (Title, Description, Location, Date, Price)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, description, location, date, price))
        conn.commit()
        conn.close()

        flash('Event added successfully!', 'success')
        return redirect('/admin')

    return render_template('add_event.html')

# Route to show delete confirmation page
@app.route('/admin/delete_event_direct/<int:event_id>')
def delete_event_direct(event_id):
    if session.get('role') != 'admin':
        return "Access Denied", 403

    conn = get_connection()
    cursor = conn.cursor()

    # Delete Payments first
    cursor.execute("""
        DELETE P FROM Payments P
        JOIN Checkins C ON P.CheckinID = C.CheckinID
        WHERE C.EventID = %s
    """, (event_id,))
    
    # Delete Checkins
    cursor.execute("DELETE FROM Checkins WHERE EventID = %s", (event_id,))
    
    # Delete Event
    cursor.execute("DELETE FROM Events WHERE EventID = %s", (event_id,))
    
    conn.commit()
    conn.close()

    flash('Event deleted successfully!', 'success')
    return redirect('/admin')

@app.route('/admin/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if session.get('role') != 'admin':
        return "Access Denied", 403
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        new_price = request.form['price']
        cursor.execute("UPDATE Events SET Price = %s WHERE EventID = %s", (new_price, event_id))
        conn.commit()
        conn.close()
        flash('Price updated successfully!', 'success')
        return redirect('/admin')

    cursor.execute("SELECT * FROM Events WHERE EventID = %s", (event_id,))
    event = cursor.fetchone()
    conn.close()

    if event:
        return render_template('edit_event.html', event=event)
    else:
        flash('Event not found.', 'danger')
        return redirect('/admin')

@app.route('/events')
def events():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Events WHERE Date >= CURDATE() ORDER BY Date ASC")
    events = cursor.fetchall()
    conn.close()
    return render_template('events.html', events=events)
@app.route('/home')
def home_page():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
