import time
from multiprocessing import Semaphore

from flask import Flask, render_template, request

app = Flask(__name__)

mutex = Semaphore(1)
write = Semaphore(1)
details_sem = Semaphore(1)
rc = 0
available_seats = 50
booking_counter = 1
bookings = {}


def book_ticket(passenger_name, seat_count):
    global available_seats, booking_counter
    with write:
        if seat_count <= available_seats:
            booking_id = booking_counter
            booking_counter += 1
            available_seats -= seat_count
            bookings[booking_id] = {'passenger_name': passenger_name, 'seat_count': seat_count}
            return booking_id
        else:
            return None






def cancel_ticket(booking_id):
    global available_seats
    with write:
        if booking_id in bookings:
            seat_count = bookings[booking_id]['seat_count']
            available_seats += seat_count
            del bookings[booking_id]
            return True
        else:
            return False


def check_details():
    # Simulate checking details
    global rc
    time.sleep(2)
    with mutex:
        # Acquire mutex before reading
        rc += 1
        if rc == 1:
            details_sem.acquire()

    try:

        return render_template('flight_details.html', available_seats=available_seats)
    finally:
        with mutex:
            rc -= 1
            if rc == 0:
                details_sem.release()  # Release for writers


def run_flask_app():
    app.run(debug=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        passenger_name = request.form.get('passenger_name')
        seat_count = int(request.form.get('seat_count'))

        booking_id = book_ticket(passenger_name, seat_count)

        if booking_id is not None:
            message = f"Booking successful! Booking ID: {booking_id}"
        else:
            message = "Not enough seats available."

        return render_template('book_ticket.html', message=message)

    return render_template('book_ticket.html')


# ... (your existing code)



@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    if request.method == 'POST':
        booking_id = int(request.form.get('booking_id'))

        if cancel_ticket(booking_id):
            message = f"Ticket with Booking ID {booking_id} canceled successfully."
        else:
            message = f"Ticket with Booking ID {booking_id} not found."

        return render_template('cancel_ticket.html', message=message)

    return render_template('cancel_ticket.html')


@app.route('/details')
def flight_details():
    global rc
    with mutex:
        rc += 1
        if rc == 1:
            details_sem.acquire()

    try:
        check_details()
        return render_template('flight_details.html', available_seats=available_seats)
    finally:
        with mutex:
            rc -= 1
            if rc == 0:
                details_sem.release()


if __name__ == '__main__':
    # Run the Flask app in a separate process
    app.run(debug=True)
