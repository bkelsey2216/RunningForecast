from weather_report import WeatherReport

def main():

    nyc = WeatherReport("New York")
    times = nyc.getBestTimesToRun()
    print(f"Best times to run in {nyc.name} in the next {len(times)} days:")
    for day, time in times.items():
        print(f"{day}: {time[0]}, score: {time[1]:.2f}")


if __name__ == "__main__":
    main()
