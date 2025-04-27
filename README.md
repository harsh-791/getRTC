# getRTC

A comprehensive system for tracking property records from Karnataka, India.

## Demo

▶️ [Watch the Demo Video](https://drive.google.com/file/d/1yh5spXPfPgUSnUuVaQ8H921fpW-WMB4B/view?usp=drive_link)



## Project Overview

getRTC is an innovative solution designed to modernize the way property records are accessed and managed in Karnataka. The system bridges the gap between traditional paper-based records and digital accessibility by:

- Automating the extraction of property details from RTC (Record of Rights, Tenancy and Crops) documents using advanced image processing
- Providing instant access to historical property records spanning multiple years
- Enabling easy comparison of property details across different time periods
- Creating a digital archive of property documents for future reference

Built with a robust Django backend and a modern React frontend, getRTC offers:

- Seamless document upload and processing
- Intelligent data extraction from scanned documents
- Interactive visualization of property history
- Secure storage and retrieval of property records
- User-friendly interface for both technical and non-technical users

The system is particularly valuable for:

- Property owners tracking their land records
- Real estate professionals verifying property details
- Government officials managing land records
- Legal professionals handling property cases
- Researchers studying land ownership patterns

The system consists of a Django backend with image processing capabilities and a React frontend that provides an intuitive user interface.

## Table of Contents

- [Getting Started](#getting-started)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Technical Approach](#technical-approach)
- [Challenges and Solutions](#challenges-and-solutions)

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/yourusername/getRTC.git
cd getRTC
```

## Setup Instructions

### Backend Setup (rtc-scraper)

1. Create and activate a virtual environment:

```bash
cd rtc-scraper
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your database and API credentials
```

4. Set up PostgreSQL database:

```bash
# Create database and user as per .env configuration
sudo -u postgres psql
postgres=# CREATE DATABASE rtc_documents;
postgres=# CREATE USER your_db_user WITH PASSWORD 'your_db_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE rtc_documents TO your_db_user;
```

5. Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

### Frontend Setup (project)

1. Install Node.js dependencies:

```bash
cd project
npm install
```

2. Start the development server:

```bash
npm run dev
```

The application will be available at:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## API Documentation

The backend provides the following REST API endpoints:

### Process Image API

- **Endpoint**: `/api/process-image/`
- **Method**: `POST`
- **Description**: Uploads and processes an image to extract property details
- **Request Format**: Multipart form data with an image field
- **Response Format**:

```json
{
  "property_id": 123,
  "property_details": {
    "Survey Number": "22",
    "Surnoc": "*",
    "Hissa": "1",
    "Village": "Devenahalli",
    "Hobli": "Kasaba",
    "Taluk": "Devanahalli",
    "District": "Bangalore Rural",
    "Owner Name": "John Doe",
    "Owner Details": "..."
  }
}
```

### Get Property Details API

- **Endpoint**: `/api/property/{property_id}/`
- **Method**: `GET`
- **Description**: Retrieves property details and associated images
- **Response Format**:

```json
{
  "property_details": {
    "id": 123,
    "survey_number": "22",
    "surnoc": "*",
    "hissa": "1",
    "village": "Devenahalli",
    "hobli": "Kasaba",
    "taluk": "Devanahalli",
    "district": "Bangalore Rural",
    "owner_name": "John Doe",
    "owner_details": "...",
    "created_at": "2025-04-22T12:00:00Z",
    "updated_at": "2025-04-22T12:00:00Z"
  },
  "images": [
    {
      "id": 1,
      "property_id": 123,
      "image_type": "RTC Document",
      "year_period": "2019-20",
      "description": "...",
      "created_at": "2025-04-22T12:05:00Z"
    }
  ]
}
```

## Technical Approach

TitleWise is a system that helps digitize and manage property records from Karnataka. Here's how it works:

### 1. Image Processing & Data Extraction

When you upload a property document image:

- The system uses AI to read the text in the image
- It extracts important details like:
  - Survey number, Surnoc, and Hissa
  - Village, Hobli, Taluk, and District
  - Owner information
- The system can read both English and Kannada text
- It checks and fixes any errors in the extracted data

### 2. Getting Historical Records

After getting the property details, the system:

- Automatically visits the Karnataka land records website
- Fills in the property details in the search form
- Finds and matches the correct location options
- Downloads historical records for different years
- Saves screenshots of the documents
- Stores all the information in the database

### 3. User Interface

The website is built with React and provides:

- Easy image upload
- Clear display of property details
- Gallery of historical documents
- Ability to zoom and download documents
- Real-time updates as new records are found

### 4. Backend System

The backend uses Django and PostgreSQL to:

- Handle image uploads and processing
- Store property and document information
- Manage the web scraping process
- Provide secure API endpoints

### 5. How Data Flows

1. User uploads an image
2. System extracts property details
3. System searches for historical records
4. Results are shown to the user
5. New records are added as they're found

### 6. Security Features

- Secure storage of sensitive information
- Protection against unauthorized access
- Safe handling of user data
- Regular security updates

## Challenges and Solutions

### Challenge 1: Dynamic Form Handling

**Problem**: Complex cascading dropdown menus with varying options and no exact text matches.

**Solution**:

- Implemented sophisticated dropdown handling system
- Multi-level fuzzy matching:
  - Exact match (case insensitive)
  - Simplified text match
  - Contains match
  - Word-by-word matching

### Challenge 2: Historical Period and Year Selection

**Problem**: Inconsistent and unpredictable period/year organization.

**Solution**:

- Dynamic extraction of available options
- Comprehensive mapping of period values to years
- Smart matching algorithm for target years
- Real-time adaptation to website changes

### Challenge 3: Multilingual Document Processing

**Problem**: Mixed English and Kannada text with inconsistent formatting.

**Solution**:

- Leveraged OCR with language detection
- Custom post-processing pipeline
- Validation rules for extracted data
- Error correction mechanisms

### Challenge 4: Asynchronous Processing

**Problem**: Long processing times for historical records.

**Solution**:

- Immediate response for initial processing
- Background processing for historical records
- Frontend polling for updates
- Progressive loading of results
