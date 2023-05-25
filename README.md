# Walk-in Clinic Finder (Commandline)

#### Video Demo: [Demo video on loom](https://www.loom.com/share/becb22aeee9446b899d755e5b5c0a272) - https://www.loom.com/share/becb22aeee9446b899d755e5b5c0a272

#### Description:

## Opportunity

When I needed to find a doctor over the weekend, the provincial health helpline agent pointed me to a website that listed all the clinics in my area. However, it was not easy to determine which one I should go to as it did not filter or sort it by how far it is from my current location and did not surface the working hours of the clinic. So, I gathered this as an opportunity to solve with my new coding skills.

## Solution

The solution I’ve built right now is a command-line interface that scrapes the data from the [Toronto Central Healthline website](https://www.torontocentralhealthline.ca/listServices.aspx?id=10072), asks the user for their address and then uses the Google Maps API to determine the distance, driving time, transit time and shows the user the closest three clinics and the time of closing for those clinics. To do this, I have used BeautifulSoup4 library for web scraping, Google Maps API for calculating the distances and transit time, TQDM library to show progress bars when fetching web requests from API and web scraping, and the Decouple library to store my API key in the .env file and keep it anonymous.

![Screenshot of Walk-in Clinic Finder showing three nearest clinics to the address provided.](/images/screenshot.png "Walk-in Clinic Finder Results")

## Design Decisions

Right now, the program is really slow to scrape data off multiple pages (95 clinics for Toronto Downtown region) and then use Google Maps Distance Metric API (which loops over all clinics again, one-by-one). However, this was my first time building something complex like this and I wanted to keep this simple. The data is scraped every single time the program is run; however, in future upgrades, I would like to store the data in a database or file and only scrape once every week.

The data shown at the end surfaces the name of the clinic, its address and phone number in the first section and then the distance from the address provided, time it will take to reach the clinic if you drive there vs taking transit, and the time the clinic is open until. It also shows the link to a webpage with other detailed information like accessibility, etc. This info is shown for the three closest clinics found.

## Optimisations and Improvements

One improvement I plan to implement is to send all 95 clinic addresses at the same time when using the Distance Matrix API to shorten the response time. Additionally, I plan to store the scraped data in a database or file and only refresh it if the data is stale (i.e., scraped more than a week ago). This optimization will significantly reduce the response time when the clinic data is recent.

## Installation

1. Clone the repository: `git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY`
2. Install the required libraries: `pip install -r requirements.txt`
3. Set up your Google Maps API key: create a `.env` file in the root directory of the project and add `GOOGLE_MAPS_API_KEY=your_api_key_here`
4. Run the program: `python project.py`

## Usage

To use the program, run the `project.py` file and follow the prompts to enter your address and see the closest clinics.

## Project Structure

The project is structured as follows:

- `project.py`: the main file that runs the program
- `requirements.txt`: the file that contains the required libraries and their versions
- `test_project.py` : the file that contains pytest functions for unit tests

## Technologies Used

The following technologies were used in this project:

- Python 3
- BeautifulSoup4
- Google Maps API
- TQDM
