from flask import Flask, render_template
from datetime import datetime

# Assume 'mydb' is already connected to your database

app = Flask(__name__)


@app.route('/print', methods=['GET'])
def get_data():
    flash('Hello')
    conn1 = mydb.cursor(dictionary=True)
    conn1.execute(
        "SELECT departure, arrival, departure_time, arrival_time, arrival_date, departure_date FROM travel_details "
        "GROUP BY departure, arrival, departure_time, arrival_time, arrival_date, departure_date")
    result = conn1.fetchall()

    gap_days = []
    for i in range(len(result) - 1):
        current_arrival = result[i]['arrival_date']
        next_departure = result[i + 1]['departure_date']

        if current_arrival and next_departure:
            difference = (next_departure - current_arrival).days
            gap_days.append(difference)
            print(f"Gap between entry {i} arrival and entry {i + 1} departure: {difference} days")
        else:
            print(f"Missing date in entry {i} or entry {i + 1}")

    print(gap_days)

    da = []
    even_days = []
    odd_days = []
    for j in range(len(gap_days)):
        if j % 2 == 0:
            even_days.append(gap_days[j])
            da.append(gap_days[j] * 100)
        else:
            odd_days.append(gap_days[j])

    # Aligning even_days and da with the length of travel_data
    aligned_even_days = even_days + [None] * (len(result) - len(even_days))
    aligned_da = da + [None] * (len(result) - len(da))

    return render_template('print.html', travel_data=result, da=aligned_da, even_days=aligned_even_days)


if __name__ == '_main_':
    app.run(debug=True)