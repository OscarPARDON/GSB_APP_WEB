from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.hashers import check_password

from DjangoProject1.asgi import application
from .models import Publication
from candidate.models import Application
from .forms import ApplicationForm
from datetime import datetime
##############################################################################################################

# This test the application view
class ApplicationTest(TestCase):

    def setUp(self): # Set up the test environnement
        self.client = Client() # Create the test client
        self.job_post = Publication.objects.create(id=1,title="TEST",description="Test", created_by_id=1) # Create a test publication for the test applications
        self.valid_url = reverse('application') + "?postID=1" # Application URL to send the test form

    def test_postID_error(self): # Test if the view has the right redirection when an invalid post ID is sent
        response = self.client.get(reverse('application')) # Get the HTTP status when no post id is sent
        self.assertEqual(response.status_code, 302) # Verify that the HTTP status is redirection (302)
        self.assertRedirects(response, '/') # Verify that the view redirect to the main page as expected

    def test_valid_application(self): # Test the view when a valid application is sent

        cv_content = b'some cv content'  # Create fake files for the test
        cover_letter_content = b'some cover letter content'  # Create fake files for the test

        cv_file = SimpleUploadedFile("cv.pdf", cv_content, content_type="application/pdf") # Upload the files
        cover_letter_file = SimpleUploadedFile("coverletter.pdf", cover_letter_content, content_type="application/pdf") # Upload the files

        data = {
            "firstname": "Jean",
            "name": "DUPONT",
            "email": "jean.dupont@example.com",
            "phone": "0601020304",
            "password": "Caracas5360?",
            "confirm": "Caracas5360?",
            "cv": cv_file,
            "cover_letter": cover_letter_file
        } # Create a test valid form

        response = self.client.post(self.valid_url, data) # Send form in POST to the view

        # Vérifications
        self.assertEqual(Application.objects.all().count(), 1) # Check that the application was successfully created
        application = Application.objects.first() # Get the application
        self.assertEqual(application.candidate_firstname, 'Jean') # Check that the firstname was successfully registered
        self.assertEqual(application.candidate_lastname, 'DUPONT') # Check that the lastname was successfully registered
        self.assertEqual(application.candidate_mail, 'jean.dupont@example.com') # Check that the email was successfully registered
        self.assertTrue(
            check_password('Caracas5360?', application.candidate_password))  # Check that the password was successfully hashed and registered
        self.assertEqual(response.status_code, 302) # Check that HTTP status is redirection (302) as expected

    def test_duplicate_application(self): # This test the view's reaction when a duplicata is created
        Application.objects.create( # Create an application
            application_number="20240301001",
            candidate_firstname="Jean",
            candidate_lastname="DUPONT",
            candidate_mail="other.mail@example.com",
            candidate_phone="0601020304",
            candidate_password="<PASSWORD>",
            job_publication=self.job_post,
            status=1,
        )

        cv_content = b'some cv content' # Create fake files for the test
        cover_letter_content = b'some cover letter content' # Create fake files for the test

        cv_file = SimpleUploadedFile("cv.pdf", cv_content, content_type="application/pdf") # Upload the file
        cover_letter_file = SimpleUploadedFile("coverletter.pdf", cover_letter_content, content_type="application/pdf") # Upload the file

        # Create a valid form with the same lastname and firstname as the already created one
        data = {
            "firstname": "Jean",
            "name": "DUPONT",
            "email": "jean.dupont@example.com",
            "phone": "0601020304",
            "password": "Caracas5360?",
            "confirm": "Caracas5360?",
            "cv": cv_file,
            "cover_letter": cover_letter_file
        }

        response = self.client.post(self.valid_url, data) # Send the form in POST & get the HTTP status
        self.assertEqual(Application.objects.filter(candidate_lastname="DUPONT", candidate_firstname="Jean").count(), 1) # Check if the application was registered (it should not)
        self.assertRedirects(response, '/?error=Vous avez déja candidaté pour cette offre') # Check if the view sent a duplicata error

    def test_duplicate_email_application(self): # This test the view's reaction to an application with an email duplicata
        Application.objects.create( # Create an application for the test
            application_number="20240301001",
            candidate_firstname="Other",
            candidate_lastname="NAME",
            candidate_mail="jean.dupont@example.com",
            candidate_phone="0601020304",
            candidate_password="<PASSWORD>",
            job_publication=self.job_post,
            status=1,
        )

        cv_content = b'some cv content' # Create a fake file for the test
        cover_letter_content = b'some cover letter content' # Create a fake file for the test

        cv_file = SimpleUploadedFile("cv.pdf", cv_content, content_type="application/pdf") # Upload the file
        cover_letter_file = SimpleUploadedFile("coverletter.pdf", cover_letter_content, content_type="application/pdf") # Upload the file

        data = {
            "firstname": "Jean",
            "name": "DUPONT",
            "email": "jean.dupont@example.com",
            "phone": "0601020304",
            "password": "Caracas5360?",
            "confirm": "Caracas5360?",
            "cv": cv_file,
            "cover_letter": cover_letter_file
        } # Create a valid application form with the same email as the already created one

        response = self.client.post(self.valid_url, data) # Send the form in POST & get the HTTP status
        self.assertEqual(Application.objects.all().count(), 1) # Verify that the application was not created
        self.assertRedirects(response, '/?error=Vous avez déja candidaté pour cette offre') # Check that the view returns a duplicata error
