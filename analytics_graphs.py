import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import seaborn.objects as so
import io
import threading
from database import load_allData
from current_user_details import get_user_data_df
from datetime import datetime

employees,desks,bookings,department,bookmeeting = load_allData()
bookmeeting.rename(columns={'startTime':'date'},inplace=True)
bookmeeting.drop(columns='endTime',inplace=True)
booking = pd.concat([bookings,bookmeeting],axis=0)



plot_lock = threading.Lock()


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
    with plot_lock:
        sns.set_style('darkgrid')
        fig, ax = plt.subplots()
        sns.lineplot(x=res.index, y='Utilization (%)', data=res, marker='o', ax=ax,palette='icefire',hue=res.index,legend=False)
        ax.set_title(f'Daily Desk Utilization ({current_year}/{current_month})')
        ax.set_xlabel('Date')
        ax.set_ylabel('Utilization (%)')
        ax.set_ylim(0, 100)
        ax.tick_params(axis='x', labelsize=6) 
        plt.xticks(rotation = 90)
        plt.tight_layout()
        

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        fig.savefig(img, format='png')
        plt.close('all')
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

    with plot_lock:
    
        fig, ax = plt.subplots()
        sns.set_style('darkgrid')
        sns.barplot(x=res['departmentName'], y=res['Frequency'], ax=ax ,palette='YlGnBu',hue=res['departmentName'],legend=True)  
        ax.set_title(f'Department-Wise Booking Distribution ({current_year}/{current_month})')
        ax.set_xlabel('Department')
        ax.set_ylabel('Usage of Desks and Meeting Room')
        ax.set_ylim(0, 100)
        ax.tick_params(axis='x', labelsize=8) 
        ax.set_ylim(0, max_value + 5)
        plt.xticks(rotation = 90)
        plt.tight_layout()
        # Save the plot to a BytesIO object
        img = io.BytesIO()
        fig.savefig(img, format='png')
        plt.close('all')
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
    print(monthly_counts)
    with plot_lock:
        sns.set_style('darkgrid')
        plot = (
            so.Plot(monthly_counts, x='month', y='bookings')
            .add(so.Area(alpha=0.7), so.Stack())
            .label(title=f"Employee Attendance Trend ({current_year})",
                x="Month",
                y="Number of Bookings")
        )

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plot.show()  # Display the plot to apply xticks before saving
        plt.xticks(rotation=90)  # Rotate x-axis labels
        plt.tight_layout()
        plt.savefig(img, format='png', bbox_inches='tight')  # Save with adjusted labels
        plt.close('all')
        img.seek(0)
        
    return img

def desk_availability_status():
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    booking_copy = booking.copy()
    booking_copy.set_index(pd.to_datetime(booking_copy['date']),inplace=True)
    booking_copy.sort_index(inplace=True)

    booking_copy = booking_copy.loc[(booking_copy.index.year == current_year) & (booking_copy.index.month == current_month) & (booking_copy.index.day == current_day)]
    occupied = booking_copy.shape[0]
    available = desks.shape[0] - occupied

    # Data for pie chart
    labels = ['Occupied', 'Not Occupied']
    sizes = [occupied, available]
    colors = ['lightpink', 'lightskyblue']

    # Plot pie chart
    with plot_lock:
        
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(f'Desk Availability Status ({current_year}/{current_month}/{current_day}) ')

        # Save image to BytesIO
        img = io.BytesIO()
        fig.savefig(img, format='png')
        plt.close('all')  # Close the figure to free memory
        img.seek(0)

    return img

