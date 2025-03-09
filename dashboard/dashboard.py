import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import datetime
sns.set(style='dark')

# Kita membuat helper function
def create_daily_orders_df(df):
    daily_orders_df = df.resample('D', on='date').sum()
    daily_orders_df = daily_orders_df.reset_index()
    return daily_orders_df

def create_sum_monthly_user(df):
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    monthly_sum_user = df.groupby(['year', 'month'])[['casual_users', 'registered_users']].sum().reset_index()

    # Mengubah nilai numerik bulan menjadi deskripsi
    month_mapping = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    monthly_sum_user['month'] = monthly_sum_user['month'].map(month_mapping)
    return monthly_sum_user

def create_sum_seasonal_user(df):
    df['season'] = df['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
    seasonal_sum_user = df.groupby(['year', 'season'])[['casual_users', 'registered_users']].sum().reset_index()
    return seasonal_sum_user

def create_sum_hourly_user(df):
    df['hour'] = df['hour']
    hourly_sum_user = df.groupby(['hour'])[['casual_users', 'registered_users']].sum().reset_index()
    return hourly_sum_user

def create_sum_weekly_user(df):
    df['weekday'] = df['date'].dt.weekday
    df['weekday'] = df['weekday'].map({0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'})
    weekly_sum_user = df.groupby(['weekday'])[['casual_users', 'registered_users']].sum().reset_index()
    return weekly_sum_user

# Memuat data
main_data_df = pd.read_csv('./dashboard/main_data.csv')
datetime_columns = ['date']
main_data_df.sort_values(by=datetime_columns, inplace=True)
main_data_df.reset_index(inplace=True)

for col in datetime_columns:
    main_data_df[col] = pd.to_datetime(main_data_df[col])

# Memuat komponen filter
min_date = main_data_df['date'].min()
max_date = main_data_df['date'].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image('./dashboard/logo.png')

    # Mengambil start date dan end date
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value = min_date, 
        max_value = max_date,
        value = [min_date, max_date])

# Memfilter data berdasarkan tanggal
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)
filtered_data_df = main_data_df[(main_data_df['date'] >= start_date) & (main_data_df['date'] <= end_date)]

daily_orders_df = create_daily_orders_df(filtered_data_df)
monthly_user_df = create_sum_monthly_user(filtered_data_df)
seasonal_user_df = create_sum_seasonal_user(filtered_data_df)
hourly_user_df = create_sum_hourly_user(filtered_data_df)
weekly_user_df = create_sum_weekly_user(filtered_data_df)

# Melengkapi dashboard dengan visualisasi data
# Visualisasi pertanyaan 1
st.header('Bike Sharing Dashboard :sparkles:')
st.subheader('Daily Users Count')
 
col1, col2, col3 = st.columns(3)

with col1:
    total_casual = daily_orders_df.casual_users.sum()
    st.metric(label='Total Casual Users', value=f'{total_casual:,}')

with col2:
    total_registered = daily_orders_df.registered_users.sum()
    st.metric(label='Total Registered Users', value=f'{total_registered:,}')

with col3:
    total_users = daily_orders_df.total_rentals.sum()
    st.metric(label='Total Users', value=f'{total_users:,}')

# Visualisasi data pengguna kasual dan pengguna terdaftar
st.subheader('Daily Users Visualization')

fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=daily_orders_df, x='date', y='casual_users', label='Casual Users', ax=ax)
sns.lineplot(data=daily_orders_df, x='date', y='registered_users', label='Registered Users', ax=ax)
ax.set_title('Daily Users Count Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Number of Users')
ax.legend()
st.pyplot(fig)


# Visualisasi pertanyaan 2
st.subheader('Best Month for Each User Type')

# Visualisasi jumlah penyewaan pengguna kasual dan terdaftar per bulan
# Membuat dua grafik terpisah untuk pengguna kasual dan terdaftar
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

