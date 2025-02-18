import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import seaborn.objects as so
import io
from database import load_allData
from datetime import datetime

employees,desks,booking,department = load_allData()


# graph for employer
def daily_desk_utilization():
    current_year = datetime.now().year
    current_month = datetime.now().month
    res = booking.copy()
    total_desks = desks[desks['deskID'].str.startswith('D')].shape[0]
    res.set_index(pd.to_datetime(res['date']),inplace=True)
    res.sort_index(inplace=True)
    res = res.loc[(res.index.year == current_year) & (res.index.month == current_month)]

    # Resample daily and calculate desk utilization percentage
    res['Utilization (%)'] = (res.resample("D").size() / total_desks) * 100

    # Plotting
    fig, ax = plt.subplots()
    sns.lineplot(x=res.index, y='Utilization (%)', data=res, marker='o', ax=ax,palette='Set3',hue=res.index)
    ax.set_title('Daily Desk Utilization')
    ax.set_xlabel('Date')
    ax.set_ylabel('Utilization (%)')
    ax.set_ylim(0, 100)
    ax.tick_params(axis='x', labelsize=6) 
    plt.xticks(rotation = 90)
    

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    fig.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return img

def department_booking_distribution():
    current_year = datetime.now().year
    current_month = datetime.now().month
    employee_df = employees.copy()
    department_df = department.copy()

    res = booking.copy()
    res.set_index(pd.to_datetime(res['date']),inplace=True)
    res.sort_index(inplace=True)
    res = res.loc[(res.index.year == current_year) & (res.index.month == current_month)]
    employee_with_dept = pd.merge(employee_df, department_df, on='departmentID', how='left')
    res = pd.merge(res, employee_with_dept[['employeeID', 'departmentName']], on='employeeID', how='left')
    res['Frequency'] = res.groupby('departmentName')['departmentName'].transform('size')

    # Plotting
    max_value = res['Frequency'].max()
    fig, ax = plt.subplots()
    sns.barplot(x=res['departmentName'], y=res['Frequency'], ax=ax ,palette='YlGnBu',hue=res['departmentName'])  
    ax.set_title('Department-Wise Booking Distribution')
    ax.set_xlabel('Department')
    ax.set_ylabel('Usage of Desks and Meeting Room')
    ax.set_ylim(0, 100)
    ax.tick_params(axis='x', labelsize=8) 
    ax.set_ylim(0, max_value + 5)
    plt.xticks(rotation = 90)
    

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    fig.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return img

def employees_attendance_trend():
    # Get current year and current month (e.g. if current month is Feb, show Jan-Feb)
    current_year = datetime.now().year


    # Copy booking data and ensure 'date' column is datetime
    res = booking.copy()
    res['date'] = pd.to_datetime(res['date'])
    # Filter for the current year
    res = res[res['date'].dt.year == current_year]

    # Resample the data by month using the valid alias 'M' (month end)
    monthly_counts = res.resample('ME', on='date').size().reset_index()
    monthly_counts.columns = ['month', 'bookings']
    plot = (
        so.Plot(monthly_counts, x='month', y='bookings')
        .add(so.Area(alpha=0.7), so.Stack())
        .label(title="Employee Attendance Trend",
            x="Month",
            y="Number of Bookings")
        
    )
    img = io.BytesIO()
    plt.xticks(rotation=90)  # Rotate x-axis labels by 90 degrees
    plot.save(img, format='png')
    img.seek(0)
    return img









# graph for employee