def preferred_days_by_employees():
    employees_copy = employees.copy()
    
    # Calculate frequency of preferred days
    frequency_counts = employees_copy['prefDays'].value_counts().reset_index()
    frequency_counts.columns = ['prefDays', 'Frequency']
    
    
    max_value = frequency_counts['Frequency'].max()

    # Create bar plot
    with plot_lock:
        fig, ax = plt.subplots()  # Set figure size
        sns.set_style('darkgrid')
        sns.barplot(data=frequency_counts, x='prefDays', y='Frequency', ax=ax, palette='RdPu',hue='prefDays',legend=True)

        # Set title and labels
        ax.set_title('Employees Preference Day Distribution')
        ax.set_xlabel('Preference Days')
        ax.set_ylabel('Counts')
        ax.tick_params(axis='x', labelsize=8) 
        ax.set_ylim(0, max_value + 3)

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        fig.savefig(img, format='png')
        plt.close('all')  # Free memory
        img.seek(0)

    return img

def weekly_peak_office_usage():
    current_week = datetime.today().isocalendar()[1]
    current_year = datetime.today().year
    booking_copy = booking.copy()

    # Ensure 'date' column is in datetime format
    booking_copy['date'] = pd.to_datetime(booking_copy['date'])

    # Filter DataFrame for current week
    df_current_week = booking_copy[
        (booking_copy['date'].dt.isocalendar().week == current_week) &
        (booking_copy['date'].dt.year == current_year)
    ]

    # Group by day of the week
    weekly_bookings = df_current_week.groupby(df_current_week['date'].dt.day_name()).size().reset_index(name='total_bookings')

    # Sort by actual weekday order (Monday to Sunday)
    weekly_bookings['date'] = pd.Categorical(
        weekly_bookings['date'],
        categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        ordered=True
    )
    weekly_bookings = weekly_bookings.sort_values('date')
    # print(weekly_bookings)

    # Create Doughnut Chart
    with plot_lock:
        fig, ax = plt.subplots()
        ax.pie(
            weekly_bookings['total_bookings'],
            labels=weekly_bookings['date'],
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'edgecolor': 'white'},
            colors=sns.color_palette("coolwarm")
        )
        ax.set_title("Weekly Peak Office Usage")

        # Make it a doughnut chart
        centre_circle = plt.Circle((0, 0), 0.4, fc='white')
        fig.gca().add_artist(centre_circle)

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        fig.savefig(img, format='png')
        plt.close('all')  # Free memory
        img.seek(0)

    return img



# graph for employee



def personal_desk_booking_history(user_details):
    user_data = get_user_data_df(user_details)
    current_year = datetime.now().year
    
    df_current_user = user_data.copy()
    booking_copy = booking.copy()

    # filtering
    booking_copy['date'] = pd.to_datetime(booking_copy['date'])
    booking_copy.set_index('date', inplace=True)
    booking_copy.sort_index(inplace=True)
    current_employee_id = df_current_user['employeeID'].iloc[0]
    booking_copy = booking_copy.loc[(booking_copy.index.year == current_year) & (booking_copy['employeeID']==current_employee_id) & (booking_copy['deskID'].astype(str).str.startswith('D'))]
    frequency = booking_copy.resample('ME').size().reset_index(name='count')
    frequency.columns = ['date','count']
    frequency.set_index('date',inplace=True)

    with plot_lock:
        fig,ax = plt.subplots()
        sns.set_style('darkgrid')
        
        sns.lineplot(data=frequency,x=frequency.index,y='count', ax=ax,marker='o')
        ax.set_title(f'Personal Desk Booking History ({current_year})')
        ax.set_xlabel('Date')
        ax.set_ylabel('Counts')
        plt.xticks(rotation = 90)
        plt.tight_layout()

        img = io.BytesIO()
        fig.savefig(img, format='png')
        plt.close('all')
        img.seek(0)

    return img