# Grafik untuk pengguna kasual
sns.lineplot(data=monthly_user_df[monthly_user_df['year'] == 2011], x='month', y='casual_users', marker='o', ax=ax1, linewidth=2.5, color='red', label='Casual Users 2011')
sns.lineplot(data=monthly_user_df[monthly_user_df['year'] == 2012], x='month', y='casual_users', marker='o', ax=ax1, linewidth=2.5, color='blue', label='Casual Users 2012')
ax1.set_title('Total Monthly Rentals for Casual Users')
ax1.set_xlabel('Month')
ax1.set_ylabel('Total Number of Rentals')
ax1.legend(loc='upper left', fontsize='large', title_fontsize='large')

# Menambahkan keterangan paling banyak dan paling sedikit untuk pengguna kasual
max_casual = monthly_user_df.groupby('year')['casual_users'].idxmax()
min_casual = monthly_user_df.groupby('year')['casual_users'].idxmin()
for idx in max_casual:
    ax1.text(monthly_user_df.loc[idx, 'month'], monthly_user_df.loc[idx, 'casual_users'], 'Max', color='green', weight='bold')
for idx in min_casual:
    ax1.text(monthly_user_df.loc[idx, 'month'], monthly_user_df.loc[idx, 'casual_users'], 'Min', color='black', weight='bold')

# Grafik untuk pengguna terdaftar
sns.lineplot(data=monthly_user_df[monthly_user_df['year'] == 2011], x='month', y='registered_users', marker='o', ax=ax2, linewidth=2.5, color='red', label='Registered Users 2011')
sns.lineplot(data=monthly_user_df[monthly_user_df['year'] == 2012], x='month', y='registered_users', marker='o', ax=ax2, linewidth=2.5, color='blue', label='Registered Users 2012')
ax2.set_title('Total Monthly Rentals for Registered Users')
ax2.set_xlabel('Month')
ax2.set_ylabel('Total Number of Rentals')
ax2.legend(loc='upper left', fontsize='large', title_fontsize='large')

# Menambahkan keterangan paling banyak dan paling sedikit untuk pengguna terdaftar
max_registered = monthly_user_df.groupby('year')['registered_users'].idxmax()
min_registered = monthly_user_df.groupby('year')['registered_users'].idxmin()
for idx in max_registered:
    ax2.text(monthly_user_df.loc[idx, 'month'], monthly_user_df.loc[idx, 'registered_users'], 'Max', color='green', weight='bold')
for idx in min_registered:
    ax2.text(monthly_user_df.loc[idx, 'month'], monthly_user_df.loc[idx, 'registered_users'], 'Min', color='black', weight='bold')

st.pyplot(fig)


# Visualisasi pertanyaan 3
st.subheader('Seasonal Trend of Bike Rentals')

# Visualisasi jumlah penyewaan pengguna kasual dan pengguna terdaftar per musim
# Membuat dua grafik terpisah untuk pengguna kasual dan terdaftar
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

# Grafik untuk pengguna kasual
sns.barplot(data=seasonal_user_df.sort_values(by='casual_users', ascending=False), x='season', y='casual_users', hue='year', ax=ax1)
ax1.set_title('Total Seasonal Rentals for Casual Users')
ax1.set_xlabel('Season')
ax1.set_ylabel('Total Number of Rentals')
ax1.legend(title='Year')

# Grafik untuk pengguna terdaftar
sns.barplot(data=seasonal_user_df.sort_values(by='registered_users', ascending=False), x='season', y='registered_users', hue='year', ax=ax2)
ax2.set_title('Total Seasonal Rentals for Registered Users')
ax2.set_xlabel('Season')
ax2.set_ylabel('Total Number of Rentals')
ax2.legend(title='Year')

st.pyplot(fig)


# Visualisasi pertanyaan 4
st.subheader('Hourly Trend of Bike Rentals')

hourly_user_rentals_avg = hourly_user_df.groupby('hour')[['casual_users', 'registered_users']].mean().reset_index()

