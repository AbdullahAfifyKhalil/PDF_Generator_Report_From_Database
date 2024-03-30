# PDF_Generator_Report_From_Database

This project is a Python-based application designed to fetch incident data from a PostgreSQL database, dynamically generate an HTML report with the fetched data, and finally convert that HTML report into a PDF file. The report includes detailed information about incidents, such as incident ID, type, submission date, reporter's information, location (with a link to Google Maps and a static map image), and more.

## Features

- Fetch incident data from a PostgreSQL database using psycopg2.
- Dynamic report generation with Jinja2 based on incident data.
- HTML report template customization with CSS.
- PDF generation from HTML content using WeasyPrint.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6+
- PostgreSQL database with the necessary schema setup

- All Python dependencies installed from the requirements:
  -> psycopg2==2.9.3
  -> Jinja2==3.0.3
  -> WeasyPrint==55.0


## Installation

1. Clone the repository to your local machine.
2. Install the required Python packages.