def preferred_desk_usage_frequency(user_details):
    current_year = datetime.now().year
    user_data = get_user_data_df(user_details)

    df_current_user = user_data.copy()
    booking_copy = booking.copy()

    # filtering
    booking_copy['date'] = pd.to_datetime(booking_copy['date'])
    booking_copy.set_index('date', inplace=True)
    booking_copy.sort_index(inplace=True)
    current_employee_id = df_current_user['employeeID'].iloc[0]
    booking_copy = booking_copy.loc[(booking_copy.index.year == current_year) & (booking_copy['employeeID']==current_employee_id) & (booking_copy['deskID'].astype(str).str.startswith('D'))]

    booking_copy['frequency'] = booking_copy.groupby('deskID')['deskID'].transform(len)

    # plotting
    with plot_lock:
        fig,ax = plt.subplots()
        sns.set_style('darkgrid')
        sns.barplot(data=booking_copy,x='deskID',y='frequency',palette='mako',hue='deskID')
        ax.set_title(f'Your Desk Usage Frequency Distribution ({current_year})')
        ax.set_xlabel('Desk ID')
        ax.set_ylabel('Frequency')

        img = io.BytesIO()
        fig.savefig(img,format='png')
        plt.close('all')
        img.seek(0)
    return img

def average_monthly_attendance(user_details):
    current_year = datetime.now().year
    current_month = datetime.now().month

    user_data = get_user_data_df(user_details)

    df_current_user = user_data.copy()
    booking_copy = booking.copy()

    # filtering
    booking_copy['date'] = pd.to_datetime(booking_copy['date'])
    booking_copy.set_index('date', inplace=True) 
    booking_copy.sort_index(inplace=True)
    current_employee_id = df_current_user['employeeID'].iloc[0]
    
    booking_copy = booking_copy.loc[(booking_copy.index.year == current_year) & (booking_copy.index.month == current_month) & (booking_copy['employeeID']==current_employee_id)]
    total_days = booking_copy.index.days_in_month.max()
    in_office_days = booking_copy.shape[0]
    sizes = [total_days,in_office_days]
    labels = ['Work From Home','In-Office']
    colors = ['paleturquoise','skyblue']

    with plot_lock:
        fig,ax = plt.subplots()
        ax.pie(sizes,labels=labels,colors=colors,autopct='%1.1f%%')
        ax.axis('equal')
        ax.set_title(f'Average Monthly Attendance ({current_year}/{current_month})')

        img = io.BytesIO()
        fig.savefig(img,format='png')
        plt.close('all')
        img.seek(0)
    return img


def comparison_of_booking_patterns_with_peers(user_details):
    user_data = get_user_data_df(user_details)

    current_user_df = user_data.copy()
    df_employee = employees.copy()
    df_booking = booking.copy()

    # Get current user's department ID
    current_dept = current_user_df['departmentID'].iloc[0]

    colleagues = df_employee[df_employee['departmentID'] == current_dept]

    merged = pd.merge(colleagues, df_booking, on='employeeID', how='inner')

    merged['date'] = pd.to_datetime(merged['date'])
    merged['day_of_week'] = merged['date'].dt.day_name()

    grouped = merged.groupby(['employeeID', 'name', 'day_of_week']).size().reset_index(name='count')

    max_day = grouped.sort_values(['employeeID', 'count'], ascending=[True, False])\
                    .groupby('employeeID').head(1)\
                    .reset_index(drop=True)

    # Plotting using matplotlib
    with plot_lock:

        fig, ax = plt.subplots()

        # Create a bar chart: x = employee name, y = count of bookings on most frequent day
        bars = ax.bar(max_day['name'], max_day['count'], color='skyblue')

        # Set chart title and labels
        ax.set_title('Colleagues: Most Frequent Booking Day')
        ax.set_xlabel('Employee Name')
        ax.set_ylabel('Number of Bookings')

        # Annotate each bar with the day name
        for bar, day in zip(bars, max_day['day_of_week']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5, day,
                    ha='center', va='bottom', fontsize=10)
            ax.set_ylim(0, max(max_day['count']) + 5)

        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save or show the figure
        plt.show()

        import io
        img = io.BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight')
        plt.close('all')
        img.seek(0)

    return img