plt.figure(figsize=(14, 8))  # ukuran figure
hourly_user_rentals_avg_melted = hourly_user_rentals_avg.melt(id_vars='hour', value_vars=['casual_users', 'registered_users'], var_name='User Type', value_name='Average Rentals')
sns.lineplot(x='hour', y='Average Rentals', hue='User Type', data=hourly_user_rentals_avg_melted)  # membuat line plot
plt.title('Average Bike Rentals by Hour and User Type')  # judul plot
plt.xlabel('Hour of the Day')  # label sumbu x
plt.ylabel('Average Bike Rentals')  # label sumbu y

# Menambahkan keterangan untuk jam paling banyak dan paling sedikit di masing-masing pengguna
max_casual = hourly_user_rentals_avg.loc[hourly_user_rentals_avg['casual_users'].idxmax()]
min_casual = hourly_user_rentals_avg.loc[hourly_user_rentals_avg['casual_users'].idxmin()]
max_registered = hourly_user_rentals_avg.loc[hourly_user_rentals_avg['registered_users'].idxmax()]
min_registered = hourly_user_rentals_avg.loc[hourly_user_rentals_avg['registered_users'].idxmin()]

plt.annotate(f'Max Casual: {max_casual["hour"]}h', xy=(max_casual['hour'], max_casual['casual_users']), xytext=(max_casual['hour']+1, max_casual['casual_users']+10),
             arrowprops=dict(facecolor='black', edgecolor='black', arrowstyle='->'))
plt.annotate(f'Min Casual: {min_casual["hour"]}h', xy=(min_casual['hour'], min_casual['casual_users']), xytext=(min_casual['hour']+1, min_casual['casual_users']-10),
             arrowprops=dict(facecolor='black', edgecolor='black', arrowstyle='->'))
plt.annotate(f'Max Registered: {max_registered["hour"]}h', xy=(max_registered['hour'], max_registered['registered_users']), xytext=(max_registered['hour']+1, max_registered['registered_users']+10),
             arrowprops=dict(facecolor='black', edgecolor='black', arrowstyle='->'))
plt.annotate(f'Min Registered: {min_registered["hour"]}h', xy=(min_registered['hour'], min_registered['registered_users']), xytext=(min_registered['hour']-3, min_registered['registered_users']+10),
             arrowprops=dict(facecolor='black', edgecolor='black', arrowstyle='->'))

plt.xticks(ticks=range(0, 24, 1))  # mengatur ticks pada sumbu x menjadi kelipatan 1
plt.tight_layout()  # layout yang pas
st.pyplot(plt)  # menampilkan plot di Streamlit


# Visualisasi pertanyaan 5
st.subheader('Weekly Trend of Bike Rentals')

weekday_user_rentals_avg = weekly_user_df.groupby('weekday')[['casual_users', 'registered_users']].mean().reset_index()

# Visualisasi data secara horizontal untuk pengguna kasual
plt.figure(figsize=(14, 8))  # ukuran figure
sns.barplot(y='weekday', x='casual_users', data=weekday_user_rentals_avg.sort_values(by='casual_users', ascending=False), color='blue')  # membuat bar plot horizontal untuk pengguna kasual
plt.title('Average Bike Rentals by Day of the Week for Casual Users')  # judul plot
plt.xlabel('Average Bike Rentals')  # label sumbu x
plt.ylabel('Day of the Week')  # label sumbu y
plt.tight_layout()  # layout yang pas
st.pyplot(plt)  # menampilkan plot di Streamlit

# Visualisasi data secara horizontal untuk pengguna terdaftar
plt.figure(figsize=(14, 8))  # ukuran figure
sns.barplot(y='weekday', x='registered_users', data=weekday_user_rentals_avg.sort_values(by='registered_users', ascending=False), color='orange')  # membuat bar plot horizontal untuk pengguna terdaftar
plt.title('Average Bike Rentals by Day of the Week for Registered Users')  # judul plot
plt.xlabel('Average Bike Rentals')  # label sumbu x
plt.ylabel('Day of the Week')  # label sumbu y
plt.tight_layout()  # layout yang pas
st.pyplot(plt)  # menampilkan plot di Streamlit

current_year = datetime.datetime.now().year
st.caption(f'Copyright (c) Athallah Anargya Mahardika {current_year}')